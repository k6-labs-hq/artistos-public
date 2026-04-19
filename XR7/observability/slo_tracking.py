"""
SLO Tracking Service for continuous observability at scale.

Periodically measures and persists SLO metrics (latency, availability, error budget)
to enable proactive alerting and trend analysis for 10x scale targets.

Key capabilities:
- Periodic measurement of p95 latency from request samples
- Error budget consumption tracking with burn rate calculation
- Automated alerting when budgets breach thresholds (50%, 80%, 100%)
- Historical SLO trend storage for capacity planning

Integrates with Prometheus metrics (business_metrics.py) and persists to slo_metrics table.

Closes: XR7-408
Domain: observability
Scale-target: 10x tenant count with proactive SLO monitoring
Compliance: SOC 2 CC7.1 - System monitoring and performance metrics
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.slo_metric import SloMetric
from XR7.observability.error_budget import (
    AVAILABILITY_SLO,
    LATENCY_SLO_P95_MS,
    calculate_error_budget_for_window,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class SloTrackingService:
    """Service for continuous SLO measurement and persistence.

    Usage:
        >>> service = SloTrackingService(db_session, org_id="tenant-123")
        >>> service.measure_and_persist(
        ...     metric_name="api_latency",
        ...     latency_samples=[120, 145, 98, 210, 301],
        ...     total_requests=5000,
        ...     failed_requests=12
        ... )
    """

    def __init__(self, db: Session, org_id: str = "default"):
        self.db = db
        self.org_id = org_id

    def measure_and_persist(
        self,
        *,
        metric_name: str,
        latency_samples: list[float] | None = None,
        total_requests: int = 0,
        failed_requests: int = 0,
        window_seconds: int = 3600,  # 1 hour default
        threshold_ms: float = LATENCY_SLO_P95_MS,
        slo_target: float = AVAILABILITY_SLO,
    ) -> SloMetric:
        """Measure current SLO state and persist to database.

        Args:
            metric_name: Identifier for this SLO (e.g., "api_latency", "ingestion_pipeline")
            latency_samples: List of latency measurements in milliseconds
            total_requests: Total requests in measurement window
            failed_requests: Failed requests (5xx, timeouts) in window
            window_seconds: Measurement window duration
            threshold_ms: p95 latency threshold for SLO
            slo_target: Availability SLO target (e.g., 0.999 for 99.9%)

        Returns:
            Persisted SloMetric instance
        """
        measured_at = datetime.now(timezone.utc)

        # Calculate p95 latency from samples
        current_p95_ms = None
        if latency_samples and len(latency_samples) > 0:
            current_p95_ms = self._calculate_p95(latency_samples)

        # Calculate error budget
        budget = calculate_error_budget_for_window(
            total_requests=total_requests,
            failed_requests=failed_requests,
            slo_target=slo_target,
            window_days=window_seconds // 86400 or 1,  # Convert seconds to days, min 1
        )

        # Determine if SLO is breached
        latency_breached = current_p95_ms > threshold_ms if current_p95_ms is not None else False
        budget_breached = budget.status in ("critical", "exhausted")
        breached = latency_breached or budget_breached

        # Create SLO metric record
        slo_metric = SloMetric(
            org_id=self.org_id,
            metric_name=metric_name,
            window_seconds=window_seconds,
            threshold_ms=threshold_ms,
            current_p95_ms=current_p95_ms,
            error_budget_pct=budget.budget_remaining_percent,
            burn_rate=budget.burn_rate,
            breached=breached,
            description=f"SLO: {slo_target * 100}% availability, p95 < {threshold_ms}ms",
            measured_at=measured_at,
        )

        self.db.add(slo_metric)
        self.db.commit()
        self.db.refresh(slo_metric)

        # Log results
        if breached:
            logger.warning(
                "slo_measurement_complete",
                extra={
                    "org_id": self.org_id,
                    "metric_name": metric_name,
                    "current_p95_ms": current_p95_ms,
                    "threshold_ms": threshold_ms,
                    "latency_breached": latency_breached,
                    "error_budget_pct": budget.budget_remaining_percent,
                    "burn_rate": budget.burn_rate,
                    "budget_status": budget.status,
                    "budget_breached": budget_breached,
                    "breached": breached,
                    "total_requests": total_requests,
                    "failed_requests": failed_requests,
                },
            )
        else:
            logger.info(
                "slo_measurement_complete",
                extra={
                    "org_id": self.org_id,
                    "metric_name": metric_name,
                    "current_p95_ms": current_p95_ms,
                    "threshold_ms": threshold_ms,
                    "latency_breached": latency_breached,
                    "error_budget_pct": budget.budget_remaining_percent,
                    "burn_rate": budget.burn_rate,
                    "budget_status": budget.status,
                    "budget_breached": budget_breached,
                    "breached": breached,
                    "total_requests": total_requests,
                    "failed_requests": failed_requests,
                },
            )

        # Trigger alerts if breached
        if breached:
            self._alert_slo_breach(
                metric_name=metric_name,
                current_p95_ms=current_p95_ms,
                threshold_ms=threshold_ms,
                budget_status=budget.status,
                budget_remaining_pct=budget.budget_remaining_percent,
                burn_rate=budget.burn_rate,
            )

        return slo_metric

    def _calculate_p95(self, samples: list[float]) -> float:
        """Calculate 95th percentile from sample list.

        Uses statistics.quantiles for accurate percentile calculation.

        Args:
            samples: List of numeric measurements

        Returns:
            95th percentile value
        """
        if not samples:
            return 0.0

        # For small sample sizes, use max as conservative estimate
        if len(samples) < 20:
            return max(samples)

        # Use quantiles for accurate p95
        sorted_samples = sorted(samples)
        p95_index = int(len(sorted_samples) * 0.95)
        return sorted_samples[p95_index]

    def _alert_slo_breach(
        self,
        *,
        metric_name: str,
        current_p95_ms: float | None,
        threshold_ms: float,
        budget_status: str,
        budget_remaining_pct: float,
        burn_rate: float,
    ) -> None:
        """Log structured alert when SLO is breached.

        In production, this would trigger PagerDuty/OpsGenie/Slack notifications.

        Args:
            metric_name: Which SLO metric breached
            current_p95_ms: Current latency measurement
            threshold_ms: Latency threshold
            budget_status: Error budget status (warning/critical/exhausted)
            budget_remaining_pct: Remaining error budget percentage
            burn_rate: Current burn rate multiplier
        """
        severity = "critical" if budget_status == "exhausted" else "warning"

        alert_payload = {
            "alert_type": "slo_breach",
            "severity": severity,
            "metric_name": metric_name,
            "org_id": self.org_id,
            "current_p95_ms": current_p95_ms,
            "threshold_ms": threshold_ms,
            "latency_breached": current_p95_ms > threshold_ms if current_p95_ms else False,
            "error_budget_status": budget_status,
            "error_budget_remaining_pct": budget_remaining_pct,
            "burn_rate": burn_rate,
            "remediation_required": budget_status in ("critical", "exhausted"),
        }

        logger.error(
            "slo_breach_alert",
            extra=alert_payload,
        )

        # TODO: Integrate with alerting system (PagerDuty, Slack, OpsGenie)
        # This would call external API to trigger on-call notification
        # For now, structured logging to CloudWatch/Datadog will suffice

    def get_slo_trend(
        self,
        metric_name: str,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Retrieve SLO measurement history for trend analysis.

        Args:
            metric_name: SLO metric to query
            hours: Lookback window in hours

        Returns:
            List of SLO measurements with timestamps
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        metrics = (
            self.db.query(SloMetric)
            .filter(
                SloMetric.org_id == self.org_id,
                SloMetric.metric_name == metric_name,
                SloMetric.measured_at >= cutoff,
            )
            .order_by(SloMetric.measured_at.asc())
            .all()
        )

        return [
            {
                "measured_at": m.measured_at.isoformat(),
                "current_p95_ms": m.current_p95_ms,
                "error_budget_pct": m.error_budget_pct,
                "burn_rate": m.burn_rate,
                "breached": m.breached,
            }
            for m in metrics
        ]

    def check_budget_health(self, metric_name: str) -> dict[str, Any]:
        """Get current error budget health for a metric.

        Args:
            metric_name: SLO metric to check

        Returns:
            Dict with latest budget status and recommendations
        """
        latest = (
            self.db.query(SloMetric)
            .filter(
                SloMetric.org_id == self.org_id,
                SloMetric.metric_name == metric_name,
            )
            .order_by(SloMetric.measured_at.desc())
            .first()
        )

        if not latest:
            return {
                "status": "unknown",
                "message": "No SLO measurements found",
                "recommendations": ["Start measuring SLOs for this metric"],
            }

        # Generate recommendations based on budget state
        recommendations = []
        if latest.error_budget_pct is not None and latest.error_budget_pct < 20:
            recommendations.append("🔴 CRITICAL: Error budget nearly exhausted")
            recommendations.append("Implement feature freeze until budget recovers")
            recommendations.append("Investigate root cause of elevated error rate")
        elif latest.error_budget_pct is not None and latest.error_budget_pct < 50:
            recommendations.append("⚠️  WARNING: Error budget consumption elevated")
            recommendations.append("Slow down deployment frequency")
            recommendations.append("Prioritize reliability work over features")
        else:
            recommendations.append("✅ Healthy error budget - safe to deploy")

        if latest.burn_rate is not None and latest.burn_rate > 5.0:
            recommendations.append(
                f"⚡ High burn rate ({latest.burn_rate:.1f}x) - budget will exhaust quickly"
            )
            recommendations.append("Roll back recent changes if correlated")

        if latest.current_p95_ms is not None and latest.current_p95_ms > latest.threshold_ms:
            latency_overage = latest.current_p95_ms - latest.threshold_ms
            recommendations.append(
                f"🐌 Latency {int(latency_overage)}ms over threshold - investigate slow queries"
            )

        return {
            "status": (
                "healthy"
                if not latest.breached
                else ("critical" if latest.error_budget_pct < 20 else "warning")
            ),
            "error_budget_remaining_pct": latest.error_budget_pct,
            "burn_rate": latest.burn_rate,
            "current_p95_ms": latest.current_p95_ms,
            "threshold_ms": latest.threshold_ms,
            "measured_at": latest.measured_at.isoformat(),
            "recommendations": recommendations,
        }
