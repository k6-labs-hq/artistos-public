from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from tests.conftest import TestSession as _TestSession


client = TestClient(app)


def _create_artist() -> Artist:
    db = _TestSession()
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Support Test Artist",
            email="support@example.com",
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()
        db.refresh(artist)
        return artist
    finally:
        db.close()


def test_support_chat_and_history_roundtrip():
    artist = _create_artist()

    chat_res = client.post(
        f"/artists/{artist.id}/support/chat",
        json={"message": "What does MISSING_MECHANICAL mean?"},
    )
    assert chat_res.status_code == 200
    payload = chat_res.json()
    assert payload["artist_id"] == artist.id
    assert payload["thread_id"]
    assert isinstance(payload["suggested_quick_replies"], list)
    assert payload["confidence"] >= 0.0

    history_res = client.get(
        f"/artists/{artist.id}/support/history",
        params={"thread_id": payload["thread_id"], "page": 1, "page_size": 10},
    )
    assert history_res.status_code == 200
    history = history_res.json()
    assert history["total"] >= 2
    assert len(history["items"]) >= 2


def test_support_actions_and_suggestions():
    artist = _create_artist()

    action_res = client.post(
        f"/artists/{artist.id}/support/action",
        json={"action": "generate_weekly_digest_now", "payload": {}},
    )
    assert action_res.status_code == 200
    action_payload = action_res.json()
    assert action_payload["action"] == "generate_weekly_digest_now"
    assert "digest_preview" in action_payload["result"]

    suggestion_res = client.get(f"/artists/{artist.id}/support/suggestions")
    assert suggestion_res.status_code == 200
    suggestions = suggestion_res.json()["suggestions"]
    assert 1 <= len(suggestions) <= 5


def test_dashboard_includes_support_payload():
    artist = _create_artist()
    dash = client.get(f"/artists/{artist.id}/dashboard")
    assert dash.status_code == 200
    payload = dash.json()
    assert "support" in payload
    support = payload["support"]
    assert support["agent_available"] is True
    assert "unread_support_messages" in support
    assert "proactive_tip" in support
