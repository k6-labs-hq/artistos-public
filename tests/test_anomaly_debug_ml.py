from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from XR7.models.event import Event, EventType
from XR7.models.payment import Payment, PaymentType
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _seed_artist_with_events_payments() -> str:
    db = _TestSession()
    artist_id = str(uuid.uuid4())
    db.add(Artist(id=artist_id, name="Anomaly Debug Artist", created_at=datetime.now(timezone.utc)))

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


def test_detect_anomalies_returns_ml_debug_signals():
    artist_id = _seed_artist_with_events_payments()

    detect = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert detect.status_code == 200

    ml_rows = [r for r in detect.json().get("detected", []) if r.get("ml_model")]
    assert ml_rows
    assert any("model_version" in r for r in ml_rows)
    assert any("anomaly_score" in r for r in ml_rows)
