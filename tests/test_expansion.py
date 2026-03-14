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
from XR7.models.payment import Payment, PaymentType
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Expansion Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()

    resp = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert resp.status_code == 201
    return artist_id


def _actor_headers(email: str, role: str) -> dict[str, str]:
    return {
        "X-Actor-Email": email,
        "X-Actor-Role": role,
    }


def _bootstrap_artist_member(artist_id: str, email: str = "owner@example.com") -> dict[str, str]:
    resp = client.post(
        f"/artists/{artist_id}/team/members",
        json={"user_email": email, "role": "artist"},
    )
    assert resp.status_code == 201
    return _actor_headers(email, "artist")


def _seed_claim_with_integrity(artist_id: str) -> str:
    db = _TestSession()
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        confidence_score=0.9,
        estimated_recoverable=1100.0,
        created_at=datetime.now(timezone.utc),
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,
        evidence={
            "integrity": {
                "packet_hash": "packet-hash-1",
                "chain_hash": "chain-hash-1",
            }
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.add(claim)
    db.commit()
    claim_id = claim.id
    db.close()
    return claim_id


def test_summary_report_csv_and_pdf_exports():
    artist_id = _create_artist()
    db = _TestSession()

    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        confidence_score=0.9,
        estimated_recoverable=1500.0,
        created_at=datetime.now(timezone.utc),
    )
    payment = Payment(
        id=str(uuid.uuid4()),
        payment_type=PaymentType.ROYALTY,
        artist_id=artist_id,
        amount=300.0,
        currency="USD",
        source="Test Source",
        received_at=datetime.now(timezone.utc),
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.add(payment)
    db.add(claim)
    db.commit()
    db.close()

    csv_resp = client.get(f"/artists/{artist_id}/reports/summary", params={"format": "csv"})
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    assert "metric,value" in csv_resp.text

    pdf_resp = client.get(f"/artists/{artist_id}/reports/summary", params={"format": "pdf"})
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF-")


def test_batch_upload_endpoint_processes_multiple_csvs():
    artist_id = _create_artist()

    csv_one = (
        "Month,Store,Country,Title,ISRC,Quantity,Earnings\n"
        "2024-01,Spotify,US,Song A,USAAA1234567,1000,4.00\n"
    ).encode("utf-8")
    csv_two = (
        "Month,Store,Country,Title,ISRC,Quantity,Earnings\n"
        "2024-02,Apple Music,US,Song B,USBBB1234567,2000,7.50\n"
    ).encode("utf-8")

    files = [
        ("files", ("jan.csv", io.BytesIO(csv_one), "text/csv")),
        ("files", ("feb.csv", io.BytesIO(csv_two), "text/csv")),
    ]

    resp = client.post(f"/artists/{artist_id}/statements/upload-batch", files=files)
    assert resp.status_code == 200
    body = resp.json()
    assert body["requested"] == 2
    assert body["processed_count"] == 2
    assert body["failed_count"] == 0


def test_dashboard_charts_and_team_access_endpoints():
    artist_id = _create_artist()

    create_owner = client.post(
        f"/artists/{artist_id}/team/members",
        json={"user_email": "owner@example.com", "role": "artist"},
    )
    assert create_owner.status_code == 201
    owner_headers = _actor_headers("owner@example.com", "artist")

    charts_resp = client.get(f"/artists/{artist_id}/dashboard/charts", headers=owner_headers)
    assert charts_resp.status_code == 200
    chart_body = charts_resp.json()
    assert chart_body["artist_id"] == artist_id
    assert "leakage_by_month" in chart_body
    assert "recovered_by_month" in chart_body
    assert "forecast_confidence_bands" in chart_body

    create_member = client.post(
        f"/artists/{artist_id}/team/members",
        json={"user_email": "manager@example.com", "role": "manager"},
        headers=owner_headers,
    )
    assert create_member.status_code == 201
    member_id = create_member.json()["id"]

    list_members = client.get(f"/artists/{artist_id}/team/members", headers=owner_headers)
    assert list_members.status_code == 200
    assert any(m["id"] == member_id for m in list_members.json())

    delete_member = client.delete(
        f"/artists/{artist_id}/team/members/{member_id}",
        headers=owner_headers,
    )
    assert delete_member.status_code == 200
    assert delete_member.json()["deleted"] is True


def test_rbac_enforces_artist_only_team_mutation():
    artist_id = _create_artist()
    owner_headers = _bootstrap_artist_member(artist_id)

    manager_create = client.post(
        f"/artists/{artist_id}/team/members",
        json={"user_email": "manager@example.com", "role": "manager"},
        headers=owner_headers,
    )
    assert manager_create.status_code == 201
    manager_id = manager_create.json()["id"]

    manager_headers = _actor_headers("manager@example.com", "manager")
    forbidden_delete = client.delete(
        f"/artists/{artist_id}/team/members/{manager_id}",
        headers=manager_headers,
    )
    assert forbidden_delete.status_code == 403

    allowed_delete = client.delete(
        f"/artists/{artist_id}/team/members/{manager_id}",
        headers=owner_headers,
    )
    assert allowed_delete.status_code == 200


def test_oauth_connector_flow_scope_refresh_and_multitenant_linking():
    artist_id = _create_artist()
    owner_headers = _bootstrap_artist_member(artist_id)

    session_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session",
        json={
            "provider": "spotify",
            "redirect_uri": "https://example.com/callback",
            "scopes": ["catalog.read", "payments.read"],
            "tenant_id": "label-a",
        },
        headers=owner_headers,
    )
    assert session_resp.status_code == 200
    session_body = session_resp.json()
    session_id = session_body["session_id"]
    oauth_state = session_body["oauth_state"]

    missing_scope_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session/{session_id}/exchange",
        json={
            "state": oauth_state,
            "code": "code-1",
            "external_account_id": "acct-123",
            "tenant_id": "label-a",
            "granted_scopes": ["catalog.read"],
        },
        headers=owner_headers,
    )
    assert missing_scope_resp.status_code == 400

    exchange_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session/{session_id}/exchange",
        json={
            "state": oauth_state,
            "code": "code-1",
            "external_account_id": "acct-123",
            "tenant_id": "label-a",
            "granted_scopes": ["catalog.read", "payments.read"],
            "expires_in_seconds": 0,
            "display_name": "Primary Label Account",
        },
        headers=owner_headers,
    )
    assert exchange_resp.status_code == 200
    account_id = exchange_resp.json()["account"]["id"]

    second_session_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session",
        json={
            "provider": "spotify",
            "redirect_uri": "https://example.com/callback",
            "scopes": ["catalog.read"],
            "tenant_id": "label-b",
        },
        headers=owner_headers,
    )
    assert second_session_resp.status_code == 200
    second_session = second_session_resp.json()

    second_exchange_resp = client.post(
        f"/artists/{artist_id}/connect/oauth-session/{second_session['session_id']}/exchange",
        json={
            "state": second_session["oauth_state"],
            "code": "code-2",
            "external_account_id": "acct-456",
            "tenant_id": "label-b",
            "granted_scopes": ["catalog.read"],
        },
        headers=owner_headers,
    )
    assert second_exchange_resp.status_code == 200

    list_resp = client.get(f"/artists/{artist_id}/connect/accounts", headers=owner_headers)
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert listed["count"] == 2
    assert {a["tenant_id"] for a in listed["accounts"]} == {"label-a", "label-b"}

    list_tenant_a = client.get(
        f"/artists/{artist_id}/connect/accounts",
        params={"tenant_id": "label-a"},
        headers=owner_headers,
    )
    assert list_tenant_a.status_code == 200
    assert list_tenant_a.json()["count"] == 1

    refresh_resp = client.post(
        f"/artists/{artist_id}/connect/accounts/{account_id}/refresh",
        json={"force": True, "expires_in_seconds": 7200, "rotate_refresh_token": True},
        headers=owner_headers,
    )
    assert refresh_resp.status_code == 200
    assert refresh_resp.json()["refreshed"] is True

    disconnect_resp = client.delete(
        f"/artists/{artist_id}/connect/accounts/{account_id}",
        headers=owner_headers,
    )
    assert disconnect_resp.status_code == 200
    assert disconnect_resp.json()["disconnected"] is True

    after_disconnect = client.get(f"/artists/{artist_id}/connect/accounts", headers=owner_headers)
    assert after_disconnect.status_code == 200
    assert after_disconnect.json()["count"] == 1

    include_inactive_resp = client.get(
        f"/artists/{artist_id}/connect/accounts",
        params={"include_inactive": "true"},
        headers=owner_headers,
    )
    assert include_inactive_resp.status_code == 200
    assert include_inactive_resp.json()["count"] == 2


