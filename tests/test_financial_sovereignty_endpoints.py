from __future__ import annotations

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.auth.jwt_service import jwt_service


client = TestClient(app)


def _create_artist(name: str, role: str = "org:sovereignty-org") -> str:
    resp = client.post("/artists/", json={"name": name, "role": role})
    assert resp.status_code == 201
    return resp.json()["id"]


def _artist_headers(artist_id: str) -> dict[str, str]:
    login = client.post("/auth/login/artist", json={"artist_id": artist_id})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _admin_headers() -> dict[str, str]:
    token = jwt_service.issue_token(subject="admin@test.xr7", role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_trust_trace_endpoint_returns_branding_payload():
    artist_id = _create_artist("Trust Trace Artist")
    resp = client.get(f"/artists/{artist_id}/trust/trace", headers=_artist_headers(artist_id))
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["artist_id"] == artist_id
    assert "trace" in payload
    assert "branding" in payload


def test_referrals_register_and_list():
    referrer_id = _create_artist("Referrer Artist")
    referred_id = _create_artist("Referred Artist")

    create_resp = client.post(
        f"/artists/{referrer_id}/referrals",
        json={"referred_artist_id": referred_id},
        headers=_artist_headers(referrer_id),
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["referred_artist_id"] == referred_id

    list_resp = client.get(
        f"/artists/{referrer_id}/referrals",
        headers=_artist_headers(referrer_id),
    )
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["artist_id"] == referrer_id
    assert "branding" in payload


def test_creator_platforms_and_ingest_endpoints():
    artist_id = _create_artist("Creator Economy Artist")
    headers = _artist_headers(artist_id)

    platforms = client.get(f"/artists/{artist_id}/creator/platforms", headers=headers)
    assert platforms.status_code == 200
    assert "supported_platforms" in platforms.json()

    ingest = client.post(
        f"/artists/{artist_id}/creator/ingest",
        json={"platform": "youtube_studio", "rows": []},
        headers=headers,
    )
    assert ingest.status_code == 200
    assert ingest.json()["events_parsed"] == 0


def test_sovereignty_rights_and_advance_endpoints():
    artist_id = _create_artist("Sovereignty Artist")
    headers = _artist_headers(artist_id)

    scan = client.get(f"/artists/{artist_id}/rights/scan", headers=headers)
    assert scan.status_code == 200
    assert "gaps" in scan.json()

    offer = client.post(
        f"/artists/{artist_id}/advance/offer",
        json={"predicted_low_forecast": 1000.0, "currency": "USD", "advance_fee_pct": 3.0},
        headers=headers,
    )
    assert offer.status_code == 200
    offer_payload = offer.json()
    assert offer_payload["eligible"] is True
    assert offer_payload["artist_id"] == artist_id


def test_messages_feed_chat_and_weekly_story():
    artist_id = _create_artist("Messages Artist")
    headers = _artist_headers(artist_id)

    feed = client.get(f"/artists/{artist_id}/messages/feed", headers=headers)
    assert feed.status_code == 200
    assert "messages" in feed.json()

    chat = client.post(
        f"/artists/{artist_id}/messages/chat",
        json={"message": "why was my youtube lower"},
        headers=headers,
    )
    assert chat.status_code == 200
    assert "answer" in chat.json()

    story = client.post(
        f"/artists/{artist_id}/messages/weekly-story",
        json={
            "total_recovered": 1200.0,
            "total_recoverable": 8500.0,
            "new_anomalies": 2,
            "claims_progressed": 1,
            "deposits": [{"amount": 250.0, "payer": "ASCAP"}],
            "currency": "USD",
        },
        headers=headers,
    )
    assert story.status_code == 200
    assert story.json()["artist_id"] == artist_id


def test_class_action_admin_endpoints_require_admin_auth():
    unauthorized = client.get("/admin/class-action/signals")
    assert unauthorized.status_code == 401

    headers = _admin_headers()
    aggregate = client.post("/admin/class-action/aggregate", headers=headers)
    assert aggregate.status_code == 200
    assert "signals" in aggregate.json()

    signals = client.get("/admin/class-action/signals", headers=headers)
    assert signals.status_code == 200
    assert "count" in signals.json()


def test_recovery_autopilot_endpoint_runs_agents():
    artist_id = _create_artist("Recovery Autopilot Artist")
    resp = client.post(
        f"/artists/{artist_id}/recovery/auto",
        json={"include_rights_registration": True},
        headers=_artist_headers(artist_id),
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["artist_id"] == artist_id
    assert "autopilot" in payload
    assert "executed_agents" in payload["autopilot"]


def test_onboarding_auto_endpoint_bootstraps_status():
    artist_id = _create_artist("Onboarding Auto Artist")
    resp = client.post(
        f"/artists/{artist_id}/onboarding/auto",
        json={"run_due_sync_jobs_now": False},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["artist_id"] == artist_id
    assert payload["status"] in {"ONBOARDED", "ACTIVE"}
    assert "progress" in payload
