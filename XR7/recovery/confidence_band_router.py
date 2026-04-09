"""Confidence-band driven anomaly routing service.

Routes anomalies to appropriate review queues, case creation, and automated
workflows based on confidence bands per the unified confidence scoring framework.

Bands:
- High: C >= 0.90 -> Auto-link or auto-case create per policy
- Medium: 0.70 <= C < 0.90 -> Analyst review queue
- Low: C < 0.70 -> Unmatched/watchlist queue with clustering
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from XR7.core.scoring.confidence_band import HIGH, MEDIUM, classify_band
from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.review_queue import ReviewSourceType
from XR7.services.review_queue import enqueue_review_item
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class ConfidenceBandRouter:
    """Routes anomalies to appropriate workflows based on confidence bands."""

    # Thresholds are defined in XR7.core.scoring.confidence_band; re-exported
    # here as class attributes for backwards-compatible callers.
    HIGH_CONFIDENCE_THRESHOLD = HIGH
    MEDIUM_CONFIDENCE_THRESHOLD = MEDIUM

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def classify_band(confidence: float) -> str:
        """Delegates to the pure core implementation."""
        return classify_band(confidence)

    def route_anomaly(
        self,
        anomaly_id: str,
        artist_id: str,
        confidence: float,
        estimated_recoverable: float | None = None,
        anomaly_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route an anomaly to appropriate workflow based on confidence band.

        Args:
            anomaly_id: Anomaly ID
            artist_id: Artist ID
            confidence: Confidence score (0-1)
            estimated_recoverable: Estimated recoverable amount
            anomaly_payload: Full anomaly payload for logging

        Returns:
            Routing result {'band': str, 'actions': list[str], 'case_id': str | None}
        """
        band = self.classify_band(confidence)
        payload = anomaly_payload or {}
        actions = []
        case_id = None
        estimate_recoverable = estimated_recoverable or 0.0

        try:
            if band == "high":
                # High confidence: auto-create case if policy allows
                actions.append("auto_case_create")
                case_id = self._auto_create_case(anomaly_id, artist_id, payload)
                actions.append(f"case_created:{case_id}" if case_id else "case_creation_deferred")

            elif band == "medium":
                # Medium confidence: enqueue to analyst review
                actions.append("enqueue_analyst_review")
                self._enqueue_analyst_review(anomaly_id, artist_id, confidence, estimate_recoverable, payload)

            else:  # band == "low"
                # Low confidence: enqueue to watchlist/unmatched
                actions.append("enqueue_watchlist")
                self._enqueue_watchlist(anomaly_id, artist_id, confidence, estimate_recoverable, payload)

            return {
                "band": band,
                "actions": actions,
                "case_id": case_id,
            }
        except Exception as e:
            logger.exception(f"Confidence-band routing failed for anomaly {anomaly_id}", extra={"band": band})
            return {
                "band": band,
                "actions": [f"routing_error:{str(e)}"],
                "case_id": None,
            }

    def _auto_create_case(self, anomaly_id: str, artist_id: str, payload: dict[str, Any]) -> str | None:
        """Auto-create a case for high-confidence anomalies."""
        try:
            case = Claim(
                id=f"claim-{anomaly_id[:16]}",
                artist_id=artist_id,
                anomaly_id=anomaly_id,
                status=ClaimStatus.DRAFT,
                claim_type="RECOVERY",
                estimated_amount=payload.get("estimated_recoverable", 0.0),
                description=f"Auto-created from high-confidence anomaly: {payload.get('category', 'UNKNOWN')}",
            )
            self.db.add(case)
            self.db.commit()
            logger.info(
                "Auto-created case for high-confidence anomaly",
                extra={"case_id": case.id, "anomaly_id": anomaly_id, "artist_id": artist_id},
            )
            return case.id
        except Exception as e:
            logger.exception(f"Failed to auto-create case for anomaly {anomaly_id}", extra={"error": str(e)})
            return None

    def _enqueue_analyst_review(
        self,
        anomaly_id: str,
        artist_id: str,
        confidence: float,
        estimated_recoverable: float,
        payload: dict[str, Any],
    ) -> None:
        """Enqueue anomaly for analyst review (medium confidence)."""
        try:
            reason = f"Medium-confidence anomaly ({confidence:.2%}) requires analyst review: {payload.get('category', 'UNKNOWN')}"
            enqueue_review_item(
                self.db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ANOMALY,
                source_id=anomaly_id,
                reason=reason,
                priority_score=estimated_recoverable,
                payload=payload,
            )
            logger.info(
                "Enqueued anomaly for analyst review",
                extra={
                    "anomaly_id": anomaly_id,
                    "artist_id": artist_id,
                    "confidence": confidence,
                },
            )
        except Exception as e:
            logger.exception(
                f"Failed to enqueue anomaly for analyst review",
                extra={"anomaly_id": anomaly_id, "error": str(e)},
            )

    def _enqueue_watchlist(
        self,
        anomaly_id: str,
        artist_id: str,
        confidence: float,
        estimated_recoverable: float,
        payload: dict[str, Any],
    ) -> None:
        """Enqueue anomaly to watchlist (low confidence)."""
        try:
            reason = (
                f"Low-confidence anomaly ({confidence:.2%}) added to watchlist for trending analysis: "
                f"{payload.get('category', 'UNKNOWN')}"
            )
            enqueue_review_item(
                self.db,
                artist_id=artist_id,
                source_type=ReviewSourceType.WATCHLIST,
                source_id=anomaly_id,
                reason=reason,
                priority_score=estimated_recoverable,
                payload=payload,
            )
            logger.info(
                "Enqueued anomaly to watchlist",
                extra={
                    "anomaly_id": anomaly_id,
                    "artist_id": artist_id,
                    "confidence": confidence,
                },
            )
        except Exception as e:
            logger.exception(
                f"Failed to enqueue anomaly to watchlist",
                extra={"anomaly_id": anomaly_id, "error": str(e)},
            )

    def route_batch(self, anomalies: list[dict[str, Any]]) -> dict[str, Any]:
        """Route a batch of anomalies and aggregate results.

        Args:
            anomalies: List of anomaly dicts with id, artist_id, confidence_score, estimated_recoverable

        Returns:
            Aggregated routing metrics
        """
        results = {
            "total": len(anomalies),
            "high_count": 0,
            "high_cases_created": 0,
            "medium_count": 0,
            "low_count": 0,
            "errors": [],
        }

        for anom in anomalies:
            try:
                route_result = self.route_anomaly(
                    anomaly_id=anom.get("id"),
                    artist_id=anom.get("artist_id"),
                    confidence=float(anom.get("confidence_score") or 0.0),
                    estimated_recoverable=anom.get("estimated_recoverable"),
                    anomaly_payload=anom,
                )

                band = route_result.get("band")
                if band == "high":
                    results["high_count"] += 1
                    if route_result.get("case_id"):
                        results["high_cases_created"] += 1
                elif band == "medium":
                    results["medium_count"] += 1
                else:
                    results["low_count"] += 1

            except Exception as e:
                logger.exception(f"Failed to route anomaly {anom.get('id')}")
                results["errors"].append(str(e))

        return results
