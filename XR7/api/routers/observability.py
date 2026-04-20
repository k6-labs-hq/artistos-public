"""
Observability router for operational metrics and dashboards.

Endpoints:
- GET /observability/error-budget - Error budget status
- GET /observability/circuit-breakers - Circuit breaker states
- GET /observability/business-metrics - Business KPIs
- GET /observability/webhooks/delivery-stats - Webhook delivery metrics

These endpoints power operational dashboards and alerting.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.webhook_event import WebhookEvent
from XR7.observability.business_metrics import get_prometheus_metrics_text, update_business_metrics
from XR7.observability.error_budget import (
    AVAILABILITY_SLO,
    BUDGET_WINDOW_DAYS,
    calculate_error_budget_for_window,
)
from XR7.recovery.circuit_breaker import CircuitBreakerRegistry
from xr7_common.logging import get_logger

router = APIRouter(tags=["observability"], prefix="/observability")
logger = get_logger(__name__)


@router.get("/error-budget")
def get_error_budget(
    window_days: int = Query(default=BUDGET_WINDOW_DAYS, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Get current error budget status.

    Calculates error budget based on API request success rate over rolling window.

    Query Parameters:
        window_days: Rolling window size in days (default: 30)

    Returns:
        Error budget state with consumption, remaining budget, burn rate

    Example Response:
        {
            "service_name": "xr7-engine",
            "slo_target": 0.999,
            "window_days": 30,
            "budget_total_minutes": 43.2,
            "budget_consumed_minutes": 10.5,
            "budget_remaining_minutes": 32.7,
            "budget_remaining_percent": 75.69,
            "burn_rate": 0.8,
            "status": "healthy",
            "measured_at": "2026-04-19T12:00:00Z"
        }
    """
    # In production, this would query actual request metrics from Prometheus/TimescaleDB
    # For now, we'll use a simplified calculation based on claim success rate
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    total_claims = db.query(func.count(Claim.id)).filter(Claim.created_at >= cutoff).scalar() or 0

    failed_claims = (
        db.query(func.count(Claim.id))
        .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.FAILED)
        .scalar()
        or 0
    )

    # Use claim processing as proxy for overall system health
    # In production: query from access logs, Prometheus, or APM tool
    total_requests = max(total_claims, 1000)  # Minimum sample size
    failed_requests = failed_claims

    budget = calculate_error_budget_for_window(
        total_requests=total_requests,
        failed_requests=failed_requests,
        slo_target=AVAILABILITY_SLO,
        window_days=window_days,
    )

    return {
        "service_name": budget.service_name,
        "slo_target": budget.slo_target,
        "window_days": budget.window_days,
        "budget_total_minutes": budget.budget_total_minutes,
        "budget_consumed_minutes": budget.budget_consumed_minutes,
        "budget_remaining_minutes": budget.budget_remaining_minutes,
        "budget_remaining_percent": budget.budget_remaining_percent,
        "burn_rate": budget.burn_rate,
        "status": budget.status,
        "measured_at": budget.measured_at.isoformat(),
        "explanation": (
            f"Error budget allows {budget.budget_total_minutes} minutes of downtime "
            f"in {window_days} days to maintain {budget.slo_target*100}% availability. "
            f"Status: {budget.status.upper()}. "
            f"{budget.budget_remaining_percent}% of budget remaining."
        ),
    }


@router.get("/circuit-breakers")
def get_circuit_breaker_status():
    """Get status of all circuit breakers.

    Returns current state (open/half-open/closed) for all external integrations.

    Returns:
        List of circuit breaker states

    Example Response:
        {
            "circuit_breakers": [
                {
                    "name": "trolley_api",
                    "state": "closed",
                    "failure_count": 0,
                    "last_failure_time": null,
                    "success_count": 150
                },
                {
                    "name": "spotify_api",
                    "state": "open",
                    "failure_count": 5,
                    "last_failure_time": "2026-04-19T11:30:00Z",
                    "next_retry_time": "2026-04-19T11:40:00Z"
                }
            ]
        }
    """
    breakers = CircuitBreakerRegistry.get_all_states()

    return {
        "circuit_breakers": [
            {
                "name": name,
                "state": info["state"],
                "failure_count": info.get("failure_count", 0),
                "last_failure_time": (
                    info["last_failure_time"].isoformat() if info.get("last_failure_time") else None
                ),
                "next_retry_time": (
                    info["next_retry_time"].isoformat() if info.get("next_retry_time") else None
                ),
                "success_count": info.get("success_count", 0),
            }
            for name, info in breakers.items()
        ],
        "summary": {
            "total_breakers": len(breakers),
            "open_count": sum(1 for info in breakers.values() if info["state"] == "open"),
            "half_open_count": sum(1 for info in breakers.values() if info["state"] == "half_open"),
            "closed_count": sum(1 for info in breakers.values() if info["state"] == "closed"),
        },
    }


