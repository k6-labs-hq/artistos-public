from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.sync_job import SyncJob
from tests.conftest import TestSession


client = TestClient(app)


def _headers(role: str, *, key: str = "org-secret") -> dict[str, str]:
    return {
        "X-Org-Key": key,
        "X-Org-Role": role,
        "X-Org-Actor": "ops@xr7.test",
    }


def _seed_org_data(org_id: str = "org-1") -> str:
    db = TestSession()
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Managed Artist",
            role=f"org:{org_id}",
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.flush()

        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.PLATFORM,
            subtype="UGC_LEAK",
            severity=AnomalySeverity.HIGH,
            status=AnomalyStatus.OPEN,
            confidence_score=0.92,
            estimated_recoverable=1450.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(anomaly)

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.IN_REVIEW,
            recovered_amount=0.0,
            sol_deadline=datetime.now(timezone.utc) + timedelta(days=20),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)

        issue = MetadataIssue(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            issue_type="MISSING_ISWC",
            severity="HIGH",
            issue_key="work:abc:iswc",
            before_value_json="{}",
            after_value_json="{}",
            repair_status="DETECTED",
            confidence_score=0.9,
            projected_leakage_avoided=320.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(issue)

        sync_job = SyncJob(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            integration="spotify",
            status="FAILED",
            attempts=2,
            max_attempts=3,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(sync_job)

        db.commit()
        return artist.id
    finally:
        db.close()


def test_management_dashboard_requires_management_roles(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    _seed_org_data("org-1")

    denied = client.get("/management/org-1/dashboard", headers=_headers("viewer"))
    assert denied.status_code == 403

    allowed = client.get("/management/org-1/dashboard", headers=_headers("org_admin"))
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["role"] == "org_admin"
    assert "wow_factor_analytics" in payload
    assert "forecast" in payload
    assert "drilldowns" in payload


def test_management_drilldowns_and_forecast(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    artist_id = _seed_org_data("org-2")

    artist = client.get(f"/management/org-2/artists/{artist_id}", headers=_headers("org_analyst"))
    assert artist.status_code == 200
    artist_payload = artist.json()
    assert artist_payload["artist"]["id"] == artist_id
    assert "forecast" in artist_payload

    anomalies = client.get(
        "/management/org-2/anomalies",
        headers=_headers("org_analyst"),
        params={"severity": "HIGH", "limit": 25},
    )
    assert anomalies.status_code == 200
    assert anomalies.json()["count"] >= 1

    claims = client.get(
        "/management/org-2/claims",
        headers=_headers("org_manager"),
        params={"sol_window_days": 30},
    )
    assert claims.status_code == 200
    claim_items = claims.json()["items"]
    assert any(item["in_sol_window"] for item in claim_items)

    forecast = client.get("/management/org-2/forecast", headers=_headers("org_manager"))
    assert forecast.status_code == 200
    forecast_payload = forecast.json()
    assert "forecast_disclaimer" in forecast_payload
    assert "predicted_total_next_90_days" in forecast_payload


def test_operator_dashboard_requires_operator_role(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    _seed_org_data("org-3")

    denied = client.get("/xr7/operator/dashboard", headers=_headers("org_admin"))
    assert denied.status_code == 403

    allowed = client.get("/xr7/operator/dashboard", headers=_headers("xr7_operator"))
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["role"] == "xr7_operator"
    assert "global_feed" in payload
    assert "system_health" in payload
    assert "activity_map" in payload
    assert "pipeline_overview" in payload