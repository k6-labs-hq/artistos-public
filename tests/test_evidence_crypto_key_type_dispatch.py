"""
Evidence signing must fail fast on non-RSA keys (#148).

Background: openssl_rsa_sign uses PKCS#1 v1.5 padding, which is RSA-only. If
someone loaded the wrong key type (EC, Ed25519, Ed448, etc.), the prior code
would raise a cryptic ``AttributeError`` deep inside the cryptography library
— or worse, silently succeed against a key the verifier can't check.

These tests lock in:
  1. RSA round-trip works (happy path).
  2. Non-RSA private key raises ValueError with a clear remediation message.
  3. Non-RSA public key causes verify to return False (never silently true).
"""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

from XR7.core.integrity.evidence_crypto import openssl_rsa_sign, openssl_rsa_verify


def _pem_pair_rsa() -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return priv_pem, pub_pem


def _pem_pair_ec() -> tuple[str, str]:
    key = ec.generate_private_key(ec.SECP256R1())
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return priv_pem, pub_pem


def _pem_pair_ed25519() -> tuple[str, str]:
    key = ed25519.Ed25519PrivateKey.generate()
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return priv_pem, pub_pem


def test_rsa_sign_verify_roundtrip():
    priv, pub = _pem_pair_rsa()
    sig = openssl_rsa_sign("hello-world", priv)
    assert openssl_rsa_verify("hello-world", sig, pub) is True


def test_rsa_verify_rejects_tampered_message():
    priv, pub = _pem_pair_rsa()
    sig = openssl_rsa_sign("hello-world", priv)
    assert openssl_rsa_verify("goodbye-world", sig, pub) is False


def test_ec_private_key_raises_valueerror():
    """Feeding an EC key into the RSA signer must fail loudly, not cryptically."""
    priv, _ = _pem_pair_ec()
    with pytest.raises(ValueError, match="must be RSA"):
        openssl_rsa_sign("hello-world", priv)


def test_ed25519_private_key_raises_valueerror():
    priv, _ = _pem_pair_ed25519()
    with pytest.raises(ValueError, match="must be RSA"):
        openssl_rsa_sign("hello-world", priv)


def test_ec_public_key_verification_returns_false():
    """A wrong-type public key must never silently succeed verification."""
    rsa_priv, _ = _pem_pair_rsa()
    sig = openssl_rsa_sign("hello-world", rsa_priv)
    _, ec_pub = _pem_pair_ec()
    assert openssl_rsa_verify("hello-world", sig, ec_pub) is False


def test_ed25519_public_key_verification_returns_false():
    rsa_priv, _ = _pem_pair_rsa()
    sig = openssl_rsa_sign("hello-world", rsa_priv)
    _, ed_pub = _pem_pair_ed25519()
    assert openssl_rsa_verify("hello-world", sig, ed_pub) is False
