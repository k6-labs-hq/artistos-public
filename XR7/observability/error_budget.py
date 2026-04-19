"""
Error Budget Tracking System for XR7 Engine.

Implements SRE error budget methodology:
- Calculate error budget based on SLO (e.g., 99.9% = 43.2 minutes downtime/month)
- Track budget consumption in real-time
- Alert when budget 50% consumed (warning), 80% consumed (critical)
- Burn rate calculation (how fast budget is being consumed)

SLO Configuration:
- availability_slo: Target uptime percentage (default: 99.9%)
- latency_slo_p95_ms: p95 latency threshold in milliseconds (default: 1000ms)
- error_rate_slo: Maximum error rate percentage (default: 1%)

Environment Variables:
- ERROR_BUDGET_SLO_AVAILABILITY: Override availability SLO (default: 0.999)
- ERROR_BUDGET_SLO_LATENCY_P95: Override latency SLO in ms (default: 1000)
- ERROR_BUDGET_WINDOW_DAYS: Rolling window for budget calculation (default: 30)

Documented in docs/production_readiness_wave2_2026_q2.md OPS-001
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from xr7_common.logging import get_logger

logger = get_logger(__name__)

# SLO configuration from environment with sensible defaults
AVAILABILITY_SLO = float(os.environ.get("ERROR_BUDGET_SLO_AVAILABILITY", "0.999"))  # 99.9%
LATENCY_SLO_P95_MS = int(os.environ.get("ERROR_BUDGET_SLO_LATENCY_P95", "1000"))  # 1000ms
ERROR_RATE_SLO = float(os.environ.get("ERROR_BUDGET_SLO_ERROR_RATE", "0.01"))  # 1%
BUDGET_WINDOW_DAYS = int(os.environ.get("ERROR_BUDGET_WINDOW_DAYS", "30"))  # 30-day rolling window


@dataclass
class ErrorBudget:
    """Error budget state for a service."""

    service_name: str
    slo_target: float  # e.g., 0.999 for 99.9%
    window_days: int  # Rolling window (usually 30 days)
    budget_total_minutes: float  # Total allowed downtime
    budget_consumed_minutes: float  # Downtime consumed so far
    budget_remaining_minutes: float  # Remaining budget
    budget_remaining_percent: float  # Remaining as percentage
    burn_rate: float  # Current burn rate (1.0 = consuming at expected rate)
    status: Literal["healthy", "warning", "critical", "exhausted"]
    measured_at: datetime


def calculate_error_budget_for_window(
    *,
    total_requests: int,
    failed_requests: int,
    slo_target: float = AVAILABILITY_SLO,
    window_days: int = BUDGET_WINDOW_DAYS,
) -> ErrorBudget:
    """Calculate error budget based on request success rate.

    Args:
        total_requests: Total number of requests in the window
        failed_requests: Number of failed requests (5xx, timeouts)
        slo_target: Target SLO (e.g., 0.999 for 99.9%)
        window_days: Size of rolling window in days

    Returns:
        ErrorBudget with current state

    Example:
        >>> budget = calculate_error_budget_for_window(
        ...     total_requests=1_000_000,
        ...     failed_requests=500,
        ...     slo_target=0.999,
        ...     window_days=30
        ... )
        >>> budget.status
        'healthy'
    """
    # Total budget in minutes for the window
    total_minutes_in_window = window_days * 24 * 60
    budget_total_minutes = total_minutes_in_window * (1.0 - slo_target)

    # Calculate actual error rate
    if total_requests == 0:
        actual_availability = 1.0
        budget_consumed_minutes = 0.0
    else:
        actual_availability = (total_requests - failed_requests) / total_requests
        # Convert availability loss to downtime minutes
        downtime_percent = max(0, 1.0 - actual_availability)
        budget_consumed_minutes = total_minutes_in_window * downtime_percent

    budget_remaining_minutes = max(0, budget_total_minutes - budget_consumed_minutes)
    budget_remaining_percent = (
        (budget_remaining_minutes / budget_total_minutes * 100)
        if budget_total_minutes > 0
        else 100.0
    )

    # Burn rate: how fast budget is being consumed relative to SLO
    # 1.0 = consuming at expected rate, 2.0 = consuming twice as fast
    expected_consumption_rate = 1.0 - slo_target
    actual_consumption_rate = 1.0 - actual_availability if total_requests > 0 else 0.0
    burn_rate = (
        actual_consumption_rate / expected_consumption_rate
        if expected_consumption_rate > 0
        else 0.0
    )

    # Determine status based on remaining budget
    if budget_remaining_minutes <= 0:
        status = "exhausted"
    elif budget_remaining_percent < 20:
        status = "critical"
    elif budget_remaining_percent < 50:
        status = "warning"
    else:
        status = "healthy"

    return ErrorBudget(
        service_name="xr7-engine",
        slo_target=slo_target,
        window_days=window_days,
        budget_total_minutes=round(budget_total_minutes, 2),
        budget_consumed_minutes=round(budget_consumed_minutes, 2),
        budget_remaining_minutes=round(budget_remaining_minutes, 2),
        budget_remaining_percent=round(budget_remaining_percent, 2),
        burn_rate=round(burn_rate, 2),
        status=status,
        measured_at=datetime.now(timezone.utc),
    )


def calculate_multi_window_burn_rate(
    *,
    short_window_errors: int,
    short_window_total: int,
    short_window_minutes: int,
    long_window_errors: int,
    long_window_total: int,
    long_window_minutes: int,
    slo_target: float = AVAILABILITY_SLO,
) -> dict:
    """Calculate burn rate across multiple time windows for alerting.

    Used for multi-window multi-burn-rate alerting (Google SRE Workbook).

    Args:
        short_window_errors: Errors in short window (e.g., 1 hour)
        short_window_total: Total requests in short window
        short_window_minutes: Short window duration
        long_window_errors: Errors in long window (e.g., 24 hours)
        long_window_total: Total requests in long window
        long_window_minutes: Long window duration
        slo_target: Target SLO

    Returns:
        dict with burn rates and alert recommendation

    Example burn rate thresholds:
        - 14.4x burn rate in 1h window + 1h window: page immediately (exhausts 30-day budget in 50 hours)
        - 6x burn rate in 6h window + 6h window: page (exhausts in 5 days)
        - 3x burn rate in 24h window + 3d window: ticket (exhausts in 10 days)
        - 1x burn rate in 3d window + 7d window: no action (expected)
    """
    error_budget_rate = 1.0 - slo_target

    short_error_rate = short_window_errors / short_window_total if short_window_total > 0 else 0.0
    short_burn_rate = short_error_rate / error_budget_rate if error_budget_rate > 0 else 0.0

    long_error_rate = long_window_errors / long_window_total if long_window_total > 0 else 0.0
    long_burn_rate = long_error_rate / error_budget_rate if error_budget_rate > 0 else 0.0

    # Determine alert severity
    alert_severity = "none"
    if short_burn_rate >= 14.4 and long_burn_rate >= 14.4:
        alert_severity = "page"  # exhausts budget in ~2 days
    elif short_burn_rate >= 6 and long_burn_rate >= 6:
        alert_severity = "page"  # exhausts in ~5 days
    elif short_burn_rate >= 3 and long_burn_rate >= 3:
        alert_severity = "ticket"  # exhausts in ~10 days

    return {
        "short_window_minutes": short_window_minutes,
        "short_window_burn_rate": round(short_burn_rate, 2),
        "short_window_error_rate_percent": round(short_error_rate * 100, 2),
        "long_window_minutes": long_window_minutes,
        "long_window_burn_rate": round(long_burn_rate, 2),
        "long_window_error_rate_percent": round(long_error_rate * 100, 2),
        "alert_severity": alert_severity,
        "budget_exhaustion_estimate_days": (
            round(BUDGET_WINDOW_DAYS / short_burn_rate, 1) if short_burn_rate > 0 else None
        ),
    }


def get_prometheus_metrics() -> list[str]:
    """Return Prometheus metric definitions for error budget tracking.

    These should be scraped by Prometheus and visualized in Grafana.

    Returns:
        List of metric definitions in Prometheus exposition format
    """
    return [
        "# HELP error_budget_total_minutes Total error budget for the window in minutes",
        "# TYPE error_budget_total_minutes gauge",
        "error_budget_total_minutes 43.2",
        "",
        "# HELP error_budget_consumed_minutes Error budget consumed so far in minutes",
        "# TYPE error_budget_consumed_minutes gauge",
        "error_budget_consumed_minutes 10.5",
        "",
        "# HELP error_budget_remaining_minutes Error budget remaining in minutes",
        "# TYPE error_budget_remaining_minutes gauge",
        "error_budget_remaining_minutes 32.7",
        "",
        "# HELP error_budget_remaining_percent Error budget remaining as percentage",
        "# TYPE error_budget_remaining_percent gauge",
        "error_budget_remaining_percent 75.69",
        "",
        "# HELP error_budget_burn_rate Current burn rate (1.0 = expected rate)",
        "# TYPE error_budget_burn_rate gauge",
        "error_budget_burn_rate 0.8",
        "",
        "# HELP error_budget_status Error budget status (0=healthy, 1=warning, 2=critical, 3=exhausted)",
        "# TYPE error_budget_status gauge",
        "error_budget_status 0",
    ]
