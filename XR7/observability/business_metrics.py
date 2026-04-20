"""
Prometheus Metrics Exporter for ArtistOS Business KPIs.

Exports custom application metrics for Grafana dashboards and alerting:
- artists_onboarded_total: Counter of newly onboarded artists
- claims_submitted_total: Counter of claims submitted
- claims_recovered_total: Counter of successfully recovered claims
- revenue_protected_usd: Gauge of total revenue protected
- avg_recovery_time_days: Gauge of average claim recovery time
- anomalies_detected_total: Counter of anomalies detected in ingestion

These metrics complement infrastructure metrics (CPU, memory, network)
with business KPIs for operational dashboards.

Documented in docs/production_readiness_wave2_2026_q2.md OPS-004
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Create custom registry to avoid conflicts with FastAPI's default Prometheus metrics
business_metrics_registry = CollectorRegistry()

# Define business metrics
artists_onboarded = Counter(
    "artists_onboarded_total",
    "Total number of artists onboarded to the platform",
    registry=business_metrics_registry,
)

claims_submitted = Counter(
    "claims_submitted_total",
    "Total number of recovery claims submitted",
    registry=business_metrics_registry,
)

claims_recovered = Counter(
    "claims_recovered_total",
    "Total number of successfully recovered claims (settled status)",
    registry=business_metrics_registry,
)

revenue_protected = Gauge(
    "revenue_protected_usd",
    "Total revenue protected through successful recoveries (USD)",
    registry=business_metrics_registry,
)

avg_recovery_time = Gauge(
    "avg_recovery_time_days",
    "Average time to recover a claim from submission to settlement (days)",
    registry=business_metrics_registry,
)

anomalies_detected = Counter(
    "anomalies_detected_total",
    "Total number of anomalies detected in royalty statements",
    registry=business_metrics_registry,
)

error_budget_remaining = Gauge(
    "error_budget_remaining_percent",
    "Percentage of error budget remaining in current window",
    registry=business_metrics_registry,
)

webhook_delivery_rate = Gauge(
    "webhook_delivery_success_rate_percent",
    "Webhook delivery success rate in last 24 hours",
    registry=business_metrics_registry,
)


def update_business_metrics(db: Session) -> None:
    """Update all business metrics from database.

    This should be called periodically (e.g., every 60 seconds) by a background
    task or by the /metrics endpoint handler.

    Args:
        db: Database session
    """
    try:
        # Time window for calculations (last 30 days)
        window_days = int(os.environ.get("METRICS_WINDOW_DAYS", "30"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

        # Artists onboarded (lifetime counter)
        total_artists = db.query(func.count(Artist.id)).scalar() or 0
        # Note: Prometheus Counters can't be set directly, they only increment
        # In production, this would be incremented on each artist creation event
        # For MVP, we'll use a Gauge instead to track total count
        from prometheus_client import Gauge

        artists_total_gauge = Gauge(
            "artists_total",
            "Total number of artists in the platform",
            registry=business_metrics_registry,
        )
        artists_total_gauge.set(total_artists)

        # Claims submitted (recent window)
        recent_claims = (
            db.query(func.count(Claim.id)).filter(Claim.created_at >= cutoff).scalar() or 0
        )
        claims_submitted_gauge = Gauge(
            "claims_submitted_recent",
            f"Claims submitted in last {window_days} days",
            registry=business_metrics_registry,
        )
        claims_submitted_gauge.set(recent_claims)

        # Claims recovered (recent window)
        recent_recovered = (
            db.query(func.count(Claim.id))
            .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.SETTLED)
            .scalar()
            or 0
        )
        claims_recovered_gauge = Gauge(
            "claims_recovered_recent",
            f"Claims recovered in last {window_days} days",
            registry=business_metrics_registry,
        )
        claims_recovered_gauge.set(recent_recovered)

        # Revenue protected
        total_revenue = (
            db.query(func.sum(Claim.recovered_amount))
            .filter(Claim.status == ClaimStatus.SETTLED)
            .scalar()
            or 0.0
        )
        revenue_protected.set(total_revenue)

        # Average recovery time (days)
        avg_time_result = (
            db.query(
                func.avg(func.extract("epoch", Claim.updated_at - Claim.created_at) / 86400).label(
                    "avg_days"
                )
            )
            .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.SETTLED)
            .first()
        )
        avg_time_days = float(avg_time_result[0]) if avg_time_result[0] else 0.0
        avg_recovery_time.set(avg_time_days)

        # Anomalies detected (recent window)
        recent_anomalies = (
            db.query(func.count(Anomaly.id)).filter(Anomaly.created_at >= cutoff).scalar() or 0
        )
        anomalies_recent_gauge = Gauge(
            "anomalies_detected_recent",
            f"Anomalies detected in last {window_days} days",
            registry=business_metrics_registry,
        )
        anomalies_recent_gauge.set(recent_anomalies)

        logger.debug(
            "Business metrics updated",
            extra={
                "total_artists": total_artists,
                "recent_claims": recent_claims,
                "recent_recovered": recent_recovered,
                "total_revenue_protected": total_revenue,
            },
        )

    except Exception as e:
        logger.error(f"Error updating business metrics: {e}", exc_info=True)


def get_prometheus_metrics_text() -> str:
    """Get Prometheus metrics in text exposition format.

    This is the format expected by Prometheus scraping.

    Returns:
        Metrics text (Content-Type: text/plain; version=0.0.4)
    """
    return generate_latest(business_metrics_registry).decode("utf-8")
