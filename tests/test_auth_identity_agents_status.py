from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.work import Work, WorkType
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _seed_artist_with_catalog() -> tuple[str, str]:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Nova Sky",
        email="nova@example.com",
        ipi_number="123456789",
        stage_names=["NOVA SKY", "Nova"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.add(
        Work(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            title="Signal Fire",
            isrc="USABC1234567",
            iswc="T-123.456.789-0",
            work_type=WorkType.RECORDING,
        )
    )
    db.commit()
    aid = artist.id
    email = artist.email or ""
    db.close()
    return aid, email


def _artist_auth_headers(artist_id: str, email: str) -> dict[str, str]:
    login = client.post("/auth/login/artist", json={"artist_id": artist_id, "email": email})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_artist_jwt_login_and_auth_me():
    artist_id, email = _seed_artist_with_catalog()

    login = client.post("/auth/login/artist", json={"artist_id": artist_id, "email": email})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    payload = me.json()
    assert payload["artist_id"] == artist_id
    assert payload["role"] == "artist"


def test_identity_auto_match_persistence_and_audit():
    artist_id, email = _seed_artist_with_catalog()
    headers = _artist_auth_headers(artist_id, email)

    match = client.post(
        f"/artists/{artist_id}/identity/auto-match",
        json={
            "statement_signals": {
                "artist_name": "NOVA SKY",
                "pro_writer_id": "123456789",
                "distributor_list": ["nova"],
                "isrcs": ["USABC1234567"],
                "iswcs": ["T-123.456.789-0"],
                "upcs": ["123456789012"],
            }
        },
        headers=headers,
    )
    assert match.status_code == 200
    body = match.json()
    assert body["artist_id"] == artist_id
    assert body["confidence_score"] >= 0.9
    assert body["decision_status"] == "AUTO_ACCEPTED"

    audit = client.get(f"/artists/{artist_id}/identity/matches/{body['id']}/audit", headers=headers)
    assert audit.status_code == 200
    assert len(audit.json()["audit"]) >= 1


def test_agents_status_endpoint_contract_shape():
    artist_id, email = _seed_artist_with_catalog()
    headers = _artist_auth_headers(artist_id, email)

    response = client.get(f"/artists/{artist_id}/agents/status", headers=headers)
    assert response.status_code == 200
    payload = response.json()

    for key in [
        "agent_orchestra_status",
        "onboarding_progress",
        "comfort_messages",
        "portal_guidance",
        "fast_track_claim",
        "expected_earnings",
        "public_profile",
        "readiness_score",
        "ugc_opportunities",
        "catalog_profile",
        "split_conflicts",
        "registration_actions",
        "follow_up_actions",
    ]:
        assert key in payload


def test_create_claim_from_anomaly_endpoint():
    artist_id, email = _seed_artist_with_catalog()
    headers = _artist_auth_headers(artist_id, email)

    db = _TestSession()
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="UNPAID_PERIOD",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        estimated_recoverable=4200.0,
        confidence_score=0.93,
        territory="US",
        description="Unpaid monthly statement",
        created_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)
    db.commit()
    anomaly_id = anomaly.id
    db.close()

    created = client.post(
        f"/artists/{artist_id}/claims",
        json={"anomaly_id": anomaly_id, "claim_type": "RECOVERY"},
        headers=headers,
    )
    assert created.status_code == 201
    claim = created.json()
    assert claim["artist_id"] == artist_id
    assert claim["anomaly_id"] == anomaly_id
    assert claim["status"] == "IDENTIFIED"

    evidence = client.get(f"/claims/{claim['id']}/evidence", headers=headers)
    assert evidence.status_code == 200
    assert "integrity" in evidence.json()
