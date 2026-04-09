from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from tests.conftest import TestSession
from XR7.api.app import app
from XR7.models.xr7_royalty import XR7AIDecisionAuditLog, XR7Track

client = TestClient(app)


def test_xr7_metadata_repair_endpoints() -> None:
    artist_id = "artist-xr7-meta"
    db = TestSession()
    try:
        track = XR7Track(
            tenant_id="default",
            artist_id=artist_id,
            title="  Untidy Title  ",
            metadata_quality_score=0.2,
        )
        db.add(track)
        db.commit()
        db.refresh(track)
        suggestion_id = f"track:{track.id}"
    finally:
        db.close()

    suggest_resp = client.post(
        f"/artists/{artist_id}/xr7/metadata/repair/suggest",
        json={"tenant_id": "default", "scope": "catalog", "max_items": 10},
    )
    assert suggest_resp.status_code == 200
    payload = suggest_resp.json()
    assert "suggestions" in payload

    apply_resp = client.post(
        f"/artists/{artist_id}/xr7/metadata/repair/apply",
        json={"tenant_id": "default", "suggestion_ids": [suggestion_id], "dry_run": False},
    )
    assert apply_resp.status_code == 200
    out = apply_resp.json()
    assert out["applied_count"] == 1

    db = TestSession()
    try:
        audit_count = (
            db.query(XR7AIDecisionAuditLog)
            .filter(
                XR7AIDecisionAuditLog.tenant_id == "default",
                XR7AIDecisionAuditLog.artist_id == artist_id,
                XR7AIDecisionAuditLog.decision_type == "metadata_repair_apply",
            )
            .count()
        )
        assert audit_count >= 1
    finally:
        db.close()


def test_xr7_ugc_endpoints() -> None:
    artist_id = "artist-xr7-ugc"
    ingest = client.post(
        f"/artists/{artist_id}/xr7/ugc/signals/ingest",
        json={
            "tenant_id": "default",
            "platform": "tiktok",
            "signals": [
                {
                    "ugc_content_id": "ugc-1",
                    "units": 5000,
                    "estimated_rate": 0.0008,
                    "confidence": 0.88,
                    "territory": "US",
                    "ugc_format": "shorts",
                }
            ],
        },
    )
    assert ingest.status_code == 200
    body = ingest.json()
    assert body["accepted"] == 1

    opportunities = client.get(
        f"/artists/{artist_id}/xr7/ugc/opportunities",
        params={"tenant_id": "default", "min_confidence": 0.7},
    )
    assert opportunities.status_code == 200
    rows = opportunities.json()["opportunities"]
    assert len(rows) >= 1
    assert rows[0]["ugc_content_id"] == "ugc-1"


def test_xr7_valuation_and_forecast_endpoints() -> None:
    artist_id = "artist-xr7-value"

    health = client.get(f"/artists/{artist_id}/xr7/catalog/health", params={"tenant_id": "default"})
    assert health.status_code == 200
    assert "score" in health.json()

    snapshot = client.get(
        f"/artists/{artist_id}/xr7/valuation/snapshot",
        params={"tenant_id": "default", "as_of": str(date.today())},
    )
    assert snapshot.status_code == 200
    snap = snapshot.json()
    assert "corrected_value" in snap

    forecast = client.post(
        f"/artists/{artist_id}/xr7/forecast/recovery",
        json={"tenant_id": "default", "horizon_days": 90, "scenario_overrides": {"uplift_factor": 1.1}},
    )
    assert forecast.status_code == 200
    assert "forecast_amount" in forecast.json()

    simulation = client.post(
        f"/artists/{artist_id}/xr7/simulations/what-if",
        json={
            "tenant_id": "default",
            "scenarios": [
                {"label": "base", "base": 1000, "rate_delta": 0.05, "territory_uplift": 0.1},
                {"label": "aggressive", "base": 1000, "rate_delta": 0.2, "territory_uplift": 0.15},
            ],
        },
    )
    assert simulation.status_code == 200
    assert len(simulation.json()["scenarios"]) == 2
