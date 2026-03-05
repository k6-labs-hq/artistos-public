from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.ml.contract_term_extractor import ContractTermExtractor
from XR7.ml.expected_payout_simulator import ExpectedPayoutSimulator
from XR7.ml.recovery_utility_ranker import RecoveryUtilityRanker
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity
from XR7.models.artist import Artist
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Intelligence Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    aid = artist.id
    db.close()
    return aid


class TestIntelligenceEndpoints:
    def test_calibration_health_endpoint(self):
        artist_id = _create_artist()
        for _ in range(2):
            client.post(
                f"/artists/{artist_id}/intelligence/feedback",
                json={"outcome": "RECOVERED", "recovered_amount": 50.0},
            )
        client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={"outcome": "DISMISSED"},
        )

        resp = client.get(f"/artists/{artist_id}/intelligence/calibration")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall" in data
        assert "by_subtype" in data
        assert data["overall"]["sample_count"] >= 3

    def test_ingest_ledger_entries(self):
        artist_id = _create_artist()
        payload = {
            "entries": [
                {
                    "source": "Spotify",
                    "record_type": "EVENT",
                    "source_file": "spotify_2025_01.csv",
                    "source_row": 42,
                    "work_id": "USABC1234567",
                    "event_type": "STREAM",
                    "quantity": 1000,
                    "rate": 0.0035,
                    "expected_amount": 3.5,
                    "received_amount": 2.4,
                    "currency": "USD",
                    "territory": "US",
                }
            ]
        }
        resp = client.post(f"/artists/{artist_id}/intelligence/ledger/ingest", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["created_count"] == 1
        assert data["entries"][0]["source_file"] == "spotify_2025_01.csv"

    def test_extract_contract_terms(self):
        artist_id = _create_artist()
        payload = {
            "contract_text": "Royalty shall be 18% worldwide with recoupment reserve provisions.",
            "effective_start": "2025-01-01",
        }
        resp = client.post(f"/artists/{artist_id}/intelligence/contracts/extract", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["term_count"] >= 2
        keys = [t["term_key"] for t in data["terms"]]
        assert "royalty_rate_percent" in keys

    def test_extract_contract_terms_upload_txt(self):
        artist_id = _create_artist()
        text = b"Royalty is 17% worldwide with reserve recoupment terms."
        resp = client.post(
            f"/artists/{artist_id}/intelligence/contracts/extract-upload",
            files={"file": ("contract.txt", io.BytesIO(text), "text/plain")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["term_count"] >= 2
        assert data["extraction_method"] in ("plain_text_decode", "pdf_text_extraction", "image_ocr")

    def test_simulate_expected_payout(self):
        artist_id = _create_artist()
        payload = {
            "usage_rows": [
                {
                    "source": "Spotify",
                    "work_id": "w1",
                    "quantity": 1000,
                    "rate": 0.004,
                    "withholding_rate": 0.1,
                    "fx_rate": 1.0,
                    "territory": "US",
                },
                {
                    "source": "Apple Music",
                    "work_id": "w2",
                    "quantity": 500,
                    "rate": 0.006,
                    "withholding_rate": 0.0,
                    "fx_rate": 1.0,
                    "territory": "GB",
                },
            ],
            "received_amount": 5.5,
        }
        resp = client.post(f"/artists/{artist_id}/intelligence/simulate-expected-payout", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # (1000*0.004)*(1-0.1) + (500*0.006) = 3.6 + 3.0 = 6.6
        assert abs(data["expected_total"] - 6.6) < 1e-9
        assert abs(data["variance"] - 1.1) < 1e-9
        assert abs(data["withheld_native_total"] - 0.4) < 1e-9

    def test_create_feedback(self):
        artist_id = _create_artist()
        payload = {
            "outcome": "RECOVERED",
            "recovered_amount": 321.99,
            "reason_code": "SETTLEMENT_RECEIVED",
            "analyst_note": "Recovered via distributor escalation.",
        }
        resp = client.post(f"/artists/{artist_id}/intelligence/feedback", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["outcome"] == "RECOVERED"
        assert abs(data["recovered_amount"] - 321.99) < 1e-9

    def test_rank_utility(self):
        artist_id = _create_artist()

        # Seed enough feedback rows to activate calibration blend.
        for _ in range(4):
            client.post(
                f"/artists/{artist_id}/intelligence/feedback",
                json={"outcome": "RECOVERED", "recovered_amount": 100.0},
            )
        client.post(
            f"/artists/{artist_id}/intelligence/feedback",
            json={"outcome": "DISMISSED"},
        )

        payload = {
            "items": [
                {"id": "a", "estimated_recoverable": 1000, "success_probability": 0.7, "effort_hours": 2},
                {"id": "b", "estimated_recoverable": 300, "success_probability": 0.9, "effort_hours": 1},
            ],
            "analyst_hourly_cost": 100,
        }
        resp = client.post(f"/artists/{artist_id}/intelligence/rank-utility", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert data["ranked"][0]["id"] == "a"
        assert data["ranked"][0]["utility_rank"] == 1
        assert "calibration" in data
        assert data["calibration"]["sample_count"] >= 5

    def test_rank_utility_uses_subtype_scope_when_available(self):
        artist_id = _create_artist()

        db = _TestSession()
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING_MECHANICAL",
            severity=AnomalySeverity.HIGH,
            confidence_score=0.9,
            description="Mechanical leakage",
        )
        db.add(anomaly)
        db.commit()
        anomaly_id = anomaly.id
        db.close()

        for _ in range(3):
            client.post(
                f"/artists/{artist_id}/intelligence/feedback",
                json={"anomaly_id": anomaly_id, "outcome": "RECOVERED", "recovered_amount": 100.0},
            )

        resp = client.post(
            f"/artists/{artist_id}/intelligence/rank-utility",
            json={
                "items": [
                    {
                        "id": "m1",
                        "subtype": "MISSING_MECHANICAL",
                        "estimated_recoverable": 500,
                        "success_probability": 0.5,
                        "effort_hours": 1,
                    }
                ]
            },
        )
        assert resp.status_code == 200
        ranked_item = resp.json()["ranked"][0]
        assert ranked_item["calibration"]["scope"] == "subtype:MISSING_MECHANICAL"
        assert ranked_item["calibration"]["sufficient_samples"] is True


class TestIntelligenceModelClasses:
    def test_contract_term_extractor(self):
        extractor = ContractTermExtractor()
        terms = extractor.extract("Artist receives 20% worldwide. Recoupment applies.")
        keys = {t["term_key"] for t in terms}
        assert "royalty_rate_percent" in keys
        assert "territory" in keys
        assert "recoupment_clause" in keys

    def test_expected_payout_simulator(self):
        sim = ExpectedPayoutSimulator()
        result = sim.simulate(
            usage_rows=[{"quantity": 1000, "rate": 0.005, "withholding_rate": 0.1, "fx_rate": 1.0}],
            received_amount=3.0,
        )
        assert abs(result["expected_total"] - 4.5) < 1e-9
        assert abs(result["variance"] - 1.5) < 1e-9
        assert abs(result["withheld_native_total"] - 0.5) < 1e-9

    def test_recovery_utility_ranker(self):
        ranker = RecoveryUtilityRanker()
        ranked = ranker.rank([
            {"id": "high", "estimated_recoverable": 2000, "success_probability": 0.8, "effort_hours": 2},
            {"id": "low", "estimated_recoverable": 200, "success_probability": 0.7, "effort_hours": 1},
        ])
        assert ranked[0]["id"] == "high"
        assert ranked[0]["utility_rank"] == 1
