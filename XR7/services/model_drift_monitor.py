from __future__ import annotations

import math
from dataclasses import dataclass

from sqlalchemy.orm import Session

from XR7.models.ml_feedback import MLFeedbackEvent
from xr7_common.logging import get_logger

logger = get_logger(__name__)

try:
    from opentelemetry import metrics

    _meter = metrics.get_meter("xr7.model_drift")
    _drift_score_hist = _meter.create_histogram(
        name="xr7.model_drift.psi",
        unit="1",
        description="Population Stability Index for model prediction drift",
    )
except Exception:  # pragma: no cover
    _drift_score_hist = None


@dataclass(frozen=True)
class DriftResult:
    psi_score: float
    baseline_count: int
    current_count: int
    threshold: float
    drift_detected: bool


def _bucket_index(value: float, bucket_count: int) -> int:
    if bucket_count <= 0:
        return 0
    clipped = max(0.0, min(1.0, float(value)))
    idx = int(clipped * bucket_count)
    return min(bucket_count - 1, idx)


def _distribution(values: list[float], bucket_count: int) -> list[float]:
    if bucket_count <= 0:
        return [1.0]
    counts = [0 for _ in range(bucket_count)]
    for v in values:
        counts[_bucket_index(v, bucket_count)] += 1
    total = sum(counts)
    if total <= 0:
        return [1.0 / bucket_count for _ in range(bucket_count)]
    return [float(c) / float(total) for c in counts]


def _psi(expected: list[float], actual: list[float], epsilon: float = 1e-6) -> float:
    total = 0.0
    for e, a in zip(expected, actual):
        e_adj = max(float(e), epsilon)
        a_adj = max(float(a), epsilon)
        total += (a_adj - e_adj) * math.log(a_adj / e_adj)
    return float(total)


def detect_prediction_drift(
    db: Session,
    *,
    artist_id: str,
    model_version: str | None = None,
    baseline_window: int = 300,
    current_window: int = 100,
    bucket_count: int = 10,
    psi_threshold: float = 0.2,
) -> DriftResult:
    query = db.query(MLFeedbackEvent).filter(MLFeedbackEvent.artist_id == artist_id)
    if model_version:
        query = query.filter(MLFeedbackEvent.model_version == model_version)

    rows = (
        query.filter(MLFeedbackEvent.model_prediction.is_not(None))
        .order_by(MLFeedbackEvent.created_at.desc())
        .limit(max(1, baseline_window + current_window))
        .all()
    )
    if not rows:
        return DriftResult(
            psi_score=0.0,
            baseline_count=0,
            current_count=0,
            threshold=float(psi_threshold),
            drift_detected=False,
        )

    values = [float(r.model_prediction or 0.0) for r in reversed(rows)]
    current_values = values[-current_window:] if len(values) > current_window else values
    baseline_values = values[: max(1, len(values) - len(current_values))]

    expected_dist = _distribution(baseline_values, bucket_count)
    actual_dist = _distribution(current_values, bucket_count)
    psi_score = _psi(expected_dist, actual_dist)
    drift_detected = bool(psi_score >= float(psi_threshold))

    result = DriftResult(
        psi_score=float(round(psi_score, 6)),
        baseline_count=len(baseline_values),
        current_count=len(current_values),
        threshold=float(psi_threshold),
        drift_detected=drift_detected,
    )

    if _drift_score_hist is not None:
        _drift_score_hist.record(
            result.psi_score,
            {
                "artist_id": artist_id,
                "model_version": model_version or "unknown",
                "drift_detected": str(result.drift_detected).lower(),
            },
        )

    if drift_detected:
        logger.warning(
            "Model drift detected",
            extra={
                "artist_id": artist_id,
                "model_version": model_version,
                "psi_score": result.psi_score,
                "threshold": result.threshold,
                "baseline_count": result.baseline_count,
                "current_count": result.current_count,
                "alert_channel": "otel",
            },
        )

    return result
