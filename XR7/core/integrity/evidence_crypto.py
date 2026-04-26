"""
Pure evidence-packet cryptography helpers.

All functions here are stateless and free of DB or service dependencies, making
them safe to call from any context — unit tests, LangGraph nodes, n8n HTTP
steps, or CLI tools — without needing a SQLAlchemy session.

Signing modes
-------------
- ``hmac``  (default): HMAC-SHA256 using ``XR7_EVIDENCE_HMAC_SECRET`` env var.
- ``rsa``:  RSA-SHA256 using ``XR7_EVIDENCE_PRIVATE_KEY_PEM`` /
  ``XR7_EVIDENCE_PUBLIC_KEY_PEM`` env vars.  Falls back to HMAC when the key
  is not configured.
"""

from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Low-level primitives
# ---------------------------------------------------------------------------


def canonicalize(data: dict[str, Any]) -> bytes:
    """Stable JSON serialisation used as the input to all hash operations."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def compute_packet_hash(packet_data: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON representation of *packet_data*."""
    return sha256_hex(canonicalize(packet_data))


def compute_chain_hash(prior_packet_hash: str | None, packet_hash: str) -> str:
    """Chain this packet to its predecessor (GENESIS sentinel when first)."""
    chain_input = f"{prior_packet_hash or 'GENESIS'}:{packet_hash}".encode("utf-8")
    return sha256_hex(chain_input)


# ---------------------------------------------------------------------------
# Signing / verification
# ---------------------------------------------------------------------------


def signing_mode() -> str:
    return os.environ.get("XR7_EVIDENCE_SIGNING_MODE", "hmac").strip().lower()


def hmac_sign(chain_hash: str) -> tuple[str, str]:
    """Return (signature_hex, key_source_label) using HMAC-SHA256."""
    secret = os.environ.get("XR7_EVIDENCE_HMAC_SECRET", "xr7-dev-evidence-secret")
    sig = _hmac.new(secret.encode("utf-8"), chain_hash.encode("utf-8"), hashlib.sha256).hexdigest()
    key_source = (
        "env:XR7_EVIDENCE_HMAC_SECRET"
        if os.environ.get("XR7_EVIDENCE_HMAC_SECRET")
        else "default-dev-secret"
    )
    return sig, key_source


def hmac_verify(chain_hash: str, signature: str) -> bool:
    """Constant-time HMAC-SHA256 verification."""
    expected, _ = hmac_sign(chain_hash)
    return _hmac.compare_digest(expected, signature)


def openssl_rsa_sign(message: str, private_key_pem: str) -> str:
    """Sign message with RSA-SHA256 using cryptography library or openssl subprocess.

    Raises ``ValueError`` if the PEM is not an RSA key — PKCS#1 v1.5 padding is
    RSA-specific, so an EC / Ed25519 / Ed448 key would otherwise fail with a
    cryptic error. Evidence integrity is load-bearing, so misconfiguration must
    fail loud, not silent.
    """
    try:
        # Try cryptography library first (pure Python, cross-platform)
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None
        )
        if not isinstance(private_key, RSAPrivateKey):
            raise ValueError(
                f"Evidence signing key must be RSA (got {type(private_key).__name__}). "
                "Set XR7_EVIDENCE_PRIVATE_KEY_PEM to an RSA PEM, or use signing mode 'hmac'."
            )
        signature = private_key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(signature).decode("ascii")

    except ImportError:
        # Fall back to openssl subprocess if cryptography not available
        with tempfile.NamedTemporaryFile(mode="w", delete=True) as key_file:
            key_file.write(private_key_pem)
            key_file.flush()
            proc = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_file.name],
                input=message.encode("utf-8"),
                capture_output=True,
                check=False,
            )
        if proc.returncode != 0:
            raise ValueError(
                f"openssl sign failed: {proc.stderr.decode('utf-8', errors='ignore').strip()}"
            )
        return base64.b64encode(proc.stdout).decode("ascii")


def openssl_rsa_verify(message: str, signature_b64: str, public_key_pem: str) -> bool:
    """Verify RSA-SHA256 signature using cryptography library or openssl subprocess.

    Returns ``False`` if the public key is not RSA — audit verification must
    never silently succeed against the wrong key type.
    """
    try:
        # Try cryptography library first (pure Python, cross-platform)
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

        try:
            signature = base64.b64decode(signature_b64.encode("ascii"), validate=True)
        except Exception:
            return False

        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        if not isinstance(public_key, RSAPublicKey):
            return False

        try:
            public_key.verify(
                signature, message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    except ImportError:
        # Fall back to openssl subprocess if cryptography not available
        try:
            signature = base64.b64decode(signature_b64.encode("ascii"), validate=True)
        except Exception:
            return False

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=True) as key_file,
            tempfile.NamedTemporaryFile(mode="wb", delete=True) as sig_file,
        ):
            key_file.write(public_key_pem)
            key_file.flush()
            sig_file.write(signature)
            sig_file.flush()
            proc = subprocess.run(
                [
                    "openssl",
                    "dgst",
                    "-sha256",
                    "-verify",
                    key_file.name,
                    "-signature",
                    sig_file.name,
                ],
                input=message.encode("utf-8"),
                capture_output=True,
                check=False,
            )
        return proc.returncode == 0


