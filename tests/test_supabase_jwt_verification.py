"""
Supabase JWT verification — dual-mode (HS256 legacy + ES256/RS256 JWKS).

Supabase projects created from ~2026 on sign tokens with asymmetric keys
(ES256 by default) and publish the public key at
{SUPABASE_URL}/auth/v1/.well-known/jwks.json. Older projects still use
HS256 with a shared secret. This module must support both.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from XR7.auth.supabase import verify_supabase_jwt


@pytest.fixture(autouse=True)
def _clear_jwks_cache():
    from XR7.auth import supabase as sb

    sb._jwk_client.cache_clear()
    yield
    sb._jwk_client.cache_clear()


@pytest.fixture
def hs256_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://testproj.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "unit-test-hs256-secret")
    monkeypatch.setenv("SUPABASE_JWT_AUDIENCE", "authenticated")


def _issue_hs256(secret: str, claims: dict) -> str:
    return jwt.encode(claims, secret, algorithm="HS256")


def _issue_es256(private_key, kid: str, claims: dict) -> str:
    return jwt.encode(claims, private_key, algorithm="ES256", headers={"kid": kid})


def test_hs256_token_verifies_with_shared_secret(hs256_env):
    claims = {
        "sub": "user-1",
        "aud": "authenticated",
        "iss": "https://testproj.supabase.co/auth/v1",
        "email": "nova@example.com",
    }
    token = _issue_hs256("unit-test-hs256-secret", claims)
    got = verify_supabase_jwt(token)
    assert got["sub"] == "user-1"
    assert got["email"] == "nova@example.com"


def test_hs256_token_with_wrong_secret_rejected(hs256_env, monkeypatch):
    claims = {"sub": "user-1", "aud": "authenticated"}
    token = _issue_hs256("a-different-secret", claims)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        verify_supabase_jwt(token)
    assert excinfo.value.status_code == 401


def test_es256_token_verifies_via_jwks(monkeypatch):
    """Generate an ES256 keypair, mock JWKS, and confirm verify_supabase_jwt accepts."""
    key = ec.generate_private_key(ec.SECP256R1())
    kid = "test-es256-kid"

    # Build the public JWK payload that PyJWKClient will fetch
    from jwt.algorithms import ECAlgorithm

    public_numbers = key.public_key().public_numbers()
    import base64

    def _b64url_uint(n: int) -> str:
        byte_len = (n.bit_length() + 7) // 8
        raw = n.to_bytes(byte_len, "big")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": _b64url_uint(public_numbers.x),
        "y": _b64url_uint(public_numbers.y),
        "alg": "ES256",
        "kid": kid,
        "use": "sig",
    }
    jwks_payload = {"keys": [jwk]}

    # Sanity: the constructed JWK must produce the same public key as `key`.
    assert ECAlgorithm.from_jwk(json.dumps(jwk))

    monkeypatch.setenv("SUPABASE_URL", "https://testproj.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_AUDIENCE", "authenticated")
    # Deliberately unset so we prove JWKS path doesn't need the shared secret
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)

    token = _issue_es256(
        key,
        kid,
        {
            "sub": "user-2",
            "aud": "authenticated",
            "iss": "https://testproj.supabase.co/auth/v1",
            "email": "nova@example.com",
        },
    )

    # Intercept JWKS fetch so we don't hit the real Supabase URL in tests.
    with patch("jwt.jwks_client.PyJWKClient.fetch_data", return_value=jwks_payload):
        got = verify_supabase_jwt(token)
    assert got["sub"] == "user-2"
    assert got["email"] == "nova@example.com"


def test_es256_token_with_wrong_key_rejected(monkeypatch):
    """Token signed by the wrong private key must fail even if kid matches."""
    good_key = ec.generate_private_key(ec.SECP256R1())
    attacker_key = ec.generate_private_key(ec.SECP256R1())
    kid = "good-kid"

    import base64

    def _b64url_uint(n: int) -> str:
        byte_len = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(n.to_bytes(byte_len, "big")).rstrip(b"=").decode()

    good_pub = good_key.public_key().public_numbers()
    jwks_payload = {
        "keys": [
            {
                "kty": "EC",
                "crv": "P-256",
                "x": _b64url_uint(good_pub.x),
                "y": _b64url_uint(good_pub.y),
                "alg": "ES256",
                "kid": kid,
                "use": "sig",
            }
        ]
    }

    monkeypatch.setenv("SUPABASE_URL", "https://testproj.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_AUDIENCE", "authenticated")

    token = _issue_es256(
        attacker_key,
        kid,
        {"sub": "user-x", "aud": "authenticated"},
    )

    from fastapi import HTTPException

    with patch("jwt.jwks_client.PyJWKClient.fetch_data", return_value=jwks_payload):
        with pytest.raises(HTTPException) as excinfo:
            verify_supabase_jwt(token)
    assert excinfo.value.status_code == 401


def test_token_without_sub_rejected(hs256_env):
    """Claims must include a subject — both modes."""
    from fastapi import HTTPException

    token = _issue_hs256("unit-test-hs256-secret", {"aud": "authenticated"})
    with pytest.raises(HTTPException) as excinfo:
        verify_supabase_jwt(token)
    assert excinfo.value.status_code == 401


def test_unsupported_algorithm_rejected(monkeypatch):
    """'none' alg and similar must not verify."""
    from fastapi import HTTPException

    # Craft a token with alg=HS384 (not in our allowed set).
    token = jwt.encode({"sub": "x", "aud": "authenticated"}, "secret", algorithm="HS384")
    monkeypatch.setenv("SUPABASE_URL", "https://testproj.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "irrelevant")

    with pytest.raises(HTTPException) as excinfo:
        verify_supabase_jwt(token)
    assert excinfo.value.status_code == 401
    assert (
        "Unsupported" in str(excinfo.value.detail)
        or "algorithm" in str(excinfo.value.detail).lower()
    )


def test_missing_supabase_url_for_es256_returns_503(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    token = _issue_es256(key, "any", {"sub": "x", "aud": "authenticated"})
    monkeypatch.delenv("SUPABASE_URL", raising=False)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        verify_supabase_jwt(token)
    assert excinfo.value.status_code == 503