def test_expansion_endpoints_smoke_matrix():
    artist_id = _create_artist()
    owner_headers = _bootstrap_artist_member(artist_id)
    claim_id = _seed_claim_with_integrity(artist_id)

    # Required data for analytics/report endpoints.
    db = _TestSession()
    db.add(
        Payment(
            id=str(uuid.uuid4()),
            payment_type=PaymentType.ROYALTY,
            artist_id=artist_id,
            amount=250.0,
            currency="USD",
            source="Smoke",
            received_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    db.close()

    # Artist-scoped endpoints (protected by team access once team exists).
    protected_calls = [
        ("get", f"/artists/{artist_id}/notifications/preferences", None),
        (
            "put",
            f"/artists/{artist_id}/notifications/preferences",
            {
                "email": "owner@example.com",
                "notify_anomaly_detected": True,
                "notify_urgent_sol": True,
                "notify_deposit_received": True,
                "notify_claim_advanced": True,
            },
        ),
        (
            "post",
            f"/artists/{artist_id}/notifications/dispatch",
            {"event_key": "anomaly_detected", "title": "Test", "body": "Smoke check"},
        ),
        ("post", f"/artists/{artist_id}/notifications/urgent-sol-check", None),
        ("get", f"/artists/{artist_id}/dashboard/charts", None),
        ("get", f"/artists/{artist_id}/reports/summary?format=json", None),
        ("get", f"/artists/{artist_id}/reports/summary?format=csv", None),
        ("get", f"/artists/{artist_id}/reports/summary?format=pdf", None),
        (
            "post",
            f"/artists/{artist_id}/connect/oauth-session",
            {"provider": "spotify", "redirect_uri": "https://example.com/callback"},
        ),
        ("get", f"/artists/{artist_id}/connect/fallbacks", None),
        ("get", f"/artists/{artist_id}/team/members", None),
        ("get", f"/artists/{artist_id}/recovery/benchmark-percentiles", None),
        (
            "post",
            f"/artists/{artist_id}/claims/templates",
            {
                "subtype": "MISSING_PAYMENT",
                "counterparty_name": "Label Co",
                "amount_claimed": 1200.0,
            },
        ),
        (
            "post",
            f"/artists/{artist_id}/intelligence/withholding-estimate",
            {
                "gross_amount": 1000.0,
                "source_currency": "USD",
                "payout_currency": "EUR",
                "fx_rate": 0.92,
                "withholding_rate": 0.1,
            },
        ),
        (
            "post",
            f"/artists/{artist_id}/ml/predict-recoverable",
            {"catalog_size": 12, "genre": "pop"},
        ),
        ("get", f"/artists/{artist_id}/recovery/audit-demand-letter", None),
    ]

    for method, url, body in protected_calls:
        req = getattr(client, method)
        if body is None:
            response = req(url, headers=owner_headers)
        else:
            response = req(url, json=body, headers=owner_headers)
        assert response.status_code < 400, f"{method.upper()} {url} failed: {response.text}"

    # Claim-level expansion endpoint.
    anchor_resp = client.post(f"/claims/{claim_id}/evidence/anchor")
    assert anchor_resp.status_code == 200

    # Public/non-artist scoped expansion endpoints.
    public_calls = [
        ("get", "/stats/public/recovery"),
        ("get", "/education/guides"),
        ("get", "/education/guides/sol-101"),
        ("get", "/b2b/portfolio/test-org"),
        ("get", "/partnerships/targets"),
    ]
    for method, url in public_calls:
        response = getattr(client, method)(url)
        assert response.status_code < 400, f"{method.upper()} {url} failed: {response.text}"