# ---------------------------------------------------------------------------
# High-level packet helpers
# ---------------------------------------------------------------------------


def seal_packet(base_packet: dict[str, Any], prior_packet_hash: str | None) -> dict[str, Any]:
    """Compute and return the integrity block for *base_packet*.

    The returned dict is meant to be attached as ``packet["integrity"]``.
    The caller is responsible for that assignment and any subsequent
    persistence.
    """
    packet_hash = compute_packet_hash(base_packet)
    chain_hash = compute_chain_hash(prior_packet_hash, packet_hash)
    mode = signing_mode()

    if mode == "rsa":
        private_key_pem = os.environ.get("XR7_EVIDENCE_PRIVATE_KEY_PEM")
        if private_key_pem:
            signature = openssl_rsa_sign(chain_hash, private_key_pem)
            signature_algorithm = "RSA-SHA256"
            key_source = "env:XR7_EVIDENCE_PRIVATE_KEY_PEM"
        else:
            mode = "hmac"  # RSA key not configured — fall back silently

    if mode == "hmac":
        signature, key_source = hmac_sign(chain_hash)
        signature_algorithm = "HMAC-SHA256"

    line_hashes = [
        sha256_hex(canonicalize(line))
        for line in base_packet.get("proof", {}).get("ledger_evidence", [])
    ]
    return {
        "packet_hash": packet_hash,
        "prior_packet_hash": prior_packet_hash,
        "chain_hash": chain_hash,
        "signature": signature,
        "signature_algorithm": signature_algorithm,
        "hash_algorithm": "SHA-256",
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "line_hashes": line_hashes,
        "key_source": key_source,
    }


def verify_packet_integrity(packet: dict[str, Any]) -> dict[str, Any]:
    """Verify all integrity fields of a sealed evidence packet.

    Returns a dict with ``valid: bool`` and a ``checks`` breakdown.
    Does not require a DB session; safe to call from any context.
    """
    if not isinstance(packet, dict):
        return {"valid": False, "error": "packet is not a dict"}

    integrity = packet.get("integrity")
    if not isinstance(integrity, dict):
        return {"valid": False, "error": "integrity block missing"}

    base_packet = {k: v for k, v in packet.items() if k != "integrity"}
    expected_packet_hash = compute_packet_hash(base_packet)
    prior_packet_hash = integrity.get("prior_packet_hash")
    expected_chain_hash = compute_chain_hash(prior_packet_hash, expected_packet_hash)

    packet_hash_matches = expected_packet_hash == integrity.get("packet_hash")
    chain_hash_matches = expected_chain_hash == integrity.get("chain_hash")

    expected_line_hashes = [
        sha256_hex(canonicalize(line))
        for line in base_packet.get("proof", {}).get("ledger_evidence", [])
    ]
    line_hashes_match = expected_line_hashes == (integrity.get("line_hashes") or [])

    algorithm = str(integrity.get("signature_algorithm") or "")
    signature = str(integrity.get("signature") or "")
    if algorithm == "RSA-SHA256":
        public_key_pem = os.environ.get("XR7_EVIDENCE_PUBLIC_KEY_PEM", "")
        signature_valid = bool(public_key_pem) and openssl_rsa_verify(
            expected_chain_hash, signature, public_key_pem
        )
        signature_mode = "rsa"
    else:
        signature_valid = hmac_verify(expected_chain_hash, signature)
        signature_mode = "hmac"

    valid = packet_hash_matches and chain_hash_matches and line_hashes_match and signature_valid
    return {
        "valid": valid,
        "checks": {
            "packet_hash_matches": packet_hash_matches,
            "chain_hash_matches": chain_hash_matches,
            "line_hashes_match": line_hashes_match,
            "signature_valid": signature_valid,
        },
        "signature_mode": signature_mode,
        "packet_hash": integrity.get("packet_hash"),
        "prior_packet_hash": prior_packet_hash,
        "chain_hash": integrity.get("chain_hash"),
    }