@router.get("/business-metrics")
def get_business_metrics(
    window_days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get business KPI metrics for operational dashboards.

    Query Parameters:
        window_days: Time window for metrics (default: 30 days)

    Returns:
        Business KPIs: artists onboarded, claims submitted/recovered, revenue protected

    Example Response:
        {
            "window_days": 30,
            "artists_onboarded": 125,
            "claims_submitted": 450,
            "claims_recovered": 320,
            "claims_in_progress": 100,
            "revenue_protected_usd": 125000.50,
            "avg_recovery_time_days": 45.2,
            "anomalies_detected": 1250,
            "measured_at": "2026-04-19T12:00:00Z"
        }
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    artists_onboarded = (
        db.query(func.count(Artist.id)).filter(Artist.created_at >= cutoff).scalar() or 0
    )

    claims_submitted = (
        db.query(func.count(Claim.id)).filter(Claim.created_at >= cutoff).scalar() or 0
    )

    claims_recovered = (
        db.query(func.count(Claim.id))
        .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.SETTLED)
        .scalar()
        or 0
    )

    claims_in_progress = (
        db.query(func.count(Claim.id))
        .filter(
            Claim.created_at >= cutoff,
            Claim.status.in_([ClaimStatus.SUBMITTED, ClaimStatus.IN_REVIEW]),
        )
        .scalar()
        or 0
    )

    revenue_protected = (
        db.query(func.sum(Claim.recovered_amount))
        .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.SETTLED)
        .scalar()
        or 0.0
    )

    anomalies_detected = (
        db.query(func.count(Anomaly.id)).filter(Anomaly.created_at >= cutoff).scalar() or 0
    )

    # Average recovery time (days from submission to settlement)
    avg_recovery_time_result = (
        db.query(
            func.avg(func.extract("epoch", Claim.updated_at - Claim.created_at) / 86400).label(
                "avg_days"
            )
        )
        .filter(Claim.created_at >= cutoff, Claim.status == ClaimStatus.SETTLED)
        .first()
    )
    avg_recovery_time_days = (
        round(avg_recovery_time_result[0], 2) if avg_recovery_time_result[0] else 0.0
    )

    return {
        "window_days": window_days,
        "period_start": cutoff.isoformat(),
        "period_end": datetime.now(timezone.utc).isoformat(),
        "artists_onboarded": artists_onboarded,
        "claims_submitted": claims_submitted,
        "claims_recovered": claims_recovered,
        "claims_in_progress": claims_in_progress,
        "recovery_rate_percent": round(
            (claims_recovered / claims_submitted * 100) if claims_submitted > 0 else 0.0, 2
        ),
        "revenue_protected_usd": round(revenue_protected, 2),
        "avg_recovery_time_days": avg_recovery_time_days,
        "anomalies_detected": anomalies_detected,
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/webhooks/delivery-stats")
def get_webhook_delivery_stats(
    window_hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Get webhook delivery statistics.

    Query Parameters:
        window_hours: Time window in hours (default: 24)

    Returns:
        Webhook delivery metrics: success rate, retry counts, DLQ depth

    Example Response:
        {
            "window_hours": 24,
            "total_webhooks": 5000,
            "delivered": 4750,
            "pending": 100,
            "failed": 150,
            "delivery_success_rate_percent": 95.0,
            "avg_retry_count": 0.5,
            "measured_at": "2026-04-19T12:00:00Z"
        }
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    total_webhooks = (
        db.query(func.count(WebhookEvent.id)).filter(WebhookEvent.created_at >= cutoff).scalar()
        or 0
    )

    delivered = (
        db.query(func.count(WebhookEvent.id))
        .filter(WebhookEvent.created_at >= cutoff, WebhookEvent.delivered.is_(True))
        .scalar()
        or 0
    )

    pending = (
        db.query(func.count(WebhookEvent.id))
        .filter(
            WebhookEvent.created_at >= cutoff,
            WebhookEvent.delivered.is_(False),
            WebhookEvent.retry_count < 5,
        )
        .scalar()
        or 0
    )

    failed = (
        db.query(func.count(WebhookEvent.id))
        .filter(
            WebhookEvent.created_at >= cutoff,
            WebhookEvent.delivered.is_(False),
            WebhookEvent.retry_count >= 5,
        )
        .scalar()
        or 0
    )

    avg_retry_count = (
        db.query(func.avg(WebhookEvent.retry_count))
        .filter(WebhookEvent.created_at >= cutoff)
        .scalar()
        or 0.0
    )

    delivery_success_rate = (
        round((delivered / total_webhooks * 100), 2) if total_webhooks > 0 else 100.0
    )

    return {
        "window_hours": window_hours,
        "period_start": cutoff.isoformat(),
        "period_end": datetime.now(timezone.utc).isoformat(),
        "total_webhooks": total_webhooks,
        "delivered": delivered,
        "pending": pending,
        "failed": failed,
        "delivery_success_rate_percent": delivery_success_rate,
        "avg_retry_count": round(avg_retry_count, 2),
        "alert_threshold_percent": 95.0,
        "status": "healthy" if delivery_success_rate >= 95.0 else "degraded",
        "measured_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics", response_class=PlainTextResponse)
def get_prometheus_metrics(db: Session = Depends(get_db)):
    """Get Prometheus metrics in text exposition format.

    This endpoint should be scraped by Prometheus server.
    Exposes business KPIs and operational metrics.

    Returns:
        Prometheus metrics in text format

    Example metrics:
        # HELP artists_total Total number of artists in the platform
        # TYPE artists_total gauge
        artists_total 125.0

        # HELP revenue_protected_usd Total revenue protected (USD)
        # TYPE revenue_protected_usd gauge
        revenue_protected_usd 125000.50
    """
    # Update metrics from database before returning
    update_business_metrics(db)

    # Return metrics in Prometheus text exposition format
    return get_prometheus_metrics_text()
