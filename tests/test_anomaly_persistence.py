from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.event import Event, EventType
from XR7.models.payment import Payment, PaymentType

client = TestClient(app)


def _seed_artist_with_anomaly_conditions() -> str:
    """Seed data that triggers at least one transparent rule finding."""
    db = _TestSession()
    artist_id = str(uuid.uuid4())
    db.add(Artist(id=artist_id, name="Persist Test", created_at=datetime.now(timezone.utc)))

    for i in range(15):
        db.add(
            Event(
                event_type=EventType.STREAM,
                artist_id=artist_id,
                timestamp=datetime.now(timezone.utc),
                quantity=1000,
                unit_value=0.004 if i < 14 else 0.04,
                currency="USD",
            )
        )
    for i in range(20):
        db.add(
            Payment(
                payment_type=PaymentType.ROYALTY,
                artist_id=artist_id,
                amount=100.0 if i < 19 else 10000.0,
                currency="USD",
                received_at=datetime.now(timezone.utc),
            )
        )

    db.commit()
    db.close()
    return artist_id


def test_detect_persists_anomalies_to_db():
    artist_id = _seed_artist_with_anomaly_conditions()

    resp = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert resp.status_code == 200
    detected = resp.json().get("detected", [])
    assert detected, "Expected at least one detected anomaly from seed"

    db = _TestSession()
    try:
        persisted = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        assert len(persisted) >= 1
        persisted_ids = {a.id for a in persisted}
        # Every anomaly in the response body should match a persisted row.
        for row in detected:
            assert row["id"] in persisted_ids
    finally:
        db.close()


def test_detect_is_idempotent():
    """Running detect twice produces no duplicate anomaly rows."""
    artist_id = _seed_artist_with_anomaly_conditions()

    first = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert first.status_code == 200
    first_ids = sorted(r["id"] for r in first.json()["detected"])

    second = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert second.status_code == 200
    second_ids = sorted(r["id"] for r in second.json()["detected"])

    assert first_ids == second_ids, "Deterministic ids should match across runs"

    db = _TestSession()
    try:
        count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
        assert count == len(first_ids), "No duplicates on re-detection"
    finally:
        db.close()


def test_detect_enables_claim_creation():
    """The whole point of #136: after detect, claim creation must find the anomaly."""
    artist_id = _seed_artist_with_anomaly_conditions()

    detect = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert detect.status_code == 200
    detected = detect.json().get("detected", [])
    assert detected

    # Pick an anomaly whose recoverability allows claim drafting.
    claim_candidate = next(
        (r for r in detected if r.get("claim_draft_allowed") is not False),
        detected[0],
    )
    anomaly_id = claim_candidate["id"]

    # The claim router requires the anomaly to exist by id — this was the MVP break.
    db = _TestSession()
    try:
        row = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        assert row is not None, "Anomaly must be persisted so claim creation can reference it"
        assert row.artist_id == artist_id
    finally:
        db.close()
