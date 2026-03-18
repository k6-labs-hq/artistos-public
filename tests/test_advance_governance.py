from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.auth.jwt_service import jwt_service
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.services.analyst_gated_advance import run_nightly_advance_opportunity_scan
from tests.conftest import TestSession as _TestSession


client = TestClient(app)


def _create_artist(name: str) -> str:
    resp = client.post("/artists/", json={"name": name, "role": "org:advance-governance"})
    assert resp.status_code == 201
    return str(resp.json()["id"])


def _artist_headers(artist_id: str) -> dict[str, str]:
    login = client.post("/auth/login/artist", json={"artist_id": artist_id})
    assert login.status_code == 200
    token = str(login.json()["access_token"])
    return {"Authorization": f"Bearer {token}"}


def _role_headers(subject: str, role: str) -> dict[str, str]:
    token = jwt_service.issue_token(subject=subject, role=role)
    return {"Authorization": f"Bearer {token}"}


def test_offer_not_visible_until_exec_approval_and_publish():
    artist_id = _create_artist("Advance Gate Hidden Offer")

    db = _TestSession()
    try:
        db.add(
            Anomaly(
                artist_id=artist_id,
                category=AnomalyCategory.ROYALTY,
                subtype="UNDERPAYMENT_SPIKE",
                severity=AnomalySeverity.HIGH,
                status=AnomalyStatus.OPEN,
                confidence_score=0.95,
                estimated_recoverable=20_000.0,
                created_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
    finally:
        db.close()

    run_resp = client.post(
        "/admin/advances/run-nightly-eval",
        headers=_role_headers("analyst@xr7", "analyst"),
    )
    assert run_resp.status_code == 200

    artist_offers_resp = client.get(
        f"/artists/{artist_id}/advance/offers",
        headers=_artist_headers(artist_id),
    )
    assert artist_offers_resp.status_code == 200
    assert artist_offers_resp.json()["count"] == 0


def test_dual_approval_publish_and_artist_accept_flow():
    artist_id = _create_artist("Advance Gate Full Flow")

    db = _TestSession()
    try:
        db.add(
            Anomaly(
                artist_id=artist_id,
                category=AnomalyCategory.ROYALTY,
                subtype="MISSING_STATEMENT_RECOVERY",
                severity=AnomalySeverity.HIGH,
                status=AnomalyStatus.OPEN,
                confidence_score=0.93,
                estimated_recoverable=25_000.0,
                created_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        summary = run_nightly_advance_opportunity_scan(db)
        assert int(summary["created"]) >= 1
    finally:
        db.close()

    analyst_queue = client.get(
        "/admin/advances/queue/analyst",
        headers=_role_headers("analyst@xr7", "analyst"),
    )
    assert analyst_queue.status_code == 200
    items = [i for i in analyst_queue.json()["items"] if i["artist_id"] == artist_id]
    assert items
    opportunity_id = str(items[0]["opportunity_id"])

    analyst_decision = client.post(
        f"/admin/advances/opportunities/{opportunity_id}/analyst-decision",
        json={"approved": True, "notes": "evidence quality is sufficient"},
        headers=_role_headers("analyst@xr7", "analyst"),
    )
    assert analyst_decision.status_code == 200

    exec_queue = client.get(
        "/admin/advances/queue/executive",
        headers=_role_headers("exec@xr7", "exec"),
    )
    assert exec_queue.status_code == 200
    exec_items = [i for i in exec_queue.json()["items"] if i["opportunity_id"] == opportunity_id]
    assert exec_items

    exec_decision = client.post(
        f"/admin/advances/opportunities/{opportunity_id}/executive-decision",
        json={"approved": True, "notes": "approved within fee cap"},
        headers=_role_headers("exec@xr7", "exec"),
    )
    assert exec_decision.status_code == 200

    publish = client.post(
        f"/admin/advances/opportunities/{opportunity_id}/publish-offer",
        headers=_role_headers("exec@xr7", "exec"),
    )
    assert publish.status_code == 200
    published_offer_id = str(publish.json()["offer_id"])

    artist_offers = client.get(
        f"/artists/{artist_id}/advance/offers",
        headers=_artist_headers(artist_id),
    )
    assert artist_offers.status_code == 200
    payload = artist_offers.json()
    assert payload["count"] >= 1
    offer_ids = {str(x["offer_id"]) for x in payload["offers"]}
    assert published_offer_id in offer_ids

    accept = client.post(
        f"/artists/{artist_id}/advance/offers/{published_offer_id}/accept",
        headers=_artist_headers(artist_id),
    )
    assert accept.status_code == 200
    assert accept.json()["status"] == "ACCEPTED"
