"""
Tests for ML confidence gating service.

Validates three-tier confidence-based routing for anomaly detection at scale.

Closes: XR7-407
Domain: ml
Scale-target: ML-assisted anomaly detection with confidence-gated workflows
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.ml.confidence_gating import ConfidenceGatingService, ConfidenceTier
from XR7.models.base import Base


@pytest.fixture
def db_session():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def gating_service(db_session):
    """Create confidence gating service."""
    return ConfidenceGatingService(db_session)


def test_reject_tier_low_confidence(gating_service):
    """Confidence below 0.30 should be rejected."""
    decision = gating_service.evaluate(confidence=0.25)

    assert decision.tier == ConfidenceTier.REJECT
    assert decision.should_create is False
    assert decision.requires_review is False
    assert decision.priority_score == 0.0
    assert "below rejection threshold" in decision.reasoning


def test_reject_tier_boundary(gating_service):
    """Confidence exactly at 0.30 should be in REVIEW tier."""
    decision = gating_service.evaluate(confidence=0.30)

    assert decision.tier == ConfidenceTier.REVIEW
    assert decision.should_create is True
    assert decision.requires_review is True


def test_review_tier_mid_confidence(gating_service):
    """Confidence in mid-range (0.30-0.89) should require review."""
    decision = gating_service.evaluate(confidence=0.75)

    assert decision.tier == ConfidenceTier.REVIEW
    assert decision.should_create is True
    assert decision.requires_review is True
    assert 0.0 < decision.priority_score < 1.0
    assert "requires analyst review" in decision.reasoning


def test_auto_accept_tier_high_confidence(gating_service):
    """Confidence >= 0.90 should auto-accept."""
    decision = gating_service.evaluate(confidence=0.92)

    assert decision.tier == ConfidenceTier.AUTO_ACCEPT
    assert decision.should_create is True
    assert decision.requires_review is False
    assert decision.priority_score == 1.0
    assert "auto-accept" in decision.reasoning


def test_auto_accept_tier_boundary(gating_service):
    """Confidence exactly at 0.90 should auto-accept."""
    decision = gating_service.evaluate(confidence=0.90)

    assert decision.tier == ConfidenceTier.AUTO_ACCEPT
    assert decision.should_create is True
    assert decision.requires_review is False


def test_priority_scoring_increases_with_confidence(gating_service):
    """Higher confidence in REVIEW tier should have higher priority."""
    low_conf = gating_service.evaluate(confidence=0.40)
    high_conf = gating_service.evaluate(confidence=0.85)

    assert high_conf.priority_score > low_conf.priority_score


def test_priority_scoring_increases_with_amount(gating_service):
    """Larger estimated_recoverable should increase priority."""
    small_amount = gating_service.evaluate(
        confidence=0.70, context={"estimated_recoverable": 500.0}
    )
    large_amount = gating_service.evaluate(
        confidence=0.70, context={"estimated_recoverable": 50000.0}
    )

    assert large_amount.priority_score > small_amount.priority_score


def test_priority_scoring_urgency_flag(gating_service):
    """Urgency flag should boost priority."""
    no_urgency = gating_service.evaluate(confidence=0.70, context={"urgency_flag": False})
    with_urgency = gating_service.evaluate(confidence=0.70, context={"urgency_flag": True})

    assert with_urgency.priority_score > no_urgency.priority_score


def test_confidence_out_of_range_clamped(gating_service):
    """Confidence outside [0, 1] should be clamped."""
    # Negative confidence
    neg_decision = gating_service.evaluate(confidence=-0.5)
    assert 0.0 <= neg_decision.confidence_score <= 1.0

    # Confidence > 1.0
    high_decision = gating_service.evaluate(confidence=1.5)
    assert 0.0 <= high_decision.confidence_score <= 1.0
    assert high_decision.tier == ConfidenceTier.AUTO_ACCEPT  # Clamped to 1.0


def test_metrics_tracking(gating_service):
    """Metrics should track gating decisions."""
    # Create mix of decisions
    gating_service.evaluate(confidence=0.20)  # Reject
    gating_service.evaluate(confidence=0.50)  # Review
    gating_service.evaluate(confidence=0.95)  # Auto-accept

    metrics = gating_service.get_metrics()

    assert metrics["total_evaluations"] == 3
    assert metrics["counts"]["rejected"] == 1
    assert metrics["counts"]["routed_to_review"] == 1
    assert metrics["counts"]["auto_accepted"] == 1
    assert metrics["rejection_rate"] == pytest.approx(0.3333, rel=1e-3)
    assert metrics["review_rate"] == pytest.approx(0.3333, rel=1e-3)
    assert metrics["auto_accept_rate"] == pytest.approx(0.3333, rel=1e-3)


def test_metrics_reset(gating_service):
    """Metrics should reset to zero."""
    gating_service.evaluate(confidence=0.50)
    gating_service.evaluate(confidence=0.50)

    assert gating_service.get_metrics()["total_evaluations"] == 2

    gating_service.reset_metrics()

    metrics = gating_service.get_metrics()
    assert metrics["total_evaluations"] == 0
    assert metrics["counts"]["rejected"] == 0
    assert metrics["counts"]["routed_to_review"] == 0
    assert metrics["counts"]["auto_accepted"] == 0


def test_decision_metadata_includes_context(gating_service):
    """Decision metadata should include provided context."""
    context = {
        "anomaly_type": "RATE_DRIFT",
        "estimated_recoverable": 15000.0,
        "artist_id": "artist-123",
    }

    decision = gating_service.evaluate(confidence=0.75, context=context)

    assert "timestamp" in decision.metadata
    assert decision.metadata["context"] == context
    assert "thresholds" in decision.metadata


def test_priority_zero_for_zero_amount(gating_service):
    """Zero estimated_recoverable should contribute zero to amount component."""
    decision = gating_service.evaluate(
        confidence=0.30,  # Minimum for REVIEW tier
        context={"estimated_recoverable": 0.0},
    )

    # Priority should be based only on confidence and urgency (no amount)
    # With conf=0.30 (min), urgency=False (0.3), amount=0.0:
    # priority = 0.40*0.0 + 0.35*0.0 + 0.25*0.3 = 0.075
    assert decision.priority_score <= 0.1


def test_priority_max_for_high_values(gating_service):
    """Maximum inputs should produce high priority score."""
    decision = gating_service.evaluate(
        confidence=0.89,  # Just below auto-accept
        context={
            "estimated_recoverable": 100000.0,  # Very high
            "urgency_flag": True,
        },
    )

    # Should be near 1.0 but not exactly (auto-accept gets 1.0)
    assert decision.priority_score > 0.9
    assert decision.priority_score < 1.0


def test_batch_evaluation_consistency(gating_service):
    """Same inputs should produce consistent results."""
    decisions = [
        gating_service.evaluate(confidence=0.75, context={"estimated_recoverable": 10000.0})
        for _ in range(10)
    ]

    # All should have same tier and priority
    assert all(d.tier == ConfidenceTier.REVIEW for d in decisions)
    priorities = [d.priority_score for d in decisions]
    assert len(set(priorities)) == 1  # All identical


def test_different_anomaly_types_tracked(gating_service):
    """Service should handle different anomaly types in context."""
    types = ["RATE_DRIFT", "MISSING_PAYMENT", "METADATA_CONFLICT", "UGC_UNDERPAYMENT"]

    for anom_type in types:
        decision = gating_service.evaluate(confidence=0.70, context={"anomaly_type": anom_type})
        assert decision.metadata["context"]["anomaly_type"] == anom_type


def test_edge_case_confidence_exactly_one(gating_service):
    """Confidence of exactly 1.0 should auto-accept."""
    decision = gating_service.evaluate(confidence=1.0)

    assert decision.tier == ConfidenceTier.AUTO_ACCEPT
    assert decision.confidence_score == 1.0


def test_edge_case_confidence_exactly_zero(gating_service):
    """Confidence of exactly 0.0 should reject."""
    decision = gating_service.evaluate(confidence=0.0)

    assert decision.tier == ConfidenceTier.REJECT
    assert decision.confidence_score == 0.0


def test_metrics_empty_service():
    """Metrics should handle zero evaluations gracefully."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    gating = ConfidenceGatingService(session)
    metrics = gating.get_metrics()

    assert metrics["total_evaluations"] == 0
    assert metrics["rejection_rate"] == 0.0
    assert metrics["review_rate"] == 0.0
    assert metrics["auto_accept_rate"] == 0.0

    session.close()
    Base.metadata.drop_all(engine)


def test_reasoning_field_populated(gating_service):
    """All decisions should have human-readable reasoning."""
    reject = gating_service.evaluate(confidence=0.15)
    review = gating_service.evaluate(confidence=0.60)
    accept = gating_service.evaluate(confidence=0.95)

    assert len(reject.reasoning) > 0
    assert len(review.reasoning) > 0
    assert len(accept.reasoning) > 0
