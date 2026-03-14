from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.oauth_connector import ConnectorAccountLink, ConnectorAccountStatus
from XR7.models.work import Work, WorkType
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Onboarding Test Artist",
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


def _seed_claim_and_work(artist_id: str) -> str:
    db = _TestSession()
    work = Work(
        id=str(uuid.uuid4()),
        title="Test Work",
        isrc="USXXX1234567",
        iswc="T-000.000.001-0",
        work_type=WorkType.RECORDING,
        artist_id=artist_id,
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=str(uuid.uuid4()),
        claim_type="ROYALTY",
        status=ClaimStatus.IDENTIFIED,
        recovered_amount=1234.56,
        evidence={"proof": "test"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(work)
    db.add(claim)
    db.commit()
    cid = claim.id
    db.close()
    return cid


def test_permissions_dashboard_and_fetchers_and_ingestion_pipeline():
    artist_id = _create_artist()

    db = _TestSession()
    db.add(
        ConnectorAccountLink(
            artist_id=artist_id,
            provider="distributor",
            tenant_id="default",
            external_account_id="acct-1",
            granted_scopes="catalog.read usage.read",
            access_token="atk",
            refresh_token="rtk",
            token_type="Bearer",
            status=ConnectorAccountStatus.ACTIVE,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    db.close()

    perm_resp = client.get(f"/artists/{artist_id}/connect/permissions-dashboard")
    assert perm_resp.status_code == 200
    perm = perm_resp.json()
    assert "connected_accounts" in perm
    assert "missing_connections" in perm

    fetch_resp = client.post(f"/artists/{artist_id}/fetchers/distributor")
    assert fetch_resp.status_code == 200
    fetch_body = fetch_resp.json()
    assert "normalized_universal_events" in fetch_body

    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    upload_resp = client.post(
        f"/artists/{artist_id}/ingestion/upload-any",
        files=[("files", ("statement.csv", io.BytesIO(csv_bytes), "text/csv"))],
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["virus_scan_passed"] is True


def test_parser_missing_data_catalog_and_recovery_modules():
    artist_id = _create_artist()
    claim_id = _seed_claim_and_work(artist_id)

    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    parse_resp = client.post(
        f"/artists/{artist_id}/parsers/distributor",
        files={"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert parse_resp.status_code == 200
    assert parse_resp.json()["event_count"] >= 1

    missing_resp = client.get(f"/artists/{artist_id}/ingestion/missing-data")
    assert missing_resp.status_code == 200
    assert "prompt_user" in missing_resp.json()

    graph_resp = client.post(f"/artists/{artist_id}/catalog/graph/build")
    assert graph_resp.status_code == 200
    assert "nodes" in graph_resp.json()

    confirm_resp = client.post(
        f"/artists/{artist_id}/catalog/confirm",
        json={"work_id": "work-1", "ownership_confirmed": "confirmed"},
    )
    assert confirm_resp.status_code == 200

    infer_resp = client.post(f"/artists/{artist_id}/catalog/infer")
    assert infer_resp.status_code == 200
    assert "inferences" in infer_resp.json()

    variance_resp = client.post(
        f"/artists/{artist_id}/variance/scan",
        json={
            "rows": [
                {
                    "streams": 1000,
                    "payout": 1.0,
                    "expected_payout": 4.0,
                    "has_registration": False,
                    "reported_usage": 500,
                }
            ]
        },
    )
    assert variance_resp.status_code == 200
    assert variance_resp.json()["finding_count"] >= 1

    evidence_resp = client.post(f"/claims/{claim_id}/evidence/generate-audit")
    assert evidence_resp.status_code == 200
    assert "ledger_entry_hash" in evidence_resp.json()

    recovery_resp = client.post(f"/artists/{artist_id}/recovery/automate")
    assert recovery_resp.status_code == 200
    assert "submission_queue" in recovery_resp.json()

    ledger_resp = client.get(f"/artists/{artist_id}/ledger/immutable")
    assert ledger_resp.status_code == 200
    assert len(ledger_resp.json()) >= 2


def test_strict_upload_validation_blocks_extension_magic_mismatch():
    artist_id = _create_artist()

    fake_zip = b"PK\x03\x04not-a-csv"
    resp = client.post(
        f"/artists/{artist_id}/ingestion/upload-any",
        files=[("files", ("looks_like.csv", io.BytesIO(fake_zip), "text/csv"))],
    )
    assert resp.status_code == 422
    body = resp.json()["detail"]
    assert body["message"].startswith("Upload blocked")


def test_parser_plugin_registry_and_sync_job_lifecycle():
    artist_id = _create_artist()

    upsert = client.put(
        f"/artists/{artist_id}/parsers/plugins",
        json={
            "parser_type": "custom_partner",
            "plugin_name": "Partner Parser",
            "plugin_entrypoint": "XR7.plugins.partner:parse",
            "enabled": True,
        },
    )
    assert upsert.status_code == 200

    listed = client.get(f"/artists/{artist_id}/parsers/plugins")
    assert listed.status_code == 200
    assert any(p["parser_type"] == "custom_partner" for p in listed.json())

    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    parse_custom = client.post(
        f"/artists/{artist_id}/parsers/custom_partner",
        files={"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert parse_custom.status_code == 200
    assert parse_custom.json()["event_count"] >= 1

    job_create = client.post(
        f"/artists/{artist_id}/sync/jobs",
        json={"integration": "distributor", "max_attempts": 2, "run_async": False},
    )
    assert job_create.status_code == 200
    job_id = job_create.json()["id"]
    assert job_create.json()["status"] == "PENDING"

    run_now = client.post(f"/artists/{artist_id}/sync/jobs/{job_id}/run")
    assert run_now.status_code == 200
    assert run_now.json()["status"] in {"COMPLETED", "RETRYING", "FAILED"}

    read_job = client.get(f"/artists/{artist_id}/sync/jobs/{job_id}")
    assert read_job.status_code == 200
    assert read_job.json()["attempts"] >= 1

    listed_jobs = client.get(f"/artists/{artist_id}/sync/jobs")
    assert listed_jobs.status_code == 200
    assert any(j["id"] == job_id for j in listed_jobs.json())
