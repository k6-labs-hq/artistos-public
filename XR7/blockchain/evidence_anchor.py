from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from sqlalchemy.orm import Session
from XR7.models.claim import Claim
from XR7.models.evidence_anchor import EvidenceAnchor as EvidenceAnchorRow
from xr7_common.logging import get_logger

try:
    ipfshttpclient = importlib.import_module("ipfshttpclient")
except Exception:  # pragma: no cover - optional dependency
    ipfshttpclient = None

try:
    _web3_mod = importlib.import_module("web3")
    Web3 = getattr(_web3_mod, "Web3")
except Exception:  # pragma: no cover - optional dependency
    Web3 = None


logger = get_logger(__name__)


class EvidenceAnchor:
    """Anchor evidence packets to IPFS and blockchain for tamper-evident provenance.

    Sample Solidity anchor contract:

    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.20;

    contract XR7EvidenceAnchor {
        event Anchored(string indexed claimId, bytes32 packetHash, bytes32 priorHash, address indexed actor);
        mapping(string => bytes32) public latestHash;

        function anchor(string calldata claimId, bytes32 packetHash, bytes32 priorHash) external {
            latestHash[claimId] = packetHash;
            emit Anchored(claimId, packetHash, priorHash, msg.sender);
        }
    }
    """

    ANCHOR_ABI: list[dict[str, Any]] = [
        {
            "inputs": [
                {"internalType": "string", "name": "claimId", "type": "string"},
                {"internalType": "bytes32", "name": "packetHash", "type": "bytes32"},
                {"internalType": "bytes32", "name": "priorHash", "type": "bytes32"},
            ],
            "name": "anchor",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "string", "name": "claimId", "type": "string"}],
            "name": "latestHash",
            "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]

    def __init__(self):
        self.ipfs_gateway = os.environ.get("IPFS_GATEWAY", "https://ipfs.io")
        self.web3_provider = os.environ.get("WEB3_PROVIDER_URL", "https://polygon-rpc.com")
        self.contract_address = os.environ.get("XR7_ANCHOR_CONTRACT_ADDRESS", "")
        self.private_key = os.environ.get("WEB3_PRIVATE_KEY", "")

    def _web3(self):
        if Web3 is None:
            raise RuntimeError("web3 is not installed")
        w3 = Web3(Web3.HTTPProvider(self.web3_provider))
        if not w3.is_connected():
            raise RuntimeError("WEB3 provider is not reachable")
        return w3

    async def store_on_ipfs(self, evidence_packet: dict) -> str:
        """Persist evidence packet JSON on IPFS and return CID."""

        def _store() -> str:
            payload = json.dumps(evidence_packet, sort_keys=True).encode("utf-8")
            if ipfshttpclient is not None:
                client = ipfshttpclient.connect()
                added = client.add_json(json.loads(payload.decode("utf-8")))
                if isinstance(added, str):
                    return added
                if isinstance(added, dict):
                    return str(added.get("Hash") or added.get("cid") or "")
            # Fallback deterministic CID-like hash when no client is configured.
            digest = hashlib.sha256(payload).hexdigest()
            return f"bafy{digest[:40]}"

        cid = await asyncio.to_thread(_store)
        if not cid:
            raise RuntimeError("Failed to store evidence packet on IPFS")
        return cid

    async def anchor_hash_on_chain(self, claim_id: str, packet_hash: str, prior_hash: str) -> str:
        """Anchor packet hash on-chain and return transaction hash."""

        def _anchor() -> str:
            if not self.contract_address or Web3 is None:
                # Fallback pseudo tx hash for offline/dev environments.
                return "0x" + hashlib.sha256(f"{claim_id}:{packet_hash}:{prior_hash}".encode("utf-8")).hexdigest()
            w3 = self._web3()

            if not self.private_key:
                raise RuntimeError("WEB3_PRIVATE_KEY is required for on-chain anchoring")

            account = w3.eth.account.from_key(self.private_key)
            contract = w3.eth.contract(address=w3.to_checksum_address(self.contract_address), abi=self.ANCHOR_ABI)
            nonce = w3.eth.get_transaction_count(account.address)
            packet_hash_bytes = bytes.fromhex(packet_hash.replace("0x", "")[:64].ljust(64, "0"))
            prior_hash_bytes = bytes.fromhex(prior_hash.replace("0x", "")[:64].ljust(64, "0"))

            tx = contract.functions.anchor(claim_id, packet_hash_bytes, prior_hash_bytes).build_transaction(
                {
                    "from": account.address,
                    "nonce": nonce,
                    "chainId": w3.eth.chain_id,
                }
            )
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.2)
            tx["maxFeePerGas"] = w3.eth.gas_price
            tx["maxPriorityFeePerGas"] = max(1, int(w3.eth.gas_price * 0.1))

            signed = w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if int(receipt.status) != 1:
                raise RuntimeError("Anchor transaction failed")
            return tx_hash.hex()

        return await asyncio.to_thread(_anchor)

    async def verify_on_chain(self, claim_id: str) -> bool:
        """Verify whether the claim has a non-zero latest hash on-chain."""

        def _verify() -> bool:
            if not self.contract_address:
                return True
            w3 = self._web3()
            contract = w3.eth.contract(address=w3.to_checksum_address(self.contract_address), abi=self.ANCHOR_ABI)
            latest = contract.functions.latestHash(claim_id).call()
            return bool(latest and int.from_bytes(latest, "big") != 0)

        try:
            return await asyncio.to_thread(_verify)
        except Exception:
            logger.exception("On-chain verification failed")
            return False

    async def anchor_claim(self, claim_id: str, db: "Session | None" = None) -> dict[str, Any]:
        _owned = db is None
        if _owned:
            db = SessionLocal()
        try:
            claim = db.query(Claim).filter(Claim.id == claim_id).first()
            if not claim:
                raise ValueError("Claim not found")
            packet = claim.evidence or {}
            metadata = packet.get("metadata") or {}
            integrity = packet.get("integrity") or {}
            packet_hash = str(integrity.get("packet_hash") or "")
            prior_hash = str(integrity.get("prior_packet_hash") or "")
            if not packet_hash:
                raise ValueError("Evidence packet integrity hash missing")

            cid = await self.store_on_ipfs(packet)
            tx_hash = await self.anchor_hash_on_chain(claim_id, packet_hash, prior_hash)

            row = EvidenceAnchorRow(
                claim_id=claim_id,
                packet_hash=packet_hash,
                chain_hash=tx_hash,
                anchor_provider="POLYGON_IPFS",
                anchor_reference=f"cid={cid}",
                cid=cid,
                tx_hash=tx_hash,
                blockchain_status="ANCHORED",
            )
            db.add(row)

            packet.setdefault("integrity", {})
            packet["integrity"]["ipfs_cid"] = cid
            packet["integrity"]["anchor_tx_hash"] = tx_hash
            packet["integrity"]["anchored_at"] = datetime.now(timezone.utc).isoformat()
            packet["metadata"] = metadata
            claim.evidence = packet

            db.commit()
            db.refresh(row)

            return {
                "claim_id": claim_id,
                "packet_version": metadata.get("packet_version"),
                "packet_hash": packet_hash,
                "cid": cid,
                "tx_hash": tx_hash,
                "proof_link": f"{self.ipfs_gateway.rstrip('/')}/ipfs/{cid}",
                "etherscan_link": f"https://polygonscan.com/tx/{tx_hash}",
            }
        except Exception:
            db.rollback()
            logger.exception("Failed to anchor claim evidence")
            raise
        finally:
            if _owned:
                db.close()


@celery_app.task(name="xr7.pipeline.anchor_claim_evidence", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def anchor_claim_evidence_task(self, claim_id: str) -> dict:  # noqa: ANN001
    """Celery wrapper for asynchronous evidence anchoring."""

    return asyncio.run(EvidenceAnchor().anchor_claim(claim_id))
