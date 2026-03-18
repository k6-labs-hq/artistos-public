from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.api.routers import auth as auth_router
from XR7.models.artist import Artist
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _seed_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Soft Auth Test Artist",
        email=f"soft-auth-{uuid.uuid4().hex[:8]}@example.com",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def test_soft_guarded_endpoints_allow_missing_token_by_default(monkeypatch):
    monkeypatch.setattr(auth_router, "_ENFORCE_AUTH_GLOBALLY", False)
    artist_id = _seed_artist()

    for path in [
        f"/artists/{artist_id}/earnings",
        f"/artists/{artist_id}/earnings/history",
        f"/artists/{artist_id}/anomalies",
        f"/artists/{artist_id}/claims",
    ]:
        response = client.get(path)
        assert response.status_code == 200


def test_soft_guarded_endpoints_reject_invalid_token_even_when_optional(monkeypatch):
    monkeypatch.setattr(auth_router, "_ENFORCE_AUTH_GLOBALLY", False)
    artist_id = _seed_artist()
    headers = {"Authorization": "Bearer not-a-valid-token"}

    for path in [
        f"/artists/{artist_id}/earnings",
        f"/artists/{artist_id}/earnings/history",
        f"/artists/{artist_id}/anomalies",
        f"/artists/{artist_id}/claims",
    ]:
        response = client.get(path, headers=headers)
        assert response.status_code == 401


def test_soft_guarded_endpoints_require_token_when_global_enforced(monkeypatch):
    monkeypatch.setattr(auth_router, "_ENFORCE_AUTH_GLOBALLY", True)
    artist_id = _seed_artist()

    for path in [
        f"/artists/{artist_id}/earnings",
        f"/artists/{artist_id}/earnings/history",
        f"/artists/{artist_id}/anomalies",
        f"/artists/{artist_id}/claims",
    ]:
        response = client.get(path)
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing bearer token"
