from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.contract import Contract, ContractType
from XR7.models.event import Event, EventType
from XR7.models.payment import Payment, PaymentType
from XR7.models.statement import Statement
from XR7.models.work import Work, WorkType
from tests.conftest import TestSession as _TestSession


client = TestClient(app)


def _seed_recovery_portfolio(artist_id: str = "artist-portfolio-1") -> dict[str, str]:
    db = _TestSession()
    artist = Artist(id=artist_id, name="Portfolio Artist", email="portfolio@example.com")
    db.add(artist)

    work = Work(
        id=f"work-{artist_id}",
        artist_id=artist_id,
        title="Portfolio Track",
        isrc="US-AAA-26-77777",
        iswc="T-123.456.789-0",
        work_type=WorkType.RECORDING,
    )
    db.add(work)

    anomaly = Anomaly(
        id=f"anom-{artist_id}",
        artist_id=artist_id,
        category=AnomalyCategory.ROYALTY,
        subtype="rate_drift",
        severity=AnomalySeverity.HIGH,
        expected_amount=1200.0,
        actual_amount=600.0,
        estimated_recoverable=600.0,
        confidence_score=0.78,
        status=AnomalyStatus.OPEN,
        territory="US",
    )
    db.add(anomaly)

    claim = Claim(
        id=f"claim-{artist_id}",
        artist_id=artist_id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.SUBMITTED,
        recovered_amount=420.0,
        currency="USD",
        evidence={
            "legal_support": {"contract_basis": [{"counterparty": "Spotify"}]},
            "proof": {"ledger_evidence": [{"id": "l1"}]},
            "reconciliation": {"discrepancy_amount": 5.0},
            "integrity": {
                "packet_hash": "abc",
                "chain_hash": "def",
                "signature": "sig",
                "signature_algorithm": "hmac-sha256",
            },
            "metadata": {"packet_version": "1.1", "revision": 1},
        },
    )
    db.add(claim)

    contract = Contract(
        id=f"contract-{artist_id}",
        artist_id=artist_id,
        contract_type=ContractType.LABEL,
        counterparty="Spotify",
        territory="US",
        terms={"artist_split": 0.7, "rate": 0.004},
    )
    db.add(contract)

    event = Event(
        id=f"event-{artist_id}",
        event_type=EventType.STREAM,
        work_id=work.id,
        artist_id=artist_id,
        platform="Spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        quantity=1000,
        unit_value=0.003,
        currency="USD",
    )
    db.add(event)

    db.add(
        Payment(
            id=f"pay-royalty-{artist_id}",
            payment_type=PaymentType.ROYALTY,
            artist_id=artist_id,
            amount=600.0,
            currency="USD",
            source="Spotify",
            received_at=datetime.now(timezone.utc),
        )
    )
    db.add(
        Payment(
            id=f"pay-payout-{artist_id}",
            payment_type=PaymentType.PAYOUT,
            artist_id=artist_id,
            amount=210.0,
            currency="USD",
            source="Trolley",
            received_at=datetime.now(timezone.utc),
        )
    )

    db.add(
        Statement(
            id=f"statement-{artist_id}",
            artist_id=artist_id,
            filename="spotify_statement.csv",
            file_hash="hash-1",
            format_detected="spotify",
            row_count=10,
            events_created=1,
            payments_created=1,
            skipped_rows=0,
            status="PROCESSED",
        )
    )

    db.commit()
    claim_id = claim.id
    anomaly_id = anomaly.id
    db.close()
    return {"artist_id": artist_id, "claim_id": claim_id, "anomaly_id": anomaly_id}


