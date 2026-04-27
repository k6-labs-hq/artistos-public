"""ML Confidence Gating Service for anomaly triage.

Provides tiered confidence-based filtering to automatically triage detected
anomalies into:
- REJECT: Too low confidence, don't create anomaly
- REVIEW: Medium confidence, send to manual review queue
- AUTO_ACCEPT: High confidence, bypass manual review

This reduces analyst workload by filtering out noise and auto-approving
high-confidence detections.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session

from xr7_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Decision tiers
# ---------------------------------------------------------------------------


class ConfidenceTier(str, Enum):
    """Confidence-based decision tiers for anomaly triage."""

    REJECT = "REJECT"  # Below minimum threshold, don't create
    REVIEW = "REVIEW"  # Medium confidence, needs manual review
    AUTO_ACCEPT = "AUTO_ACCEPT"  # High confidence, bypass review


# ---------------------------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------------------------

# Minimum confidence to create an anomaly at all
MIN_CONFIDENCE = 0.50

# High confidence threshold for auto-accept (bypass manual review)
AUTO_ACCEPT_THRESHOLD = 0.90

# Urgency boost: high-value or urgent anomalies get lower threshold
URGENT_AUTO_ACCEPT_THRESHOLD = 0.75


# ---------------------------------------------------------------------------
# Gating decision
# ---------------------------------------------------------------------------


@dataclass
class GatingDecision:
    """Result of confidence gating evaluation."""

    tier: ConfidenceTier
    should_create: bool
    requires_review: bool
    priority_score: float
    reasoning: str


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class ConfidenceGatingService:
    """Service for confidence-based anomaly triage.

    Applies ML confidence thresholds to automatically filter and route
    detected anomalies based on confidence scores and contextual factors.

    Usage::

        gating = ConfidenceGatingService(db)

        decision = gating.evaluate(
            confidence=0.87,
            context={
                "anomaly_type": "MISSING_PAYMENT",
                "estimated_recoverable": 1250.0,
                "artist_id": "art_xyz",
                "urgency_flag": False,
            }
        )

        if decision.should_create:
            if decision.requires_review:
                enqueue_for_review()
            else:
                auto_accept()

        metrics = gating.get_metrics()
    """

    def __init__(self, db: Session) -> None:
        """Initialize gating service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

        # Metrics tracking
        self._total_evaluated = 0
        self._rejected_count = 0
        self._review_count = 0
        self._auto_accept_count = 0

    def evaluate(
        self,
        confidence: float,
        context: dict | None = None,
    ) -> GatingDecision:
        """Evaluate whether to create/route an anomaly based on confidence.

        Args:
            confidence: ML confidence score (0.0 to 1.0)
            context: Optional context with:
                - anomaly_type: str (e.g., "MISSING_PAYMENT")
                - estimated_recoverable: float (dollar amount)
                - artist_id: str
                - urgency_flag: bool (whether anomaly is urgent/time-sensitive)

        Returns:
            GatingDecision with tier, routing instructions, and reasoning
        """
        context = context or {}
        self._total_evaluated += 1

        # Extract context
        urgency_flag = context.get("urgency_flag", False)
        estimated_recoverable = float(context.get("estimated_recoverable", 0.0))

        # Compute priority score (0-100)
        # Factors: confidence (70%), dollar amount (20%), urgency (10%)
        priority_score = (
            confidence * 70.0
            + min(estimated_recoverable / 10000.0, 1.0) * 20.0
            + (10.0 if urgency_flag else 0.0)
        )

        # Decision logic

        # REJECT: Below minimum threshold
        if confidence < MIN_CONFIDENCE:
            self._rejected_count += 1
            return GatingDecision(
                tier=ConfidenceTier.REJECT,
                should_create=False,
                requires_review=False,
                priority_score=priority_score,
                reasoning=(
                    f"Confidence {confidence:.2f} below minimum threshold " f"{MIN_CONFIDENCE:.2f}"
                ),
            )

        # AUTO_ACCEPT: High confidence
        auto_threshold = URGENT_AUTO_ACCEPT_THRESHOLD if urgency_flag else AUTO_ACCEPT_THRESHOLD

        if confidence >= auto_threshold:
            self._auto_accept_count += 1
            threshold_type = "urgent" if urgency_flag else "standard"
            return GatingDecision(
                tier=ConfidenceTier.AUTO_ACCEPT,
                should_create=True,
                requires_review=False,
                priority_score=priority_score,
                reasoning=(
                    f"Confidence {confidence:.2f} meets {threshold_type} "
                    f"auto-accept threshold {auto_threshold:.2f}"
                ),
            )

        # REVIEW: Medium confidence, needs manual review
        self._review_count += 1
        return GatingDecision(
            tier=ConfidenceTier.REVIEW,
            should_create=True,
            requires_review=True,
            priority_score=priority_score,
            reasoning=(
                f"Confidence {confidence:.2f} in review range "
                f"({MIN_CONFIDENCE:.2f} to {auto_threshold:.2f})"
            ),
        )

    def get_metrics(self) -> dict:
        """Get gating metrics for monitoring.

        Returns:
            Dict with counts and rates for rejected/review/auto-accept tiers
        """
        total = self._total_evaluated

        if total == 0:
            return {
                "total_evaluated": 0,
                "rejected_count": 0,
                "review_count": 0,
                "auto_accept_count": 0,
                "reject_rate": 0.0,
                "review_rate": 0.0,
                "auto_accept_rate": 0.0,
            }

        return {
            "total_evaluated": total,
            "rejected_count": self._rejected_count,
            "review_count": self._review_count,
            "auto_accept_count": self._auto_accept_count,
            "reject_rate": self._rejected_count / total,
            "review_rate": self._review_count / total,
            "auto_accept_rate": self._auto_accept_count / total,
        }
