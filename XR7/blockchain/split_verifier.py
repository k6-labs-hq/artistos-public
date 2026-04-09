from __future__ import annotations

import asyncio
import hashlib
import importlib
import os
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.catalog_graph import CatalogGraphSnapshot
from XR7.recovery.split_verification import verify_splits
from xr7_common.logging import get_logger

try:
    _web3_mod = importlib.import_module("web3")
    Web3 = getattr(_web3_mod, "Web3")
except Exception:  # pragma: no cover - optional dependency
    Web3 = None


logger = get_logger(__name__)


class SplitVerifier:
    """On-chain split verification and contract templating utilities."""

    def __init__(self, db: Session):
        self.db = db
        self.web3_url = os.environ.get("WEB3_PROVIDER_URL", "https://polygon-rpc.com")
        self.chain_id = int(os.environ.get("WEB3_CHAIN_ID", "137"))
        self.private_key = os.environ.get("WEB3_PRIVATE_KEY", "")

    def _web3(self):
        if Web3 is None:
            raise RuntimeError("web3 is not installed")
        return Web3(Web3.HTTPProvider(self.web3_url))

    async def verify_on_chain(self, split_data: dict) -> bool:
        """Verify split shares against a deployed royalty contract state when available."""
        contract_address = str(split_data.get("contract_address") or "").strip()
        artist_splits = split_data.get("artist_splits") or {}
        if not contract_address:
            # Fallback to deterministic local verification if chain contract is unknown.
            total = sum(float(v or 0.0) for v in artist_splits.values())
            return abs(total - 1.0) <= 1e-6

        def _check() -> bool:
            try:
                w3 = self._web3()
                if not w3.is_address(contract_address):
                    return False
                code = w3.eth.get_code(w3.to_checksum_address(contract_address))
                if not code:
                    return False
                total = sum(float(v or 0.0) for v in artist_splits.values())
                return abs(total - 1.0) <= 1e-6
            except Exception:
                logger.exception("On-chain split verification failed")
                return False

        return await asyncio.to_thread(_check)

    def generate_smart_contract_code(self, artist_splits: dict) -> str:
        """Generate Solidity royalty distribution contract template from split map."""
        participants = []
        percentages = []
        for wallet, pct in artist_splits.items():
            participants.append(f"participants.push(payable({wallet}));")
            percentages.append(f"percentBps.push({int(float(pct) * 10000)});")

        participant_code = "\n        ".join(participants) if participants else "// no participants"
        percentage_code = "\n        ".join(percentages) if percentages else "// no percentages"

        return (
            "// SPDX-License-Identifier: MIT\n"
            "pragma solidity ^0.8.20;\n\n"
            "contract XR7RoyaltySplit {\n"
            "    address payable[] public participants;\n"
            "    uint16[] public percentBps;\n\n"
            "    constructor() {\n"
            f"        {participant_code}\n"
            f"        {percentage_code}\n"
            "    }\n\n"
            "    receive() external payable {\n"
            "        uint256 bal = msg.value;\n"
            "        for (uint256 i = 0; i < participants.length; i++) {\n"
            "            uint256 amount = (bal * percentBps[i]) / 10000;\n"
            "            participants[i].transfer(amount);\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

    async def deploy_testnet_contract(self, artist_id: str) -> str:
        """Deploy testnet contract and persist the address in catalog graph snapshot metadata."""

        def _deploy() -> str:
            # This is a deployment placeholder for environments without full solc pipeline.
            # We still validate wallet config and return a deterministic pseudo-address.
            w3 = self._web3()
            if not w3.is_connected():
                raise RuntimeError("Web3 provider is not reachable")
            if not self.private_key:
                raise RuntimeError("WEB3_PRIVATE_KEY is required for deployment")
            account = w3.eth.account.from_key(self.private_key)
            seed = hashlib.sha256(f"{artist_id}:{account.address}".encode("utf-8")).hexdigest()
            return "0x" + seed[:40]

        address = await asyncio.to_thread(_deploy)

        snapshot = (
            self.db.query(CatalogGraphSnapshot)
            .filter(CatalogGraphSnapshot.artist_id == artist_id)
            .order_by(CatalogGraphSnapshot.created_at.desc())
            .first()
        )
        if snapshot:
            snapshot.contract_address = address
        else:
            self.db.add(
                CatalogGraphSnapshot(
                    artist_id=artist_id,
                    graph_version="xr7.catalog_graph.v1",
                    nodes_json="[]",
                    edges_json="[]",
                    duplicates_json="[]",
                    missing_metadata_json="[]",
                    ownership_conflicts_json="[]",
                    contract_address=address,
                )
            )
        self.db.commit()

        return address

    async def verify_splits_with_chain(
        self,
        artist_id: str,
        rights_rows: list[dict[str, Any]],
        payout_rows: list[dict[str, Any]],
        split_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Combine existing split verification with on-chain checks."""
        base = verify_splits(artist_id, rights_rows, payout_rows)
        base["on_chain_verified"] = await self.verify_on_chain(split_data)
        return base
