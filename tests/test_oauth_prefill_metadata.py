from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.artist import Artist

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="OAuth Prefill Artist",
            email=None,
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()
        return artist.id
    finally:
        db.close()


def test_oauth_exchange_persists_profile_metadata():
    artist_id = _create_artist()

    create_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session",
        json={
            "provider": "google",
            "redirect_uri": "https://example.com/callback",
            "scopes": ["openid", "email", "profile"],
            "tenant_id": "default",
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()

    exchange_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session/{created['session_id']}/exchange",
        json={
            "state": created["oauth_state"],
            "code": "oauth-code-1",
            "external_account_id": "google-account-123",
            "tenant_id": "default",
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "display_name": "Nova Artist",
            "profile_metadata": {
                "name": "Nova Artist",
                "email": "nova@example.com",
                "picture": "https://example.com/avatar.png",
            },
        },
    )
    assert exchange_resp.status_code == 200
    account = exchange_resp.json()["account"]
    assert "nova@example.com" in account["profile_metadata_json"]
