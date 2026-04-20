from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession
from XR7.api.app import app
from XR7.auth.jwt_service import jwt_service
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.artist import Artist

client = TestClient(app)


def _seed_artist(org_id: str = "org-v2") -> str:
    db = TestSession()
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Sovereignty V2 Artist",
            email="v2-artist@test.xr7",
            role=f"org:{org_id}",
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()
        return artist.id
    finally:
        db.close()


def _artist_headers(artist_id: str) -> dict[str, str]:
    login = client.post("/auth/login/artist", json={"artist_id": artist_id})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _org_headers() -> dict[str, str]:
    return {
        "X-Org-Key": "org-secret",
        "X-Org-Role": "org_admin",
        "X-Org-Actor": "ops@xr7.test",
    }


def _admin_headers() -> dict[str, str]:
    token = jwt_service.issue_token(subject="admin@test.xr7", role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_management_dashboard_v2_endpoint(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    _seed_artist("org-v2")

    resp = client.get("/management/org-v2/dashboard/v2", headers=_org_headers())
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["org_id"] == "org-v2"
    assert "v2" in payload
    assert "portfolio_cohorts" in payload["v2"]
    assert "execution" in payload["v2"]


def test_ml_suite_explain_and_calibration_endpoints():
    artist_id = _seed_artist("org-ml")
    headers = _artist_headers(artist_id)

    explain = client.get(f"/artists/{artist_id}/ml/explain", headers=headers)
    assert explain.status_code == 200
    explain_payload = explain.json()
    assert explain_payload["artist_id"] == artist_id
    assert "outputs" in explain_payload
    assert "model_versions" in explain_payload

    calibration = client.get(f"/artists/{artist_id}/ml/calibration-dashboard", headers=headers)
    assert calibration.status_code == 200
    calibration_payload = calibration.json()
    assert calibration_payload["artist_id"] == artist_id
    assert "calibration" in calibration_payload
    assert "dashboard" in calibration_payload


def test_governance_export_erase_and_admin_audit_listing():
    artist_id = _seed_artist("org-governance")
    artist_headers = _artist_headers(artist_id)

    export_resp = client.post(f"/artists/{artist_id}/privacy/export", headers=artist_headers)
    assert export_resp.status_code == 200
    export_payload = export_resp.json()
    assert export_payload["artist_id"] == artist_id
    assert "export" in export_payload

    erase_resp = client.post(f"/artists/{artist_id}/privacy/erase", headers=artist_headers)
    assert erase_resp.status_code == 200
    assert erase_resp.json()["status"] == "erased"

    admin_resp = client.get("/admin/audit/events", headers=_admin_headers())
    assert admin_resp.status_code == 200
    payload = admin_resp.json()
    assert "items" in payload
    assert payload["count"] >= 1

    db = TestSession()
    try:
        assert db.query(AdminAuditLog).count() >= 1
    finally:
        db.close()
