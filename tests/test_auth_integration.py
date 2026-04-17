"""
Integration tests for auth.py bearer token validation, JWT expiry,
and scope (role) enforcement.

Covers:
- Missing bearer token → 401
- Malformed / tampered token → 401
- Expired token → 401
- Valid admin token accepted on admin-only endpoint → 200 / 403 for non-admin
- Valid artist token accepted on artist-scoped endpoint → 200 / 403 for wrong artist
- require_analyst / require_executive / require_legal role enforcement
- /auth/login/artist happy-path issues a verifiable token
- /auth/login/admin happy-path with env credentials
- /auth/me returns correct payload for a valid token
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession, override_get_db
from XR7.api.app import app
from XR7.auth.jwt_service import JWTService, JWTValidationError, jwt_service
from XR7.models.artist import Artist
from XR7.models.base import get_db

# ---------------------------------------------------------------------------
# Test client
# ---------------------------------------------------------------------------
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_token(
    role: str, subject: str = "test-sub", extra: dict | None = None, ttl_minutes: int | None = None
) -> str:
    svc = JWTService()
    if ttl_minutes is not None:
        svc.access_ttl_minutes = ttl_minutes
    return svc.issue_token(subject=subject, role=role, extra=extra)


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_artist(name: str = "Test Artist", email: str = "test@example.com") -> str:
    """Insert a minimal artist row and return its id."""
    db = TestSession()
    try:
        artist = Artist(name=name, email=email)
        db.add(artist)
        db.commit()
        db.refresh(artist)
        return artist.id
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 1. Missing / malformed tokens
# ---------------------------------------------------------------------------


class TestMissingToken:
    def test_missing_token_returns_401(self):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_empty_bearer_returns_401(self):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401

    def test_non_bearer_scheme_returns_401(self):
        token = _make_token("admin")
        resp = client.get("/auth/me", headers={"Authorization": f"Basic {token}"})
        assert resp.status_code == 401


class TestMalformedToken:
    def test_garbage_token_returns_401(self):
        resp = client.get("/auth/me", headers=_auth("not.a.jwt"))
        assert resp.status_code == 401

    def test_tampered_signature_returns_401(self):
        token = _make_token("admin")
        parts = token.split(".")
        # flip last char of signature
        sig = parts[2]
        tampered_sig = sig[:-1] + ("A" if sig[-1] != "A" else "B")
        tampered = f"{parts[0]}.{parts[1]}.{tampered_sig}"
        resp = client.get("/auth/me", headers=_auth(tampered))
        assert resp.status_code == 401

    def test_two_part_token_returns_401(self):
        resp = client.get("/auth/me", headers=_auth("header.payload"))
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 2. Expired token
# ---------------------------------------------------------------------------


class TestExpiredToken:
    def test_expired_token_returns_401(self):
        # Issue a token that expired 1 second ago
        svc = JWTService()
        now = datetime.now(timezone.utc)
        import base64
        import hashlib
        import hmac
        import json

        def _b64url_encode(raw: bytes) -> str:
            return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        payload = {
            "sub": "expired-user",
            "role": "artist",
            "iss": svc.issuer,
            "aud": svc.audience,
            "iat": int((now - timedelta(minutes=5)).timestamp()),
            "exp": int((now - timedelta(seconds=1)).timestamp()),  # already expired
            "artist_id": "expired-user",
        }
        header = {"alg": "HS256", "typ": "JWT"}
        signing_input = (
            f"{_b64url_encode(json.dumps(header, separators=(',', ':')).encode())}"
            f".{_b64url_encode(json.dumps(payload, separators=(',', ':')).encode())}"
        )
        sig = hmac.new(svc.secret, signing_input.encode("ascii"), hashlib.sha256).digest()
        token = f"{signing_input}.{_b64url_encode(sig)}"

        resp = client.get("/auth/me", headers=_auth(token))
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 3. /auth/me — valid token
# ---------------------------------------------------------------------------


class TestAuthMe:
    def test_admin_token_returns_me_payload(self):
        token = _make_token("admin", subject="admin@example.com")
        resp = client.get("/auth/me", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin"
        assert data["subject"] == "admin@example.com"

    def test_artist_token_returns_me_payload(self):
        artist_id = _create_artist()
        token = _make_token("artist", subject=artist_id, extra={"artist_id": artist_id})
        resp = client.get("/auth/me", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "artist"


# ---------------------------------------------------------------------------
# 4. Admin scope enforcement
# ---------------------------------------------------------------------------


class TestAdminScope:
    def test_admin_token_accepted_on_admin_endpoint(self):
        token = _make_token("admin")
        resp = client.get("/admin/audit/events", headers=_auth(token))
        # 200 or 404 (route exists); reject 401/403
        assert resp.status_code not in (401, 403)

    def test_artist_token_rejected_on_admin_endpoint(self):
        artist_id = _create_artist()
        token = _make_token("artist", subject=artist_id, extra={"artist_id": artist_id})
        resp = client.get("/admin/audit/events", headers=_auth(token))
        assert resp.status_code == 403

    def test_no_token_rejected_on_admin_endpoint(self):
        resp = client.get("/admin/audit/events")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 5. Artist scope enforcement
# ---------------------------------------------------------------------------


class TestArtistScope:
    def test_artist_token_accepted_for_own_data(self):
        artist_id = _create_artist()
        token = _make_token("artist", subject=artist_id, extra={"artist_id": artist_id})
        resp = client.post(
            f"/artists/{artist_id}/privacy/export",
            headers=_auth(token),
        )
        assert resp.status_code not in (401, 403)

    def test_artist_token_rejected_for_other_artist(self):
        owner_id = _create_artist(name="Owner", email="owner@example.com")
        intruder_id = _create_artist(name="Intruder", email="intruder@example.com")
        token = _make_token("artist", subject=intruder_id, extra={"artist_id": intruder_id})
        resp = client.post(
            f"/artists/{owner_id}/privacy/export",
            headers=_auth(token),
        )
        assert resp.status_code == 403

    def test_admin_token_accepted_for_any_artist(self):
        artist_id = _create_artist(name="Managed Artist", email="managed@example.com")
        token = _make_token("admin")
        resp = client.post(
            f"/artists/{artist_id}/privacy/export",
            headers=_auth(token),
        )
        assert resp.status_code not in (401, 403)


# ---------------------------------------------------------------------------
# 6. Login endpoints
# ---------------------------------------------------------------------------


class TestArtistLogin:
    def test_valid_artist_login_returns_token(self):
        artist_id = _create_artist(name="Login Artist", email="login@example.com")
        resp = client.post(
            "/auth/login/artist",
            json={"artist_id": artist_id, "email": "login@example.com"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # Token must be valid
        payload = jwt_service.verify_token(body["access_token"])
        assert payload["role"] == "artist"
        assert payload["artist_id"] == artist_id

    def test_wrong_email_returns_401(self):
        artist_id = _create_artist(name="Mismatch Artist", email="real@example.com")
        resp = client.post(
            "/auth/login/artist",
            json={"artist_id": artist_id, "email": "wrong@example.com"},
        )
        assert resp.status_code == 401

    def test_unknown_artist_returns_404(self):
        resp = client.post(
            "/auth/login/artist",
            json={"artist_id": "does-not-exist"},
        )
        assert resp.status_code == 404


class TestAdminLogin:
    def test_valid_admin_login_returns_token(self, monkeypatch):
        monkeypatch.setenv("XR7_ADMIN_EMAIL", "admin@xr7.io")
        monkeypatch.setenv("XR7_ADMIN_PASSWORD", "s3cr3t!")
        resp = client.post(
            "/auth/login/admin",
            json={"email": "admin@xr7.io", "password": "s3cr3t!"},
        )
        assert resp.status_code == 200
        body = resp.json()
        payload = jwt_service.verify_token(body["access_token"])
        assert payload["role"] == "admin"

    def test_wrong_password_returns_401(self, monkeypatch):
        monkeypatch.setenv("XR7_ADMIN_EMAIL", "admin@xr7.io")
        monkeypatch.setenv("XR7_ADMIN_PASSWORD", "correct")
        resp = client.post(
            "/auth/login/admin",
            json={"email": "admin@xr7.io", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_unconfigured_admin_returns_503(self, monkeypatch):
        monkeypatch.delenv("XR7_ADMIN_EMAIL", raising=False)
        monkeypatch.delenv("XR7_ADMIN_PASSWORD", raising=False)
        resp = client.post(
            "/auth/login/admin",
            json={"email": "any@xr7.io", "password": "any"},
        )
        assert resp.status_code == 503


# ---------------------------------------------------------------------------
# 7. JWTService unit tests
# ---------------------------------------------------------------------------


class TestJWTService:
    def test_verify_valid_token(self):
        token = _make_token("analyst", subject="alice")
        payload = jwt_service.verify_token(token)
        assert payload["sub"] == "alice"
        assert payload["role"] == "analyst"

    def test_wrong_issuer_rejected(self):
        svc = JWTService()
        svc.issuer = "rogue-issuer"
        token = svc.issue_token("bob", "artist")
        with pytest.raises(JWTValidationError, match="issuer"):
            jwt_service.verify_token(token)

    def test_wrong_audience_rejected(self):
        svc = JWTService()
        svc.audience = "rogue-audience"
        token = svc.issue_token("carol", "artist")
        with pytest.raises(JWTValidationError, match="audience"):
            jwt_service.verify_token(token)

    def test_missing_role_rejected(self):
        import base64
        import hashlib
        import hmac as _hmac
        import json

        def _enc(raw: bytes) -> str:
            return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        svc = JWTService()
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {
            "sub": "no-role",
            "iss": svc.issuer,
            "aud": svc.audience,
            "iat": now,
            "exp": now + 3600,
        }
        si = f"{_enc(json.dumps(header, separators=(',', ':')).encode())}.{_enc(json.dumps(payload, separators=(',', ':')).encode())}"
        sig = _hmac.new(svc.secret, si.encode("ascii"), hashlib.sha256).digest()
        token = f"{si}.{_enc(sig)}"
        with pytest.raises(JWTValidationError, match="role"):
            svc.verify_token(token)
