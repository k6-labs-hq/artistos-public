from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.recovery.black_box_expiration import evaluate_black_box_expiration_for_anomaly
from XR7.recovery.claims_evidence_package_builder import ClaimsEvidencePackageBuilder
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.leakage_benchmark_engine import LeakageBenchmarkEngine
from XR7.recovery.recoverability_classifier import (
    ContractRecoverabilityScorer,
    build_recoverability_payload,
)
from XR7.recovery.society_signal_feed import SocietySignalFeed

client = TestClient(app)


def _create_artist(db, name: str = "Post Black Box Artist") -> Artist:
    row = Artist(id=str(uuid.uuid4()), name=name, created_at=datetime.now(timezone.utc))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _artist_token(artist_id: str) -> str:
    resp = client.post("/auth/login/artist", json={"artist_id": artist_id})
    assert resp.status_code == 200
    return str(resp.json()["access_token"])


def test_black_box_probability_fields_present_for_anomaly():
    anomaly = {
        "subtype": "MLC_UNMATCHED_DIGITAL_MECHANICAL",
        "event_date": (datetime.now(timezone.utc) - timedelta(days=900)).isoformat(),
    }
    result = evaluate_black_box_expiration_for_anomaly(anomaly)
    assert "P_already_redistributed" in result
    assert "P_still_recoverable" in result
    assert "redistribution_risk_score" in result


def test_contract_recoverability_scorer_returns_clause_strategy():
    scorer = ContractRecoverabilityScorer()
    out = scorer.score(
        anomaly_like={"event_date": "2025-01-01T00:00:00+00:00", "as_of_year": 2026},
        contract_data={"governing_clause": "audit rights", "audit_window_years": 3},
        jurisdiction="US",
    )
    assert out["governing_clause"] == "audit_rights"
    assert out["recommended_legal_strategy"]


def test_discovery_rule_engine_flags_urgent_deadline():
    engine = DiscoveryRuleEngine()
    old = datetime.now(timezone.utc) - timedelta(days=(365 * 3) - 30)
    out = engine.evaluate({"statement_receipt_date": old.isoformat(), "jurisdiction": "US"})
    assert out["urgent_flag"] is True
    assert out["discovery_memo"]["attorney_review_checklist"]["attorney_review_required"] is True


def test_leakage_benchmark_engine_returns_percentiles():
    engine = LeakageBenchmarkEngine()
    out = engine.compare_against_cohort(
        {
            "estimated_leaked": 1000,
            "total_estimated_earnings": 10000,
            "recovered": 200,
            "expired": 300,
        },
        [
            {
                "estimated_leaked": 800,
                "total_estimated_earnings": 10000,
                "recovered": 300,
                "expired": 100,
            },
            {
                "estimated_leaked": 1400,
                "total_estimated_earnings": 10000,
                "recovered": 150,
                "expired": 400,
            },
        ],
    )
    assert "leakage_percentile" in out
    assert "expiration_risk_rating" in out


def test_society_signal_feed_reclassifies_anomalies():
    feed = SocietySignalFeed()
    anomalies = [
        {
            "id": "a1",
            "subtype": "MLC_UNMATCHED_DIGITAL_MECHANICAL",
            "payer": "MLC",
            "event_date": "2024-01-01T00:00:00+00:00",
            "confidence_score": 0.8,
            "estimated_recoverable": 100,
        }
    ]
    out = feed.apply_signal(
        {
            "signal_type": "redistribution_pause",
            "payer_or_society": "MLC",
            "royalty_type": "digital_mechanicals",
            "effective_at": datetime.now(timezone.utc).isoformat(),
            "source": "test",
        },
        anomalies,
    )
    assert out["affected_anomaly_count"] == 1
    assert out["signal_log_entry"]["signal_type"] == "redistribution_pause"


def test_claim_evidence_package_builder_strength_and_checklist():
    builder = ClaimsEvidencePackageBuilder()
    package = builder.build(
        claim={"id": "c1", "artist_id": "ar1", "governing_law_state": "US"},
        anomaly={"id": "a1", "subtype": "RATE_DRIFT_UNDERPAYMENT", "description": "Underpayment"},
        recoverability_payload=build_recoverability_payload(
            {
                "subtype": "RATE_DRIFT_UNDERPAYMENT",
                "estimated_recoverable": 1200,
                "confidence_score": 0.9,
            }
        ),
        trust_score=88,
    )
    assert package["claim_strength_rating"] in {"A", "B", "C", "D"}
    assert package["attorney_review_checklist"]["attorney_declaration_template_present"] is True


def test_recovery_router_discovery_rule_endpoint():
    db = _TestSession()
    try:
        artist = _create_artist(db)
        token = _artist_token(artist.id)
        resp = client.post(
            f"/artists/{artist.id}/recovery/discovery-rule",
            json={
                "statement_receipt_date": (
                    datetime.now(timezone.utc) - timedelta(days=10)
                ).isoformat(),
                "jurisdiction": "US",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "statute_of_limitations_deadline" in body
    finally:
        db.close()


def test_claim_creation_sets_attorney_review_gate_when_low_trust():
    db = _TestSession()
    try:
        artist = _create_artist(db)
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="RATE_DRIFT_UNDERPAYMENT",
            severity=AnomalySeverity.HIGH,
            estimated_recoverable=800.0,
            confidence_score=0.2,
            status=AnomalyStatus.OPEN,
            description="Low-confidence underpayment",
            created_at=datetime.now(timezone.utc),
        )
        db.add(anomaly)
        db.commit()

        token = _artist_token(artist.id)
        resp = client.post(
            f"/artists/{artist.id}/claims",
            json={"anomaly_id": anomaly.id, "claim_type": "RECOVERY"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        claim_id = resp.json()["id"]

        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        assert claim is not None
        assert claim.attorney_review_required is True
    finally:
        db.close()


def test_advance_claim_blocked_when_attorney_review_required():
    db = _TestSession()
    try:
        artist = _create_artist(db)
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="RATE_DRIFT_UNDERPAYMENT",
            severity=AnomalySeverity.HIGH,
            estimated_recoverable=1200.0,
            confidence_score=0.95,
            status=AnomalyStatus.OPEN,
            description="Underpayment",
            created_at=datetime.now(timezone.utc),
        )
        db.add(anomaly)
        db.flush()
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="RECOVERY",
            status=ClaimStatus.PREPARED,
            attorney_review_required=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()

        resp = client.post(f"/claims/{claim.id}/advance")
        assert resp.status_code == 422
    finally:
        db.close()