def test_recovery_portfolio_endpoints_matrix():
    ids = _seed_recovery_portfolio("artist-portfolio-2")

    expected_value = client.get(f"/artists/{ids['artist_id']}/recovery/expected-value")
    assert expected_value.status_code == 200
    assert "confidence_interval" in expected_value.json()

    funnel = client.get(f"/artists/{ids['artist_id']}/recovery/funnel")
    assert funnel.status_code == 200
    assert "drop_off_points" in funnel.json()

    integrity = client.get(f"/artists/{ids['artist_id']}/catalog/integrity")
    assert integrity.status_code == 200
    assert "isrc_iswc_reconciliation" in integrity.json()

    advanced_benchmark = client.get(f"/artists/{ids['artist_id']}/recovery/rate-benchmark-advanced")
    assert advanced_benchmark.status_code == 200
    assert "dynamic_rate_curves" in advanced_benchmark.json()

    heatmap = client.get(f"/artists/{ids['artist_id']}/recovery/heatmap")
    assert heatmap.status_code == 200
    assert "leakage_by_platform" in heatmap.json()

    roi = client.get(f"/artists/{ids['artist_id']}/recovery/roi")
    assert roi.status_code == 200
    assert "roi" in roi.json()

    attribution = client.get(f"/artists/{ids['artist_id']}/recovery/attribution")
    assert attribution.status_code == 200
    assert "by_anomalies" in attribution.json()

    benchmarking = client.get(f"/artists/{ids['artist_id']}/benchmarking")
    assert benchmarking.status_code == 200
    assert "peer_percentiles" in benchmarking.json()

    playbook = client.get(f"/artists/{ids['artist_id']}/recovery/playbook")
    assert playbook.status_code == 200
    assert "recommended_actions" in playbook.json()

    fraud = client.post(f"/artists/{ids['artist_id']}/fraud-scan")
    assert fraud.status_code == 200
    assert "scan_summary" in fraud.json()

    reconstruct = client.post(f"/artists/{ids['artist_id']}/recovery/reconstruct-historical")
    assert reconstruct.status_code == 200
    assert "delta" in reconstruct.json()

    sla = client.get(f"/artists/{ids['artist_id']}/sla/status")
    assert sla.status_code == 200
    assert "sla_timers" in sla.json()


def test_claim_anomaly_payer_and_workspace_endpoints():
    ids = _seed_recovery_portfolio("artist-portfolio-3")

    anomaly_probability = client.get(f"/anomalies/{ids['anomaly_id']}/recovery-probability")
    assert anomaly_probability.status_code == 200
    assert "probability_of_recovery" in anomaly_probability.json()

    strength_explainer = client.get(f"/claims/{ids['claim_id']}/strength-explainer")
    assert strength_explainer.status_code == 200
    assert "contributing_factors" in strength_explainer.json()

    sla_prediction = client.get(f"/claims/{ids['claim_id']}/sla-prediction")
    assert sla_prediction.status_code == 200
    assert "expected_settlement_date" in sla_prediction.json()

    automation_plan = client.get(f"/claims/{ids['claim_id']}/automation-plan")
    assert automation_plan.status_code == 200
    assert "automated_next_steps" in automation_plan.json()

    optimized = client.get(f"/claims/{ids['claim_id']}/evidence/optimized")
    assert optimized.status_code == 200
    assert "payer_specific_formatting" in optimized.json()

    payer_behavior = client.get("/payers/spotify/behavior")
    assert payer_behavior.status_code == 200
    assert "acceptance_probability" in payer_behavior.json()

    payer_risk = client.get("/payers/spotify/risk")
    assert payer_risk.status_code == 200
    assert "risk_score" in payer_risk.json()

    headers = {"X-Workspace-Role": "manager"}
    ws_overview = client.get("/workspace/overview", headers=headers)
    assert ws_overview.status_code == 200

    ws_artists = client.get("/workspace/artists", headers=headers)
    assert ws_artists.status_code == 200

    ws_claims = client.get("/workspace/claims", headers=headers)
    assert ws_claims.status_code == 200

    ws_deadlines = client.get("/workspace/deadlines", headers=headers)
    assert ws_deadlines.status_code == 200

    dashboard = client.get(f"/artists/{ids['artist_id']}/dashboard")
    assert dashboard.status_code == 200
    assert "expected_recovery_value" in dashboard.json()
