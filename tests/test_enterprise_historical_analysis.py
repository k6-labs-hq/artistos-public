from __future__ import annotations

import io

from fastapi.testclient import TestClient

from XR7.api.app import app


client = TestClient(app)


def test_enterprise_historical_analyze_json_payload():
    resp = client.post(
        "/enterprise/historical/analyze",
        json={
            "organization_name": "WME",
            "entity_type": "Talent Agency",
            "records": [
                {
                    "client": "Client Music",
                    "vertical": "MUSIC",
                    "estimated_royalty_gap": 100000,
                    "estimated_unpaid_sync": 25000,
                    "sol_risk": "high",
                },
                {
                    "client": "Client TV",
                    "vertical": "TV_FILM",
                    "estimated_missing": 90000,
                    "estimated_underpayment": 15000,
                    "estimated_backend_missing": 10000,
                    "sol_risk": "medium",
                },
            ],
        },
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["organization_name"] == "WME"
    assert payload["roster_size"] == 2
    assert payload["total_estimated_recoverable"] > 0
    assert payload["by_vertical"]["MUSIC"]["clients"] == 1
    assert payload["by_vertical"]["TV_FILM"]["clients"] == 1


def test_enterprise_historical_analyze_file_csv():
    csv_text = "\n".join(
        [
            "client,vertical,estimated_royalty_gap,estimated_missing,estimated_underpayment,estimated_backend_missing,sol_risk",
            "Client A,MUSIC,80000,0,0,0,high",
            "Client B,TV_FILM,0,60000,10000,5000,medium",
        ]
    )
    resp = client.post(
        "/enterprise/historical/analyze-file",
        data={"organization_name": "WME", "entity_type": "Talent Agency"},
        files={"file": ("wme.csv", io.BytesIO(csv_text.encode("utf-8")), "text/csv")},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["roster_size"] == 2
    assert len(payload["top_25_clients"]) == 2
    assert payload["sol_risk"]["high"] == 1
    assert payload["sol_risk"]["medium"] == 1
