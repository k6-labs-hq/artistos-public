from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    response = client.post(
        "/artists/",
        json={"name": f"E2E-{uuid.uuid4()}", "ipi_number": None, "stage_names": []},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_forensic_route_chain_e2e_with_queue_assertion():
    """Exercise the forensic route chain and assert recovery submit queues a task."""
    artist_id = _create_artist()

    # 1) Auth provider discovery + connect URL
    providers = client.get("/auth/providers")
    assert providers.status_code == 200
    assert any(p["provider"] == "spotify" for p in providers.json()["providers"])

    connect = client.post("/auth/connect/spotify", params={"redirect_uri": "https://example.test/callback"})
    assert connect.status_code == 200
    assert "authorization_url" in connect.json()

    # 2) Statement normalization insert
    statement_resp = client.post(
        "/statements/upload",
        json={
            "work_id": "work-e2e-1",
            "isrc": "USAAA1234567",
            "iswc": "T-000.000.001-0",
            "title": "E2E Song",
            "artist_name": "E2E Artist",
            "writer_name": "E2E Writer",
            "publisher_name": "E2E Pub",
            "distributor": "DistroKid",
            "platform": "Spotify",
            "usage_type": "stream",
            "usage_count": 1000,
            "payout_amount": 4.25,
            "payout_currency": "USD",
            "confidence_score": 0.95,
            "source_file_id": "src-e2e-1",
            "metadata_flags": {"lineage": "row-12"},
        },
    )
    assert statement_resp.status_code == 201
    assert statement_resp.json()["event_id"]

    # 3) Catalog confirm + readback
    confirm = client.post(
        "/catalog/confirm",
        json={
            "artist_id": artist_id,
            "works": [
                {
                    "work_id": "work-e2e-1",
                    "title": "E2E Song",
                    "writer_name": "E2E Writer",
                    "publisher_name": "E2E Pub",
                }
            ],
        },
    )
    assert confirm.status_code == 200
    assert confirm.json()["created_nodes"] >= 1

    catalog = client.get("/catalog", params={"artist_id": artist_id})
    assert catalog.status_code == 200
    assert any(n["node_type"] == "Work" for n in catalog.json()["nodes"])

    # 4) Seed variance + claim for downstream evidence/recovery routes
    db = _TestSession()
    try:
        anomaly = Anomaly(
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype="RATE_BELOW_MARKET",
            severity=AnomalySeverity.HIGH,
            status=AnomalyStatus.OPEN,
            expected_amount=80.0,
            actual_amount=10.0,
            estimated_recoverable=70.0,
            confidence_score=0.88,
            description="Rate variance detected",
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

    # 5) Variance list + evidence fetch
    variance = client.get("/variance", params={"artist_id": artist_id})
    assert variance.status_code == 200
    assert variance.json()["count"] >= 1

    evidence = client.get(f"/variance/{anomaly_id}/evidence")
    assert evidence.status_code == 200
    assert evidence.json()["variance_id"] == anomaly_id

    # 6) Recovery submit with explicit queue assertion
    with patch("XR7.api.routers.forensic.submit_recovery_action.delay", return_value=SimpleNamespace(id="task-123")) as mocked_delay:
        submit = client.post(f"/recovery/{claim_id}/submit")
    assert submit.status_code == 200
    assert submit.json()["queued"] is True
    assert submit.json()["task_id"] == "task-123"
    mocked_delay.assert_called_once_with(claim_id)

    # 7) Ledger list + fetch single entry
    ledger = client.get("/ledger", params={"artist_id": artist_id})
    assert ledger.status_code == 200
    assert len(ledger.json()) >= 1
    entry_types = {e["entry_type"] for e in ledger.json()}
    assert "catalog_confirmed" in entry_types
    assert "recovery_submitted" in entry_types

    entry_id = ledger.json()[0]["id"]
    ledger_entry = client.get(f"/ledger/{entry_id}")
    assert ledger_entry.status_code == 200
    assert ledger_entry.json()["id"] == entry_id
