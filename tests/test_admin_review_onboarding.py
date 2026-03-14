from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Ops Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def _seed_claim_with_anomaly(artist_id: str) -> str:
    db = _TestSession()
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        confidence_score=0.8,
        estimated_recoverable=1200.0,
        created_at=datetime.now(timezone.utc),
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,
        recovered_amount=1200.0,
        evidence={"seed": True},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.add(claim)
    db.commit()
    cid = claim.id
    db.close()
    return cid


def test_onboarding_status_flow_new_onboarded_active():
    artist_id = _create_artist()

    status_before = client.get(f"/artists/{artist_id}/onboarding/status")
    assert status_before.status_code == 200
    assert status_before.json()["status"] == "NEW"

    accept = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert accept.status_code == 201

    status_after_terms = client.get(f"/artists/{artist_id}/onboarding/status")
    assert status_after_terms.status_code == 200
    assert status_after_terms.json()["status"] in {"ONBOARDED", "ACTIVE"}
    assert status_after_terms.json()["gates"]["terms_accepted"] is True

    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    upload = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert upload.status_code == 201

    status_after_upload = client.get(f"/artists/{artist_id}/onboarding/status")
    assert status_after_upload.status_code == 200
    assert status_after_upload.json()["status"] == "ACTIVE"
    assert status_after_upload.json()["gates"]["statement_uploaded"] is True


def test_review_queue_auto_item_on_evidence_generation(monkeypatch):
    monkeypatch.setenv("ANALYST_API_KEY", "analyst-secret")
    artist_id = _create_artist()
    claim_id = _seed_claim_with_anomaly(artist_id)

    evidence = client.post(f"/claims/{claim_id}/evidence")
    assert evidence.status_code == 200

    queue = client.get(
        "/review-queue/items",
        headers={"X-Analyst-Key": "analyst-secret", "X-Analyst-Email": "analyst@xr7.test"},
    )
    assert queue.status_code == 200
    items = queue.json()
    assert any(i["source_type"] == "EVIDENCE" and i["source_id"] == claim_id for i in items)


def test_admin_console_pagination_and_audit_logs(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "admin-secret")
    artist_id = _create_artist()

    artists = client.get(
        "/admin/artists?limit=5&offset=0&sort=created_at_desc",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops-user@xr7.test"},
    )
    assert artists.status_code == 200
    artists_payload = artists.json()
    assert "total" in artists_payload and "items" in artists_payload
    assert artists_payload["limit"] == 5

    review_queue = client.get(
        f"/admin/review-queue?artist_id={artist_id}",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops-user@xr7.test"},
    )
    assert review_queue.status_code == 200
    assert "items" in review_queue.json()

    logs = client.get(
        "/admin/audit-logs?limit=20",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops-user@xr7.test"},
    )
    assert logs.status_code == 200
    assert len(logs.json()) >= 2


def test_readiness_expanded_sections_present():
    resp = client.get("/health/readiness")
    assert resp.status_code == 200
    body = resp.json()
    assert "ingestion" in body
    assert "queues" in body
    assert "storage" in body
    assert "ml" in body
    assert "plugins" in body
    assert "webhooks" in body
