"""require_admin_session accepts EITHER X-Admin-Key or a JWT with role=admin.

Pinned via /admin/claims/queue, which uses the dependency. Tests verify:
- X-Admin-Key path still works (back-compat with operator curl/automation)
- JWT path with role=admin works (new path for the operator dashboard
  signed in via Supabase)
- JWT with role=artist is rejected with 403
- Missing both is rejected with 401
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.auth.jwt_service import jwt_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def _admin_key_env(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key-value")
    monkeypatch.setenv("XR7_ENV", "development")


def test_admin_key_path_works():
    resp = client.get(
        "/admin/claims/queue",
        headers={"X-Admin-Key": "test-admin-key-value"},
    )
    assert resp.status_code == 200, resp.text
    assert "items" in resp.json()


def test_jwt_admin_path_works():
    token = jwt_service.issue_token(
        subject="founder@k6-labs.com", role="admin", extra={"tenant_id": "default"}
    )
    resp = client.get(
        "/admin/claims/queue",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text


def test_jwt_artist_rejected_403():
    token = jwt_service.issue_token(
        subject="art_xyz", role="artist", extra={"artist_id": "art_xyz"}
    )
    resp = client.get(
        "/admin/claims/queue",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_no_auth_rejected_401():
    resp = client.get("/admin/claims/queue")
    assert resp.status_code == 401


def test_wrong_admin_key_falls_through_to_401():
    """A bad key with no JWT is the same as no auth — 401, not 403."""
    resp = client.get(
        "/admin/claims/queue",
        headers={"X-Admin-Key": "wrong-key-entirely"},
    )
    assert resp.status_code == 401
