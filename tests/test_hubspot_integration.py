from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.artist import Artist
from XR7.models.review_queue import ReviewItem, ReviewSourceType

client = TestClient(app)


def _create_artist_db() -> str:
    db = _TestSession()
    artist = Artist(id=str(uuid.uuid4()), name="HubSpot Test", created_at=datetime.now(timezone.utc))
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def test_artist_create_triggers_hubspot_sync(monkeypatch):
    calls = []

    def _fake_delay(artist_id: str, event: str = "artist_created"):
        calls.append((artist_id, event))

    monkeypatch.setattr("XR7.api.routers.artists.hubspot_sync_artist.delay", _fake_delay)

    resp = client.post("/artists/", json={"name": "CRM Artist", "email": "crm@example.com", "role": "artist"})
    assert resp.status_code == 201
    assert calls
    assert calls[0][1] == "artist_created"


def test_widget_flows_trigger_hubspot_sync(monkeypatch):
    reg_calls = []
    lead_calls = []

    monkeypatch.setattr(
        "XR7.api.routers.widget.hubspot_sync_widget_registration.delay",
        lambda **kwargs: reg_calls.append(kwargs),
    )
    monkeypatch.setattr(
        "XR7.api.routers.widget.hubspot_sync_widget_lead.delay",
        lambda lead_id, event="widget_estimate": lead_calls.append((lead_id, event)),
    )

    register = client.post(
        "/widget/register",
        json={"artist_name": "Band Lead", "phone": "+15551234567", "email": "lead@example.com"},
    )
    assert register.status_code == 200
    assert reg_calls

    dev_phone_otp = register.json().get("dev_phone_otp")
    dev_email_otp = register.json().get("dev_email_otp")
    verify = client.post(
        "/widget/verify",
        json={
            "session_id": register.json()["session_id"],
            "phone_otp": dev_phone_otp,
            "email_otp": dev_email_otp,
        },
    )
    assert verify.status_code == 200

    estimate = client.post(
        "/widget/estimate",
        json={
            "estimate_token": verify.json()["estimate_token"],
            "career_stage": "DEVELOPING",
            "genre": "POP",
            "years_active": 3,
            "territory": "US",
        },
    )
    assert estimate.status_code == 200
    assert lead_calls


def test_review_decision_emits_ml_feedback_and_metrics(monkeypatch):
    monkeypatch.setenv("ANALYST_API_KEY", "analyst-secret")
    artist_id = _create_artist_db()

    db = _TestSession()
    item = ReviewItem(
        artist_id=artist_id,
        source_type=ReviewSourceType.ANOMALY.value,
        source_id="anom-123",
        reason="low confidence anomaly",
        priority_score=800.0,
        status="OPEN",
        payload={"subtype": "RATE_DRIFT_HIGH", "category": "PLATFORM", "model_version": "v2"},
    )
    db.add(item)
    db.commit()
    item_id = item.id
    db.close()

    decide = client.post(
        f"/review-queue/items/{item_id}/decision",
        headers={"X-Analyst-Key": "analyst-secret", "X-Analyst-Email": "analyst@xr7.test"},
        json={"decision": "ESCALATE", "notes": "Need legal check"},
    )
    assert decide.status_code == 200

    events = client.get(f"/artists/{artist_id}/intelligence/feedback/events")
    assert events.status_code == 200
    assert any(e["feedback_type"] == "REVIEW_DECISION" for e in events.json())

    metrics = client.get(
        "/review-queue/metrics",
        headers={"X-Analyst-Key": "analyst-secret", "X-Analyst-Email": "analyst@xr7.test"},
    )
    assert metrics.status_code == 200
    body = metrics.json()
    assert "per_analyst_calibration" in body


def test_statement_upload_and_anomaly_detection_trigger_hubspot_updates(monkeypatch):
    calls = []
    statement_calls = []
    monkeypatch.setattr(
        "XR7.api.routers.ingestion.hubspot_sync_recovery_update.delay",
        lambda artist_id, event="recovery_update": calls.append((artist_id, event)),
    )
    monkeypatch.setattr(
        "XR7.api.routers.ingestion.hubspot_sync_statement_ingestion.delay",
        lambda artist_id, statement_id=None, statement_signals=None, event="statement_uploaded": statement_calls.append(
            (artist_id, statement_id, event)
        ),
    )
    monkeypatch.setattr(
        "XR7.api.routers.anomalies.hubspot_sync_recovery_update.delay",
        lambda artist_id, event="recovery_update": calls.append((artist_id, event)),
    )

    artist_id = _create_artist_db()
    accept = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert accept.status_code == 201

    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    upload = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert upload.status_code == 201

    detect = client.post(f"/artists/{artist_id}/anomalies/detect")
    assert detect.status_code == 200

    assert any(evt in {"first_statement_uploaded", "statement_batch_uploaded", "anomalies_detected"} for _, evt in calls)
    assert statement_calls
