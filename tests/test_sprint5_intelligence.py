from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from XR7.models.base import Base, engine, get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setenv("ANALYST_API_KEY", "test-analyst-key")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def analyst_headers():
    return {
        "X-Analyst-Key": "test-analyst-key",
        "X-Analyst-Email": "analyst@test.com",
    }


def _create_artist() -> str:
    db = next(get_db())
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Sprint5 Test Artist",
            email="sprint5@test.com",
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()
        return artist.id
    finally:
        db.close()


def test_model_drift_endpoint_detects_shift():
    artist_id = _create_artist()

    for _ in range(100):
        response = client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={
                "feedback_type": "CLAIM_OUTCOME",
                "outcome": "RECOVERED",
                "model_version": "v2.1",
                "model_prediction": 0.05,
            },
        )
        assert response.status_code == 200

    for _ in range(20):
        response = client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={
                "feedback_type": "CLAIM_OUTCOME",
                "outcome": "RECOVERED",
                "model_version": "v2.1",
                "model_prediction": 0.95,
            },
        )
        assert response.status_code == 200

    drift_resp = client.get(
        f"/artists/{artist_id}/intelligence/model-drift?model_version=v2.1&psi_threshold=0.2"
    )
    assert drift_resp.status_code == 200
    drift = drift_resp.json()
    assert drift["psi_score"] > 0.2
    assert drift["drift_detected"] is True


def test_confidence_tier_routing_creates_low_tier_item(analyst_headers):
    artist_id = _create_artist()
    response = client.post(
        "/review-queue/items/route-confidence",
        headers=analyst_headers,
        json={
            "artist_id": artist_id,
            "source_type": "ML_CONFIDENCE",
            "source_id": "test-source-1",
            "reason": "Low confidence claim",
            "confidence_score": 0.41,
            "payload": {"subtype": "royalty"},
        },
    )
    assert response.status_code == 201
    item = response.json()
    assert abs(item["priority_score"] - 0.9) < 1e-9
    assert item["payload"]["confidence_tier"] == "low"


def test_override_decision_tracks_active_learning(analyst_headers):
    artist_id = _create_artist()
    create_resp = client.post(
        "/review-queue/items/route-confidence",
        headers=analyst_headers,
        json={
            "artist_id": artist_id,
            "source_type": "ML_CONFIDENCE",
            "source_id": "test-source-2",
            "reason": "Needs analyst check",
            "confidence_score": 0.78,
            "payload": {"model_version": "v2.1", "model_prediction": 0.78},
        },
    )
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    decision_resp = client.post(
        f"/review-queue/items/{item_id}/decision",
        headers=analyst_headers,
        json={"decision": "REJECT", "notes": "Override model decision"},
    )
    assert decision_resp.status_code == 200

    list_resp = client.get(
        f"/review-queue/items?artist_id={artist_id}",
        headers=analyst_headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1
    payload = items[0]["payload"] or {}
    assert int(payload.get("override_count") or 0) >= 1
    assert payload.get("active_learning_candidate") is True
