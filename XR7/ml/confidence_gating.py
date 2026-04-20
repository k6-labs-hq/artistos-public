"""
ML Confidence Gating Service for anomaly detection at scale.

Implements three-tier confidence-based routing to reduce analyst fatigue and
enable automated processing of high-confidence detections.

Tiers:
- REJECT (< 0.30): Discard low-confidence detections, log for calibration
- REVIEW (0.30 - 0.89): Route to analyst queue with priority scoring
- AUTO_ACCEPT (≥ 0.90): Bypass review, create claim seeds automatically

Addresses ML-assisted ingestion intelligence scale target: filters noise,
accelerates high-confidence workflows, prioritizes analyst time on ambiguous cases.

Closes: XR7-407
Domain: ml
Scale-target: ML-assisted anomaly detection with confidence-gated workflows
Compliance: SOC 2 CC7.2 — System monitoring (quality controls on automated decisions)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from xr7_common.logging import get_logger

logger = get_logger(__name__)


class ConfidenceTier(str, Enum):
    """Confidence tier classification for gating decisions."""

    REJECT = "reject"  # < 0.30: Too low to process
    REVIEW = "review"  # 0.30 - 0.89: Analyst review required
    AUTO_ACCEPT = "auto_accept"  # >= 0.90: Auto-process without review


@dataclass
class GatingDecision:
    """Result of confidence gating evaluation."""

    tier: ConfidenceTier
    confidence_score: float
    should_create: bool  # Whether to create anomaly/claim
    requires_review: bool  # Whether to enqueue for analyst
    priority_score: float  # Priority for review queue (0-1, higher = more urgent)
    reasoning: str  # Human-readable explanation
    metadata: dict[str, Any]  # Additional context for logging/metrics


class ConfidenceGatingService:
    """Service for confidence-based anomaly gating and routing.

    Usage:
        >>> gating = ConfidenceGatingService(db_session)
        >>> decision = gating.evaluate(
        ...     confidence=0.92,
        ...     context={"anomaly_type": "RATE_DRIFT", "estimated_recoverable": 5000}
        ... )
        >>> if decision.should_create:
        ...     # Create anomaly
        ...     if decision.requires_review:
        ...         # Enqueue for analyst
        ...     else:
        ...         # Auto-process (create claim seed)
    """

    # Tier thresholds
    REJECT_THRESHOLD = 0.30
    AUTO_ACCEPT_THRESHOLD = 0.90

    # Priority scoring weights
    CONFIDENCE_WEIGHT = 0.40
    AMOUNT_WEIGHT = 0.35
    URGENCY_WEIGHT = 0.25

    def __init__(self, db: Session):
        self.db = db
        self._metrics: dict[str, int] = {
            "total_evaluations": 0,
            "rejected": 0,
            "routed_to_review": 0,
            "auto_accepted": 0,
        }

    def evaluate(
        self,
        confidence: float,
        context: dict[str, Any] | None = None,
    ) -> GatingDecision:
        """Evaluate confidence score and return gating decision.

        Args:
            confidence: ML model confidence score (0-1)
            context: Additional context for priority scoring:
                - anomaly_type (str): Type of anomaly detected
                - estimated_recoverable (float): Estimated dollar amount
                - urgency_flag (bool): Whether detection is time-sensitive
                - artist_id (str): Artist identifier

        Returns:
            GatingDecision with tier, routing, and priority information
        """
        context = context or {}
        self._metrics["total_evaluations"] += 1

        # Validate confidence score
        if not (0.0 <= confidence <= 1.0):
            logger.warning(
                "confidence_out_of_range",
                extra={"confidence": confidence, "clamping_to_range": True},
            )
            confidence = max(0.0, min(1.0, confidence))

        # Classify tier
        if confidence < self.REJECT_THRESHOLD:
            tier = ConfidenceTier.REJECT
            should_create = False
            requires_review = False
            priority_score = 0.0
            reasoning = (
                f"Confidence {confidence:.2f} below rejection threshold {self.REJECT_THRESHOLD}"
            )
            self._metrics["rejected"] += 1

            logger.info(
                "confidence_gating_rejection",
                extra={
                    "confidence": confidence,
                    "threshold": self.REJECT_THRESHOLD,
                    "anomaly_type": context.get("anomaly_type"),
                    "estimated_recoverable": context.get("estimated_recoverable"),
                },
            )

        elif confidence < self.AUTO_ACCEPT_THRESHOLD:
            tier = ConfidenceTier.REVIEW
            should_create = True
            requires_review = True
            priority_score = self._calculate_priority(confidence, context)
            reasoning = (
                f"Confidence {confidence:.2f} requires analyst review "
                f"(threshold: {self.AUTO_ACCEPT_THRESHOLD})"
            )
            self._metrics["routed_to_review"] += 1

            logger.info(
                "confidence_gating_review",
                extra={
                    "confidence": confidence,
                    "priority_score": priority_score,
                    "anomaly_type": context.get("anomaly_type"),
                    "estimated_recoverable": context.get("estimated_recoverable"),
                },
            )

        else:  # confidence >= AUTO_ACCEPT_THRESHOLD
            tier = ConfidenceTier.AUTO_ACCEPT
            should_create = True
            requires_review = False
            priority_score = 1.0  # Highest priority for auto-accepted items
            reasoning = (
                f"Confidence {confidence:.2f} meets auto-accept threshold "
                f"{self.AUTO_ACCEPT_THRESHOLD} - bypassing manual review"
            )
            self._metrics["auto_accepted"] += 1

            logger.info(
                "confidence_gating_auto_accept",
                extra={
                    "confidence": confidence,
                    "anomaly_type": context.get("anomaly_type"),
                    "estimated_recoverable": context.get("estimated_recoverable"),
                    "artist_id": context.get("artist_id"),
                },
            )

        return GatingDecision(
            tier=tier,
            confidence_score=confidence,
            should_create=should_create,
            requires_review=requires_review,
            priority_score=priority_score,
            reasoning=reasoning,
            metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context,
                "thresholds": {
                    "reject": self.REJECT_THRESHOLD,
                    "auto_accept": self.AUTO_ACCEPT_THRESHOLD,
                },
            },
        )

    def _calculate_priority(self, confidence: float, context: dict[str, Any]) -> float:
        """Calculate priority score for review queue placement.

        Higher priority (closer to 1.0) = more urgent for analyst attention.

        Factors:
        - Confidence: Higher confidence = higher priority (less ambiguous)
        - Amount: Larger estimated_recoverable = higher priority
        - Urgency: Time-sensitive flags boost priority

        Returns:
            Priority score in [0, 1]
        """
        # Confidence component: normalize mid-range to [0, 1]
        # 0.30 → 0.0, 0.89 → 1.0
        confidence_range = self.AUTO_ACCEPT_THRESHOLD - self.REJECT_THRESHOLD
        confidence_normalized = (confidence - self.REJECT_THRESHOLD) / confidence_range
        confidence_component = max(0.0, min(1.0, confidence_normalized))

        # Amount component: log scale for estimated_recoverable
        # $1k → 0.2, $10k → 0.5, $50k+ → 1.0
        estimated_recoverable = float(context.get("estimated_recoverable") or 0.0)
        if estimated_recoverable <= 0:
            amount_component = 0.0
        elif estimated_recoverable < 1000:
            amount_component = 0.1
        elif estimated_recoverable < 10000:
            amount_component = 0.5
        elif estimated_recoverable < 50000:
            amount_component = 0.8
        else:
            amount_component = 1.0

        # Urgency component: boolean urgency flags
        urgency_flag = bool(context.get("urgency_flag"))
        urgency_component = 1.0 if urgency_flag else 0.3

        # Weighted combination
        priority = (
            self.CONFIDENCE_WEIGHT * confidence_component
            + self.AMOUNT_WEIGHT * amount_component
            + self.URGENCY_WEIGHT * urgency_component
        )

        return round(min(1.0, max(0.0, priority)), 4)

    def get_metrics(self) -> dict[str, Any]:
        """Get current gating metrics for monitoring/calibration.

        Returns:
            Dict with counts and rates for each tier
        """
        total = self._metrics["total_evaluations"]

        if total == 0:
            return {
                "total_evaluations": 0,
                "rejection_rate": 0.0,
                "review_rate": 0.0,
                "auto_accept_rate": 0.0,
                "counts": self._metrics.copy(),
            }

        return {
            "total_evaluations": total,
            "rejection_rate": round(self._metrics["rejected"] / total, 4),
            "review_rate": round(self._metrics["routed_to_review"] / total, 4),
            "auto_accept_rate": round(self._metrics["auto_accepted"] / total, 4),
            "counts": self._metrics.copy(),
            "thresholds": {
                "reject": self.REJECT_THRESHOLD,
                "auto_accept": self.AUTO_ACCEPT_THRESHOLD,
            },
        }

    def reset_metrics(self) -> None:
        """Reset metrics counters (useful for testing/periodic reporting)."""
        for key in self._metrics:
            self._metrics[key] = 0
