from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.contract import Contract, ContractType
from XR7.models.event import Event, EventType
from XR7.models.evidence_anchor import EvidenceAnchor
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.notification_preference import NotificationPreference
from XR7.models.oauth_connector import (
    ConnectorAccountLink,  # noqa: F401 - ensure table registration
)
from XR7.models.payment import Payment, PaymentType
from XR7.models.work import Work, WorkType

client = TestClient(app)


def _seed_artist_stack(artist_id: str = "artist-intel-ext") -> dict:
    db = _TestSession()

    artist = Artist(id=artist_id, name="Extension Artist", email="artist@example.com")
    db.add(artist)

    anomaly = Anomaly(
        id=f"anom-{artist_id}",
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="spotify_shortfall",
        severity=AnomalySeverity.HIGH,
        expected_amount=1200.0,
        actual_amount=700.0,
        estimated_recoverable=500.0,
        confidence_score=0.8,
        status=AnomalyStatus.OPEN,
        territory="US",
        created_at=datetime.now(timezone.utc),
    )
    db.add(anomaly)

    claim = Claim(
        id=f"claim-{artist_id}",
        artist_id=artist.id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.SUBMITTED,
        recovered_amount=450.0,
        currency="USD",
        evidence={
            "metadata": {"packet_version": "1.1", "revision": 2},
            "proof": {
                "ledger_evidence": [{"ledger_entry_id": "le1"}, {"ledger_entry_id": "le2"}],
            },
            "legal_support": {
                "contract_basis": [{"counterparty": "DistroKid"}],
                "source_citations": [{"source_file": "statement.csv", "source_row": 12}],
            },
            "reconciliation": {"discrepancy_amount": 12.5},
            "integrity": {
                "packet_hash": "abc",
                "chain_hash": "def",
                "signature": "sig",
                "signature_algorithm": "hmac-sha256",
            },
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(claim)

    db.add(
        CalibrationSnapshot(
            artist_id=artist.id,
            scope_type="subtype",
            scope_key="spotify_shortfall",
            posterior_mean=0.74,
            lower_credible=0.61,
            upper_credible=0.84,
            sample_count=20,
            success_count=14,
            failure_count=6,
            alpha=16,
            beta=8,
        )
    )

    db.add(
        EvidenceAnchor(
            claim_id=claim.id,
            packet_hash="abc",
            chain_hash="def",
            anchor_provider="INTERNAL_IMMUTABLE_LOG",
            anchor_reference="anchor-1",
        )
    )

    db.add(
        Contract(
            id=f"contract-{artist_id}",
            artist_id=artist.id,
            contract_type=ContractType.LABEL,
            counterparty="DistroKid",
            territory="US",
            terms={"artist_split": 0.7, "rate": 0.004},
        )
    )

    db.add(
        Payment(
            id=f"pay-{artist_id}",
            payment_type=PaymentType.ROYALTY,
            artist_id=artist.id,
            amount=700.0,
            currency="USD",
            source="DistroKid",
            received_at=datetime.now(timezone.utc),
        )
    )

    db.add(
        Work(
            id=f"work-{artist_id}",
            artist_id=artist.id,
            title="Track One",
            isrc="US-AAA-26-00001",
            work_type=WorkType.RECORDING,
        )
    )

    db.add(
        Event(
            id=f"event-{artist_id}",
            event_type=EventType.STREAM,
            work_id=f"work-{artist_id}",
            artist_id=artist.id,
            platform="Spotify",
            territory="US",
            timestamp=datetime.now(timezone.utc),
            quantity=1000,
            unit_value=0.003,
            currency="USD",
        )
    )

    db.add(
        NotificationPreference(
            artist_id=artist.id,
            email="artist@example.com",
            phone="+15555550100",
            notify_urgent_sol=True,
        )
    )

    db.commit()
    claim_id = claim.id
    db.close()
    return {"artist_id": artist_id, "claim_id": claim_id}


def test_claim_forecast_playbook_strength_and_negotiation_endpoints():
    ids = _seed_artist_stack("artist-intel-ext-1")

    forecast = client.get(f"/claims/{ids['claim_id']}/forecast")
    assert forecast.status_code == 200
    assert 0.0 <= forecast.json()["confidence"] <= 1.0
    assert "recommended_next_action" in forecast.json()

    playbook = client.get(f"/claims/{ids['claim_id']}/playbook")
    assert playbook.status_code == 200
    assert "required_fields_checklist" in playbook.json()

    strength = client.get(f"/claims/{ids['claim_id']}/evidence/strength")
    assert strength.status_code == 200
    assert 0.0 <= strength.json()["overall_strength_score"] <= 100.0

    negotiation = client.get(f"/claims/{ids['claim_id']}/negotiation-intel")
    assert negotiation.status_code == 200
    assert "settlement_ranges" in negotiation.json()


def test_expert_evidence_export_and_claim_list_forecast_block():
    ids = _seed_artist_stack("artist-intel-ext-2")

    expert = client.post(f"/claims/{ids['claim_id']}/evidence/export?mode=expert")
    assert expert.status_code == 200
    body = expert.json()
    assert body["mode"] == "expert"
    assert "tamper_checks" in body
    assert "expert_witness_mode" in body

    claims = client.get(f"/artists/{ids['artist_id']}/claims")
    assert claims.status_code == 200
    rows = claims.json()
    assert len(rows) == 1
    assert "claim" in rows[0]
    assert "forecast" in rows[0]


def test_recovery_endpoints_deadline_playbook_priority_and_splits():
    ids = _seed_artist_stack("artist-intel-ext-3")

    risk = client.get(f"/artists/{ids['artist_id']}/recovery/deadline-risk")
    assert risk.status_code == 200
    assert risk.json()["risk_color"] in {"RED", "YELLOW", "GREEN"}

    playbook_summary = client.get(f"/artists/{ids['artist_id']}/recovery/playbook-summary")
    assert playbook_summary.status_code == 200
    assert playbook_summary.json()["total_claims"] >= 1

    pq = client.get(f"/artists/{ids['artist_id']}/recovery/priority-queue")
    assert pq.status_code == 200
    assert "claim_forecasts" in pq.json()

    verify = client.get(f"/artists/{ids['artist_id']}/splits/verification")
    assert verify.status_code == 200
    assert "mismatch_count" in verify.json()

    conflicts = client.get(f"/artists/{ids['artist_id']}/splits/conflicts")
    assert conflicts.status_code == 200
    assert "conflicts" in conflicts.json()


def test_weekly_digest_pre_signature_and_partner_connectors():
    ids = _seed_artist_stack("artist-intel-ext-4")

    digest = client.get(f"/artists/{ids['artist_id']}/digest/weekly")
    assert digest.status_code == 200
    assert "digest" in digest.json()
    assert "delivery" in digest.json()

    review = client.post(
        f"/artists/{ids['artist_id']}/intelligence/contracts/pre-signature-review",
        json={
            "contract_text": "Artist royalty rate is 8%. Recoupment is cross-collateralized. No audit rights provided."
        },
    )
    assert review.status_code == 200
    assert "future_underpayment_risk_score" in review.json()
    assert isinstance(review.json()["recommended_redlines"], list)

    connect = client.post(f"/artists/{ids['artist_id']}/connect/stripe")
    assert connect.status_code == 200
    status = client.get(f"/artists/{ids['artist_id']}/connect/stripe/status")
    assert status.status_code == 200
    assert status.json()["status"]["supported"] is True
