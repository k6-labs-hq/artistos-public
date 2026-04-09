from __future__ import annotations

import io
import json
import zipfile

from fastapi.testclient import TestClient

from XR7.api.app import app

client = TestClient(app)


def _create_tvfilm_artist(name: str = "TV Film Talent") -> str:
    resp = client.post(
        "/artists/",
        json={
            "name": name,
            "role": "Actor",
            "primary_vertical": "TV_FILM",
            "tvfilm_role": "Actor",
        },
    )
    assert resp.status_code == 201
    return str(resp.json()["id"])


def _sample_statement_csv() -> bytes:
    rows = [
        "production_id,production_title,season_number,episode_number,role,union,market,distribution_window,platform,expected_amount,amount_paid",
        "prod-001,City Cases,1,1,Actor,SAG-AFTRA,US,Streaming,Netflix,12000,9000",
        "prod-001,City Cases,1,2,Actor,SAG-AFTRA,Foreign,Streaming,Netflix,10000,7000",
        "prod-002,Stunt Ops,2,3,Stunt Performer,SAG-AFTRA,US,Syndication,Hulu,8000,4000",
    ]
    return ("\n".join(rows) + "\n").encode("utf-8")


def test_tvfilm_ingestion_scan_claims_and_forecast_flow():
    artist_id = _create_tvfilm_artist("TV Film Full Flow")

    preview = client.post(
        "/tvfilm/ingestion/preview",
        files={"file": ("residuals.csv", io.BytesIO(_sample_statement_csv()), "text/csv")},
    )
    assert preview.status_code == 200
    assert preview.json()["rows_detected"] == 3

    commit = client.post(
        f"/tvfilm/artists/{artist_id}/ingestion/commit",
        files={"file": ("residuals.csv", io.BytesIO(_sample_statement_csv()), "text/csv")},
    )
    assert commit.status_code == 200
    assert commit.json()["rows_committed"] == 3

    scan = client.post(f"/tvfilm/artists/{artist_id}/anomalies/scan")
    assert scan.status_code == 200
    assert scan.json()["anomalies_created"] >= 1

    draft = client.post(
        f"/tvfilm/artists/{artist_id}/claims/draft",
        json={"union_template": "SAG-AFTRA"},
    )
    assert draft.status_code == 200
    assert draft.json()["claims_drafted"] >= 1

    forecast = client.post(f"/tvfilm/artists/{artist_id}/forecast", json={})
    assert forecast.status_code == 200
    payload = forecast.json()
    assert "30_day" in payload["forecast"]
    assert "180_day" in payload["forecast"]

    audit = client.get(f"/tvfilm/artists/{artist_id}/calculation-audit")
    assert audit.status_code == 200
    audit_payload = audit.json()
    assert audit_payload["rows_audited"] == 3
    assert audit_payload["calculation_profiles"][0]["recommended_template"] in {"SAG-AFTRA", "STUDIO_GENERIC"}


def test_tvfilm_enterprise_portfolio_analyze_and_fetch_job():
    analyze = client.post(
        "/tvfilm/enterprise/portfolio/analyze",
        json={
            "organization_name": "WME Demo Portfolio",
            "entity_type": "Talent Agency",
            "uploaded_filename": "roster.csv",
            "records": [
                {
                    "client": "Client A",
                    "role": "Actor",
                    "union": "SAG-AFTRA",
                    "platform": "Netflix",
                    "estimated_missing": 125000,
                    "estimated_underpayment": 32000,
                    "estimated_backend_missing": 18500,
                    "sol_risk": "high",
                },
                {
                    "client": "Client B",
                    "role": "Writer (TV/Film)",
                    "union": "WGA",
                    "platform": "Hulu",
                    "estimated_missing": 84000,
                    "estimated_underpayment": 12000,
                    "estimated_backend_missing": 7000,
                    "sol_risk": "medium",
                },
            ],
        },
    )
    assert analyze.status_code == 200
    job_id = analyze.json()["job_id"]

    fetch = client.get(f"/tvfilm/enterprise/portfolio/{job_id}")
    assert fetch.status_code == 200
    summary = fetch.json()["summary"]
    assert summary["roster_size"] == 2
    assert summary["total_residuals_missing"] > 0


def test_tvfilm_catalogs_roles_trust_and_agents_endpoint():
    artist_id = _create_tvfilm_artist("TV Film Agents")

    roles = client.get("/tvfilm/roles/options")
    assert roles.status_code == 200
    assert "Writer (TV/Film)" in roles.json()["role_options"]

    rules = client.get("/tvfilm/catalogs/anomaly-rules")
    assert rules.status_code == 200
    assert "MISSING_STREAMING_RESIDUALS" in rules.json()["flat_rule_list"]

    trust = client.post("/tvfilm/trust/explain", json={"role": "Showrunner", "agency_mode": True})
    assert trust.status_code == 200
    assert trust.json()["logo_state"] == "glowing"

    agents = client.post(f"/tvfilm/artists/{artist_id}/agents/run")
    assert agents.status_code == 200
    assert agents.json()["evidence_hash_count"] >= 1


def test_tvfilm_bulk_claim_draft_and_evidence_exports():
    artist_id = _create_tvfilm_artist("TV Film Export Flow")

    commit = client.post(
        f"/tvfilm/artists/{artist_id}/ingestion/commit",
        files={"file": ("residuals.csv", io.BytesIO(_sample_statement_csv()), "text/csv")},
    )
    assert commit.status_code == 200

    scan = client.post(f"/tvfilm/artists/{artist_id}/anomalies/scan")
    assert scan.status_code == 200
    assert scan.json()["anomalies_created"] >= 1

    bulk_draft = client.post(f"/tvfilm/artists/{artist_id}/claims/bulk-draft", json={})
    assert bulk_draft.status_code == 200
    drafted = bulk_draft.json()
    assert drafted["claims_drafted"] >= 1

    claim_id = drafted["drafts"][0]["claim_id"]

    json_export = client.get(f"/tvfilm/claims/{claim_id}/evidence/export?format=json")
    assert json_export.status_code == 200
    packet = json_export.json()
    assert packet["packet_type"] == "TV_FILM_EVIDENCE"
    assert packet["claim"]["claim_id"] == claim_id

    pdf_export = client.get(f"/tvfilm/claims/{claim_id}/evidence/export?format=pdf")
    assert pdf_export.status_code == 200
    assert pdf_export.headers["content-type"].startswith("application/pdf")
    assert pdf_export.content.startswith(b"%PDF-")

    zip_export = client.get(f"/tvfilm/claims/{claim_id}/evidence/export?format=zip")
    assert zip_export.status_code == 200
    assert zip_export.headers["content-type"].startswith("application/zip")
    claim_zip = zipfile.ZipFile(io.BytesIO(zip_export.content))
    assert "tvfilm_evidence_packet.json" in claim_zip.namelist()
    assert "tvfilm_evidence_packet.pdf" in claim_zip.namelist()

    bulk_zip_export = client.post(
        f"/tvfilm/artists/{artist_id}/claims/bulk-export",
        json={"claim_ids": [draft["claim_id"] for draft in drafted["drafts"]]},
    )
    assert bulk_zip_export.status_code == 200
    assert bulk_zip_export.headers["content-type"].startswith("application/zip")
    bulk_zip = zipfile.ZipFile(io.BytesIO(bulk_zip_export.content))
    assert "manifest.json" in bulk_zip.namelist()
    manifest = json.loads(bulk_zip.read("manifest.json").decode("utf-8"))
    assert manifest["artifact_count"] == drafted["claims_drafted"]
