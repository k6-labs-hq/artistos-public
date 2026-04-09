from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus

client = TestClient(app)


def _create_artist() -> str:
    response = client.post("/artists/", json={"name": f"Artist-{uuid.uuid4()}", "ipi_number": None, "stage_names": []})
    assert response.status_code == 201
    return response.json()["id"]


def test_required_auth_statement_catalog_variance_recovery_ledger_routes():
    artist_id = _create_artist()

    providers = client.get("/auth/providers")
    assert providers.status_code == 200
    assert any(p["provider"] == "spotify" for p in providers.json()["providers"])

    connect = client.post("/auth/connect/spotify", params={"redirect_uri": "https://example.org/callback"})
    assert connect.status_code == 200
    assert connect.json()["provider"] == "spotify"

    statement_upload = client.post(
        "/statements/upload",
        json={
            "work_id": "work-1",
            "isrc": "USAAA1234567",
            "iswc": "T-000.000.001-0",
            "title": "Track",
            "artist_name": "A",
            "writer_name": "W",
            "publisher_name": "P",
            "distributor": "DistroKid",
            "platform": "Spotify",
            "usage_type": "stream",
            "usage_count": 10,
            "payout_amount": 1.25,
            "payout_currency": "USD",
            "confidence_score": 0.8,
            "source_file_id": "src-1",
            "metadata_flags": {"matched": "isrc"},
        },
    )
    assert statement_upload.status_code == 201
    assert statement_upload.json()["event_id"]

    # Status endpoint uses statement upload audit records from ingestion module.
    missing_status = client.get(f"/statements/{uuid.uuid4()}/status")
    assert missing_status.status_code == 404

    catalog_confirm = client.post(
        "/catalog/confirm",
        json={
            "artist_id": artist_id,
            "works": [
                {"work_id": "work-1", "title": "Track", "writer_name": "Writer A", "publisher_name": "Publisher A"}
            ],
        },
    )
    assert catalog_confirm.status_code == 200
    assert catalog_confirm.json()["created_nodes"] >= 1

    catalog = client.get("/catalog", params={"artist_id": artist_id})
    assert catalog.status_code == 200
    assert len(catalog.json()["nodes"]) >= 1

    db = _TestSession()
    try:
        anomaly = Anomaly(
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING_PAYMENT",
            severity=AnomalySeverity.HIGH,
            status=AnomalyStatus.OPEN,
            expected_amount=100.0,
            actual_amount=0.0,
            estimated_recoverable=100.0,
            confidence_score=0.9,
            description="Missing royalty",
        )
        db.add(anomaly)
        db.flush()

        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.IDENTIFIED,
            recovered_amount=0.0,
            evidence={},
        )
        db.add(claim)
        db.commit()
        anomaly_id = anomaly.id
        claim_id = claim.id
    finally:
        db.close()

    variance = client.get("/variance", params={"artist_id": artist_id})
    assert variance.status_code == 200
    assert variance.json()["count"] >= 1

    evidence = client.get(f"/variance/{anomaly_id}/evidence")
    assert evidence.status_code == 200
    assert evidence.json()["variance_id"] == anomaly_id

    submit = client.post(f"/recovery/{claim_id}/submit")
    assert submit.status_code == 200
    assert "queued" in submit.json()

    ledger = client.get("/ledger", params={"artist_id": artist_id})
    assert ledger.status_code == 200
    assert len(ledger.json()) >= 1
    entry_id = ledger.json()[0]["id"]

    single_entry = client.get(f"/ledger/{entry_id}")
    assert single_entry.status_code == 200
    assert single_entry.json()["id"] == entry_id
