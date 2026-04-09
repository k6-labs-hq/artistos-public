from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist

client = TestClient(app)


def _create_artist(session) -> Artist:
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Recoverability Gate Artist",
        created_at=datetime.now(timezone.utc),
    )
    session.add(artist)
    session.commit()
    session.refresh(artist)
    return artist


def _artist_token(artist_id: str) -> str:
    resp = client.post("/auth/login/artist", json={"artist_id": artist_id})
    assert resp.status_code == 200
    return str(resp.json()["access_token"])


def test_claim_creation_rejects_expired_black_box_anomaly():
    session = _TestSession()
    try:
        artist = _create_artist(session)
        old_time = datetime.now(timezone.utc) - timedelta(days=365 * 8)
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="ASCAP_UNMATCHED_ROYALTY",
            severity=AnomalySeverity.HIGH,
            estimated_recoverable=1200.0,
            confidence_score=0.91,
            status=AnomalyStatus.OPEN,
            description="Historic unmatched ASCAP royalty",
            time_window_end=old_time,
            created_at=old_time,
        )
        session.add(anomaly)
        session.commit()

        token = _artist_token(artist.id)
        resp = client.post(
            f"/artists/{artist.id}/claims",
            json={"anomaly_id": anomaly.id, "claim_type": "RECOVERY"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422
        detail = resp.json().get("detail") or {}
        assert "recoverability_class" in detail
    finally:
        session.close()


def test_claim_creation_allows_contract_based_recoverability():
    session = _TestSession()
    try:
        artist = _create_artist(session)
        recent_time = datetime.now(timezone.utc) - timedelta(days=120)
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="RATE_DRIFT_UNDERPAYMENT",
            severity=AnomalySeverity.MEDIUM,
            estimated_recoverable=2400.0,
            confidence_score=0.87,
            status=AnomalyStatus.OPEN,
            description="Contract underpayment signal",
            time_window_end=recent_time,
            created_at=recent_time,
        )
        session.add(anomaly)
        session.commit()

        token = _artist_token(artist.id)
        resp = client.post(
            f"/artists/{artist.id}/claims",
            json={"anomaly_id": anomaly.id, "claim_type": "RECOVERY"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["anomaly_id"] == anomaly.id
    finally:
        session.close()
