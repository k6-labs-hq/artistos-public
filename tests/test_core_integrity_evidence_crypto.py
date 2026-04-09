"""
Tests for XR7.core.integrity.evidence_crypto
=============================================
Covers:
  - canonicalize() produces stable, sorted, deterministic JSON bytes
  - sha256_hex() matches expected digests for known inputs
  - compute_packet_hash() is stable across identical dicts
  - compute_chain_hash() uses GENESIS sentinel for first packet
  - compute_chain_hash() chains correctly when prior hash is provided
  - hmac_sign() / hmac_verify() round-trip (default dev secret + env var)
  - hmac_verify() rejects tampered signatures
  - seal_packet() returns the full integrity block with all expected keys
  - verify_packet_integrity() validates a freshly sealed packet
  - verify_packet_integrity() detects packet tampering
  - verify_packet_integrity() detects chain-hash tampering
  - verify_packet_integrity() handles malformed inputs gracefully
  - Domain-boundary check: module is DB-free

Fixtures: all pure — no DB session needed.

Recommended future tests:
  - RSA sign/verify round-trip (requires an actual test keypair in env).
  - RSA fallback to HMAC when private key not configured.
  - Property-based: arbitrary dict → seal → verify always returns valid=True.
  - Concurrent seal_packet() calls (thread-safety of temp-file handling).
"""
from __future__ import annotations

import hashlib
import json

from XR7.core.integrity.evidence_crypto import (
    canonicalize,
    compute_chain_hash,
    compute_packet_hash,
    hmac_sign,
    hmac_verify,
    seal_packet,
    sha256_hex,
    verify_packet_integrity,
)

# ---------------------------------------------------------------------------
# Domain-boundary guard
# ---------------------------------------------------------------------------

def test_no_db_imports_in_evidence_crypto():
    import XR7.core.integrity.evidence_crypto as mod

    with open(mod.__file__) as f:
        source = f.read()

    forbidden = ["sqlalchemy", "SessionLocal", "from XR7.services", "from XR7.api"]
    for token in forbidden:
        assert token not in source, f"Pure core module must not import '{token}'"


# ---------------------------------------------------------------------------
# canonicalize
# ---------------------------------------------------------------------------

class TestCanonicalize:
    def test_returns_bytes(self):
        assert isinstance(canonicalize({"a": 1}), bytes)

    def test_key_order_is_sorted(self):
        result = canonicalize({"z": 1, "a": 2})
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_identical_dicts_produce_identical_bytes(self):
        d = {"title": "Shape of You", "isrc": "GBAHS1700437", "amount": 12.50}
        assert canonicalize(d) == canonicalize(d)

    def test_different_insertion_order_produces_same_bytes(self):
        a = canonicalize({"b": 2, "a": 1})
        b = canonicalize({"a": 1, "b": 2})
        assert a == b

    def test_different_values_produce_different_bytes(self):
        assert canonicalize({"x": 1}) != canonicalize({"x": 2})

    def test_nested_structures_are_serialised(self):
        d = {"proof": {"lines": [{"amount": 10}]}}
        result = canonicalize(d)
        assert b"proof" in result and b"lines" in result


# ---------------------------------------------------------------------------
# sha256_hex
# ---------------------------------------------------------------------------

class TestSha256Hex:
    def test_known_digest(self):
        # echo -n "hello" | sha256sum
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert sha256_hex(b"hello") == expected

    def test_empty_bytes_has_known_digest(self):
        expected = hashlib.sha256(b"").hexdigest()
        assert sha256_hex(b"") == expected

    def test_returns_lowercase_hex(self):
        result = sha256_hex(b"test")
        assert result == result.lower()
        assert len(result) == 64


# ---------------------------------------------------------------------------
# compute_packet_hash
# ---------------------------------------------------------------------------

class TestComputePacketHash:
    def test_stable_for_same_input(self):
        packet = {"artist_id": "a1", "amount": 100.0, "currency": "USD"}
        assert compute_packet_hash(packet) == compute_packet_hash(packet)

    def test_changes_when_content_changes(self):
        p1 = {"amount": 100.0}
        p2 = {"amount": 100.1}
        assert compute_packet_hash(p1) != compute_packet_hash(p2)

    def test_hash_is_64_char_hex(self):
        h = compute_packet_hash({"x": 1})
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_integrity_key_excluded_from_its_own_hash(self):
        """Callers strip 'integrity' before hashing — test that hash of base only."""
        base = {"artist_id": "a1", "amount": 50.0}
        direct = compute_packet_hash(base)
        with_integrity = {**base, "integrity": {"packet_hash": "dummy"}}
        # The direct hash and the hash of {**base} must be identical;
        # the caller is responsible for not passing the full packet.
        assert direct == compute_packet_hash(base)
        # Adding extra keys changes the hash
        assert direct != compute_packet_hash(with_integrity)


