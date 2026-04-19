"""
Tests for SLO tracking service.

Validates continuous SLO measurement, persistence, and alerting.

Closes: XR7-408
Domain: observability
Scale-target: 10x tenant count with proactive SLO monitoring
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from XR7.models.base import Base
from XR7.models.slo_metric import SloMetric
from XR7.observability.slo_tracking import SloTrackingService


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
def slo_service(db_session):
    """Create SLO tracking service."""
    return SloTrackingService(db_session, org_id="test-org")


def test_measure_and_persist_latency_within_slo(slo_service, db_session):
    """Latency below threshold should not breach SLO."""
    metric = slo_service.measure_and_persist(
        metric_name="api_latency",
        latency_samples=[100, 150, 200, 250, 300],  # p95 = 300ms
        total_requests=5000,
        failed_requests=0,
        threshold_ms=500,  # Well above p95
    )

    assert metric.current_p95_ms == 300
    assert metric.breached is False
    assert metric.metric_name == "api_latency"
    assert metric.org_id == "test-org"

    # Verify persisted
    saved = db_session.query(SloMetric).filter(SloMetric.id == metric.id).first()
    assert saved is not None
    assert saved.breached is False


def test_measure_and_persist_latency_breach(slo_service, db_session):
    """Latency above threshold should breach SLO."""
    metric = slo_service.measure_and_persist(
        metric_name="api_latency",
        latency_samples=[100, 150, 600, 700, 800],  # p95 = 800ms
        total_requests=5000,
        failed_requests=0,
        threshold_ms=500,  # Below p95
    )

    assert metric.current_p95_ms == 800
    assert metric.breached is True


def test_measure_and_persist_error_budget_critical(slo_service, db_session):
    """High error rate should breach error budget."""
    metric = slo_service.measure_and_persist(
        metric_name="api_availability",
        latency_samples=[100, 150, 200],
        total_requests=10000,
        failed_requests=500,  # 5% error rate, way above 0.1% SLO allowance
        slo_target=0.999,  # 99.9% availability
    )

    assert metric.breached is True
    assert metric.error_budget_pct is not None
    assert metric.error_budget_pct < 50  # Budget heavily consumed
    assert metric.burn_rate is not None
    assert metric.burn_rate > 1.0  # Burning faster than expected


def test_measure_and_persist_healthy_state(slo_service, db_session):
    """Healthy metrics should show good budget and no breach."""
    metric = slo_service.measure_and_persist(
        metric_name="api_health",
        latency_samples=[80, 90, 100, 110, 120],
        total_requests=100000,
        failed_requests=50,  # 0.05% error rate - well within 0.1% budget
        threshold_ms=500,
        slo_target=0.999,
    )

    assert metric.breached is False
    assert metric.current_p95_ms == 120
    assert metric.error_budget_pct > 50  # Plenty of budget remaining


def test_p95_calculation_small_sample(slo_service):
    """Small sample sizes should use max as conservative estimate."""
    samples = [100, 200, 300]
    p95 = slo_service._calculate_p95(samples)

    # With 3 samples, conservatively use max
    assert p95 == 300


def test_p95_calculation_large_sample(slo_service):
    """Large sample should calculate accurate p95."""
    # 100 samples: 100, 101, 102, ..., 199
    samples = list(range(100, 200))
    p95 = slo_service._calculate_p95(samples)

    # p95 of [100-199] should be around 195
    assert 194 <= p95 <= 196


def test_p95_calculation_empty_samples(slo_service):
    """Empty samples should return 0."""
    p95 = slo_service._calculate_p95([])
    assert p95 == 0.0


def test_get_slo_trend_returns_history(slo_service, db_session):
    """Should retrieve historical SLO measurements."""
    # Create multiple measurements
    for i in range(5):
        slo_service.measure_and_persist(
            metric_name="test_metric",
            latency_samples=[100 + i * 10],
            total_requests=1000,
            failed_requests=i,
        )

    trend = slo_service.get_slo_trend("test_metric", hours=24)

    assert len(trend) == 5
    assert all("measured_at" in t for t in trend)
    assert all("current_p95_ms" in t for t in trend)
    assert all("error_budget_pct" in t for t in trend)


def test_get_slo_trend_filters_by_time(slo_service, db_session):
    """Should only return measurements within time window."""
    # Create old measurement (manually set timestamp)
    old_metric = SloMetric(
        org_id="test-org",
        metric_name="test_metric",
        current_p95_ms=100,
        window_seconds=3600,
        threshold_ms=500,
        measured_at=datetime.now(timezone.utc) - timedelta(hours=48),
    )
    db_session.add(old_metric)
    db_session.commit()

    # Create recent measurement
    slo_service.measure_and_persist(
        metric_name="test_metric",
        latency_samples=[150],
        total_requests=1000,
        failed_requests=0,
    )

    # Query last 24 hours - should exclude 48-hour-old metric
    trend = slo_service.get_slo_trend("test_metric", hours=24)

    assert len(trend) == 1


def test_check_budget_health_no_data(slo_service):
    """Should return unknown status when no measurements exist."""
    health = slo_service.check_budget_health("nonexistent_metric")

    assert health["status"] == "unknown"
    assert "No SLO measurements" in health["message"]


def test_check_budget_health_critical(slo_service):
    """Should return critical status when budget nearly exhausted."""
    slo_service.measure_and_persist(
        metric_name="critical_metric",
        latency_samples=[100],
        total_requests=10000,
        failed_requests=900,  # 9% error rate - exhausts 99.9% SLO budget
        slo_target=0.999,
    )

    health = slo_service.check_budget_health("critical_metric")

    assert health["status"] == "critical"
    assert health["error_budget_remaining_pct"] < 20
    assert any("CRITICAL" in rec for rec in health["recommendations"])


def test_check_budget_health_warning(slo_service):
    """Should return warning when budget moderately consumed."""
    slo_service.measure_and_persist(
        metric_name="warning_metric",
        latency_samples=[100],
        total_requests=10000,
        failed_requests=200,  # 2% error rate - consumes significant budget
        slo_target=0.999,
    )

    health = slo_service.check_budget_health("warning_metric")

    assert health["status"] == "warning"
    assert 20 <= health["error_budget_remaining_pct"] < 50
    assert any("WARNING" in rec for rec in health["recommendations"])


def test_check_budget_health_healthy(slo_service):
    """Should return healthy status when budget consumption is low."""
    slo_service.measure_and_persist(
        metric_name="healthy_metric",
        latency_samples=[100],
        total_requests=100000,
        failed_requests=10,  # 0.01% error rate - well within budget
        slo_target=0.999,
    )

    health = slo_service.check_budget_health("healthy_metric")

    assert health["status"] == "healthy"
    assert health["error_budget_remaining_pct"] > 50
    assert any("Healthy" in rec or "safe to deploy" in rec for rec in health["recommendations"])


def test_check_budget_health_high_burn_rate(slo_service):
    """Should recommend action when burn rate is high."""
    slo_service.measure_and_persist(
        metric_name="high_burn_metric",
        latency_samples=[100],
        total_requests=10000,
        failed_requests=600,  # Creates high burn rate
        slo_target=0.999,
    )

    health = slo_service.check_budget_health("high_burn_metric")

    assert health["burn_rate"] > 5.0
    assert any("burn rate" in rec.lower() for rec in health["recommendations"])


def test_check_budget_health_latency_overage(slo_service):
    """Should recommend investigation when latency exceeds threshold."""
    slo_service.measure_and_persist(
        metric_name="slow_metric",
        latency_samples=[800, 900, 1000],
        total_requests=1000,
        failed_requests=0,
        threshold_ms=500,
    )

    health = slo_service.check_budget_health("slow_metric")

    assert health["current_p95_ms"] > health["threshold_ms"]
    assert any("Latency" in rec or "slow" in rec.lower() for rec in health["recommendations"])


def test_multi_org_isolation(db_session):
    """Different orgs should have isolated SLO tracking."""
    service1 = SloTrackingService(db_session, org_id="org-1")
    service2 = SloTrackingService(db_session, org_id="org-2")

    service1.measure_and_persist(
        metric_name="shared_metric",
        latency_samples=[100],
        total_requests=1000,
        failed_requests=0,
    )

    service2.measure_and_persist(
        metric_name="shared_metric",
        latency_samples=[500],
        total_requests=1000,
        failed_requests=0,
    )

    trend1 = service1.get_slo_trend("shared_metric", hours=24)
    trend2 = service2.get_slo_trend("shared_metric", hours=24)

    assert len(trend1) == 1
    assert len(trend2) == 1
    assert trend1[0]["current_p95_ms"] == 100
    assert trend2[0]["current_p95_ms"] == 500


def test_persisted_metric_has_all_fields(slo_service, db_session):
    """Persisted metric should have complete field set."""
    metric = slo_service.measure_and_persist(
        metric_name="complete_metric",
        latency_samples=[150, 200, 250],
        total_requests=5000,
        failed_requests=10,
        window_seconds=7200,
        threshold_ms=300,
    )

    assert metric.id is not None
    assert metric.org_id == "test-org"
    assert metric.metric_name == "complete_metric"
    assert metric.window_seconds == 7200
    assert metric.threshold_ms == 300
    assert metric.current_p95_ms is not None
    assert metric.error_budget_pct is not None
    assert metric.burn_rate is not None
    assert metric.breached is not None
    assert metric.description is not None
    assert metric.measured_at is not None
    assert metric.created_at is not None