# ---------------------------------------------------------------------------
# compute_chain_hash
# ---------------------------------------------------------------------------

class TestComputeChainHash:
    def test_genesis_sentinel_used_when_no_prior(self):
        h = compute_chain_hash(None, "abc123")
        expected_input = "GENESIS:abc123".encode("utf-8")
        expected = hashlib.sha256(expected_input).hexdigest()
        assert h == expected

    def test_prior_hash_is_chained(self):
        h = compute_chain_hash("prior_abc", "current_xyz")
        expected_input = "prior_abc:current_xyz".encode("utf-8")
        expected = hashlib.sha256(expected_input).hexdigest()
        assert h == expected

    def test_different_prior_produces_different_chain_hash(self):
        h1 = compute_chain_hash("prior_1", "same_packet")
        h2 = compute_chain_hash("prior_2", "same_packet")
        assert h1 != h2

    def test_returns_64_char_hex(self):
        h = compute_chain_hash(None, "pkt")
        assert len(h) == 64


# ---------------------------------------------------------------------------
# hmac_sign / hmac_verify
# ---------------------------------------------------------------------------

class TestHmacSignVerify:
    def test_sign_returns_tuple_of_str(self):
        sig, key_source = hmac_sign("test_chain_hash")
        assert isinstance(sig, str)
        assert isinstance(key_source, str)

    def test_verify_accepts_valid_signature(self):
        chain_hash = "some_chain_hash_value"
        sig, _ = hmac_sign(chain_hash)
        assert hmac_verify(chain_hash, sig) is True

    def test_verify_rejects_wrong_signature(self):
        sig, _ = hmac_sign("chain_hash")
        assert hmac_verify("chain_hash", "bad" + sig) is False

    def test_verify_rejects_tampered_payload(self):
        sig, _ = hmac_sign("chain_hash_A")
        assert hmac_verify("chain_hash_B", sig) is False

    def test_sign_uses_env_secret_when_set(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_HMAC_SECRET", "test-secret-123")
        sig1, key_src = hmac_sign("data")
        assert key_src == "env:XR7_EVIDENCE_HMAC_SECRET"
        # Sign with a different secret to confirm env var is used
        monkeypatch.setenv("XR7_EVIDENCE_HMAC_SECRET", "different-secret")
        sig2, _ = hmac_sign("data")
        assert sig1 != sig2

    def test_verify_correctly_roundtrips_with_env_secret(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_HMAC_SECRET", "roundtrip-secret")
        chain_hash = "test_chain_hash_roundtrip"
        sig, _ = hmac_sign(chain_hash)
        assert hmac_verify(chain_hash, sig) is True

    def test_dev_secret_label_when_env_not_set(self, monkeypatch):
        monkeypatch.delenv("XR7_EVIDENCE_HMAC_SECRET", raising=False)
        _, key_src = hmac_sign("data")
        assert key_src == "default-dev-secret"


# ---------------------------------------------------------------------------
# seal_packet
# ---------------------------------------------------------------------------

class TestSealPacket:
    def _make_base_packet(self):
        return {
            "artist_id": "test-artist",
            "anomaly_id": "anm-001",
            "amount": 250.00,
            "currency": "USD",
        }

    def test_seal_returns_dict_with_all_required_keys(self):
        integrity = seal_packet(self._make_base_packet(), prior_packet_hash=None)
        required_keys = {
            "packet_hash", "prior_packet_hash", "chain_hash",
            "signature", "signature_algorithm", "hash_algorithm",
            "signed_at", "line_hashes", "key_source",
        }
        assert required_keys.issubset(integrity.keys())

    def test_hash_algorithm_is_sha256(self):
        integrity = seal_packet(self._make_base_packet(), None)
        assert integrity["hash_algorithm"] == "SHA-256"

    def test_prior_packet_hash_is_none_for_first_packet(self):
        integrity = seal_packet(self._make_base_packet(), None)
        assert integrity["prior_packet_hash"] is None

    def test_prior_packet_hash_propagated(self):
        integrity = seal_packet(self._make_base_packet(), "abc123")
        assert integrity["prior_packet_hash"] == "abc123"

    def test_signed_at_is_iso_string(self):
        integrity = seal_packet(self._make_base_packet(), None)
        from datetime import datetime
        # Must be parseable as ISO datetime
        dt = datetime.fromisoformat(integrity["signed_at"])
        assert dt is not None

    def test_signature_algorithm_is_hmac_sha256_by_default(self, monkeypatch):
        monkeypatch.delenv("XR7_EVIDENCE_SIGNING_MODE", raising=False)
        integrity = seal_packet(self._make_base_packet(), None)
        assert integrity["signature_algorithm"] == "HMAC-SHA256"

    def test_line_hashes_empty_when_no_ledger_evidence(self):
        integrity = seal_packet(self._make_base_packet(), None)
        assert integrity["line_hashes"] == []

    def test_line_hashes_computed_for_ledger_evidence(self):
        packet = {
            **self._make_base_packet(),
            "proof": {"ledger_evidence": [{"line": 1, "amount": 10.0}, {"line": 2, "amount": 5.0}]},
        }
        integrity = seal_packet(packet, None)
        assert len(integrity["line_hashes"]) == 2
        for h in integrity["line_hashes"]:
            assert len(h) == 64  # SHA-256 hex

    def test_different_packets_produce_different_hashes(self):
        p1 = seal_packet({"amount": 100.0}, None)
        p2 = seal_packet({"amount": 200.0}, None)
        assert p1["packet_hash"] != p2["packet_hash"]


# ---------------------------------------------------------------------------
# verify_packet_integrity
# ---------------------------------------------------------------------------

class TestVerifyPacketIntegrity:
    def _sealed(self, payload=None, prior=None):
        base = payload or {"artist_id": "a1", "amount": 300.0}
        integrity = seal_packet(base, prior)
        return {**base, "integrity": integrity}

    def test_freshly_sealed_packet_is_valid(self):
        packet = self._sealed()
        result = verify_packet_integrity(packet)
        assert result["valid"] is True

    def test_all_checks_true_for_valid_packet(self):
        packet = self._sealed()
        checks = verify_packet_integrity(packet)["checks"]
        assert all(checks.values()), f"Some checks failed: {checks}"

    def test_chained_packet_is_valid(self):
        first = self._sealed({"amount": 100.0})
        first_hash = first["integrity"]["packet_hash"]
        second = self._sealed({"amount": 200.0}, prior=first_hash)
        assert verify_packet_integrity(second)["valid"] is True

    def test_tampered_amount_invalidates_packet_hash(self):
        packet = self._sealed({"artist_id": "a1", "amount": 300.0})
        packet["amount"] = 999.0  # tamper after sealing
        result = verify_packet_integrity(packet)
        assert result["valid"] is False
        assert result["checks"]["packet_hash_matches"] is False

    def test_tampered_chain_hash_detected(self):
        packet = self._sealed()
        packet["integrity"]["chain_hash"] = "forged_chain_hash"
        result = verify_packet_integrity(packet)
        assert result["valid"] is False
        assert result["checks"]["chain_hash_matches"] is False

    def test_missing_integrity_block_returns_invalid(self):
        result = verify_packet_integrity({"artist_id": "a1"})
        assert result["valid"] is False
        assert "integrity block missing" in result.get("error", "")

    def test_non_dict_input_returns_invalid(self):
        result = verify_packet_integrity("not a dict")
        assert result["valid"] is False

    def test_none_input_returns_invalid(self):
        result = verify_packet_integrity(None)
        assert result["valid"] is False

    def test_tampered_signature_detected(self):
        packet = self._sealed()
        packet["integrity"]["signature"] = "0" * 64  # forge signature
        result = verify_packet_integrity(packet)
        assert result["valid"] is False
        assert result["checks"]["signature_valid"] is False

    def test_tampered_line_hashes_detected(self):
        packet = self._sealed({
            "amount": 100.0,
            "proof": {"ledger_evidence": [{"line": 1}]},
        })
        packet["integrity"]["line_hashes"] = ["forged_hash"]
        result = verify_packet_integrity(packet)
        assert result["valid"] is False
        assert result["checks"]["line_hashes_match"] is False

    def test_result_contains_signature_mode(self):
        packet = self._sealed()
        result = verify_packet_integrity(packet)
        assert result["signature_mode"] in ("hmac", "rsa")

    def test_result_exposes_packet_and_chain_hash(self):
        packet = self._sealed()
        result = verify_packet_integrity(packet)
        assert "packet_hash" in result
        assert "chain_hash" in result
        assert "prior_packet_hash" in result


# ---------------------------------------------------------------------------
# RSA sign / verify round-trip
# ---------------------------------------------------------------------------

# Minimal 2048-bit RSA key pair for testing only — never used in production.
_TEST_RSA_PRIVATE_KEY = """\
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqbwdPM1DqGBUV
d3EF6Sn1mAmaWbhDLckQdMTdhOBgw5NFN5Kv4g0BcQJSIwyFJwP+Xy4A2VeEHQ3J
zJSSS7lZxbOYHaYlwzCoiKMPnydm8kf+g1wDJJukeR2718Itla9EZ/m2jZ2zKFpo
1KNXH3h3zUvtOB56KeKdAPXRqBh3HkwPHN01sjiOO/0LwhzCEXUmHFHqDeEFPs/p
Znki+x2MYVwGG9Qr17qvI6lGnLpKWmeR0yFDZZJrgH0GhkGb3vVST0ouXX5DnXBq
UfHLmJty6Uz/AH8I61+Ah17srAbAn63R91mtuWJEbNDcYFHVcOkZ6RPo6AcOdD6J
VfcpUi+rAgMBAAECggEAP7YfomDJh6kXAJ5U1uPRtqhuNpABjMNp3Uf5a+HHSwTx
YbejkzJKsFZBitjlTkVGfemwtcqJp66AwAZFJ+c8061PNLcorAcqgmYJpsZVIWvC
tAcA93/Q2wwXrGe8g/PnwAeqVq7b2+Ri37tVkDUIgKhzEKug4QQVXaHFQum2s5g3
QsMifMiHN1O0pcAahsOi1MjUZkbNw+gxq6erWT/vaZd9RWBJAt1iv0XzWFI5bGFI
dEsRWfMsL0HqBbIjX5xHZ3kZFU1vzQGWUjO4/uZVAE6OQw0fvNRZ+r/L4v483m4g
xX15nvpjBPFTkRpCS4QcrBVElQGCG7RlHRQJx2zzqQKBgQDum38Df19iZnWZPWIU
EVbI+V2hwV797OMzXHbIcVUMebI4NcrCQYoCo+ZS+oJMkcyrPInPGx40bUe85ks5
92kO/gkmvi49sbpxm5bphyx9LQl8toIzTFXEw+v7raNuqU9o2wGUaUjArwkTZ8r6
n+gzK0ukJ85bjN3ZnOr4kXCA7wKBgQC222KxmQiipC0Li7M4AbMvP2vn784Oprs/
uDbUaS3ZjL6jRulgYNZmtZQaPeAqVjpR3ls0HXf3SAZZnw2oZhIeQctPb72CZYEH
W3vPsrkMPbUchAUDBQzS3rH+WVVbXNKyX7vRJ26tW0mMbBxXw+nTUwDIVL/bKell
UM3GNBUFBQKBgB2WvM5zOiHasNSa7xGsAMYVXk4Ty7LTcG1LFxPOMgzE/pvH1+f0
9qdTKdm6ZPQX1Hibnj9HjpxTvOSo7kU28BlC2WGrjdJqusMh1zoIYDT5o8aKX2T7
H1uyLA5evviXGFjZZ72+vJ3gVtDIOzyPHd1SjiPCJ+3kbxJwShce+gOTAoGACBGu
TT//jY3JHxVPF02b5p3Z2SZP5X2eDbXHVaA+kbcQQoxCiCo9y9J/cpkAZ13evPYe
+DHEtXjMLvBB3giDDCrDGgJITpTEGNsEn6m3WL7wWw3IWtXCNxv0ptCyX5G9CnoH
A7fFvoikujmbFpRioRyskCqNPNKgpgPm0LRDqTECgYEAnUP4Vgz8gwNt821XwZVS
GF3ZbPgzP4qzW52p7LGJ11uRBj9o1HQ60GNU1/5vY2Ere4QQBSml5uqKOcjOqUAJ
DCLQkE71mnVQHlVGfftjoUFcQL/g87rw0QhFfMNyR9w08ga7XbfI1ZpYbRuDAm8M
kwHjWfgd4sTh01lO0TYFv1A=
-----END PRIVATE KEY-----
"""

_TEST_RSA_PUBLIC_KEY = """\
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqm8HTzNQ6hgVFXdxBekp
9ZgJmlm4Qy3JEHTE3YTgYMOTRTeSr+INAXECUiMMhScD/l8uANlXhB0NycyUkku5
WcWzmB2mJcMwqIijD58nZvJH/oNcAySbpHkdu9fCLZWvRGf5to2dsyhaaNSjVx94
d81L7TgeeininQD10agYdx5MDxzdNbI4jjv9C8IcwhF1JhxR6g3hBT7P6WZ5Ivsd
jGFcBhvUK9e6ryOpRpy6SlpnkdMhQ2WSa4B9BoZBm971Uk9KLl1+Q51walHxy5ib
culM/wB/COtfgIde7KwGwJ+t0fdZrbliRGzQ3GBR1XDpGekT6OgHDnQ+iVX3KVIv
qwIDAQAB
-----END PUBLIC KEY-----
"""


class TestRsaSignVerify:
    """Tests for openssl_rsa_sign / openssl_rsa_verify using a test key pair."""

    def test_rsa_sign_returns_base64_string(self):
        from XR7.core.integrity.evidence_crypto import openssl_rsa_sign
        sig = openssl_rsa_sign("test_message", _TEST_RSA_PRIVATE_KEY)
        import base64
        # Must be valid base64
        decoded = base64.b64decode(sig.encode("ascii"), validate=True)
        assert len(decoded) > 0

    def test_rsa_verify_accepts_valid_signature(self):
        from XR7.core.integrity.evidence_crypto import openssl_rsa_sign, openssl_rsa_verify
        message = "chain_hash_for_rsa_test"
        sig = openssl_rsa_sign(message, _TEST_RSA_PRIVATE_KEY)
        assert openssl_rsa_verify(message, sig, _TEST_RSA_PUBLIC_KEY) is True

    def test_rsa_verify_rejects_wrong_message(self):
        from XR7.core.integrity.evidence_crypto import openssl_rsa_sign, openssl_rsa_verify
        sig = openssl_rsa_sign("original_message", _TEST_RSA_PRIVATE_KEY)
        assert openssl_rsa_verify("tampered_message", sig, _TEST_RSA_PUBLIC_KEY) is False

    def test_rsa_verify_rejects_invalid_base64(self):
        from XR7.core.integrity.evidence_crypto import openssl_rsa_verify
        # Non-base64 signature should return False, not raise
        assert openssl_rsa_verify("message", "not!valid!base64!!!", _TEST_RSA_PUBLIC_KEY) is False

    def test_seal_packet_uses_rsa_when_mode_is_rsa_and_key_is_present(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
        monkeypatch.setenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", _TEST_RSA_PRIVATE_KEY)
        integrity = seal_packet({"amount": 100.0}, None)
        assert integrity["signature_algorithm"] == "RSA-SHA256"
        assert integrity["key_source"] == "env:XR7_EVIDENCE_PRIVATE_KEY_PEM"

    def test_seal_packet_falls_back_to_hmac_when_rsa_key_missing(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
        monkeypatch.delenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", raising=False)
        integrity = seal_packet({"amount": 100.0}, None)
        # Falls back silently to HMAC
        assert integrity["signature_algorithm"] == "HMAC-SHA256"

    def test_verify_rsa_signed_packet_is_valid(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
        monkeypatch.setenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", _TEST_RSA_PRIVATE_KEY)
        monkeypatch.setenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", _TEST_RSA_PUBLIC_KEY)
        base = {"artist_id": "rsa-artist", "amount": 500.0}
        integrity = seal_packet(base, None)
        packet = {**base, "integrity": integrity}
        result = verify_packet_integrity(packet)
        assert result["valid"] is True
        assert result["signature_mode"] == "rsa"

    def test_verify_rsa_packet_without_public_key_is_invalid(self, monkeypatch):
        monkeypatch.setenv("XR7_EVIDENCE_SIGNING_MODE", "rsa")
        monkeypatch.setenv("XR7_EVIDENCE_PRIVATE_KEY_PEM", _TEST_RSA_PRIVATE_KEY)
        monkeypatch.delenv("XR7_EVIDENCE_PUBLIC_KEY_PEM", raising=False)
        base = {"artist_id": "rsa-artist", "amount": 500.0}
        integrity = seal_packet(base, None)
        # Manually mark as RSA-SHA256 so verify takes the RSA path
        integrity["signature_algorithm"] = "RSA-SHA256"
        packet = {**base, "integrity": integrity}
        result = verify_packet_integrity(packet)
        # No public key → signature_valid is False
        assert result["checks"]["signature_valid"] is False

