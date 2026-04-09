from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.ml_feedback import CalibrationSnapshot, MLFeedbackEvent, MLFeedbackType

_ALPHA_PRIOR = 2.0
_BETA_PRIOR = 2.0


@dataclass
class FeedbackCounters:
    success: int = 0
    failure: int = 0

    @property
    def sample_count(self) -> int:
        return int(self.success + self.failure)


def _is_success(row: MLFeedbackEvent) -> bool | None:
    outcome = str(row.outcome or "").upper()
    decision = str(row.human_decision or "").upper()

    if outcome in {"RECOVERED", "SETTLED", "ACCEPTED", "PAID", "APPROVE"}:
        return True
    if outcome in {"DISMISSED", "REJECTED", "ABANDONED", "FAILED", "REJECT"}:
        return False
    if decision in {"APPROVE", "CONFIRM"}:
        return True
    if decision in {"REJECT", "OVERRIDE", "DISMISS"}:
        return False
    if row.estimated_amount is not None and row.actual_amount is not None:
        # Consider effective outcome successful if realized recovery is at least half of estimate.
        return float(row.actual_amount) >= 0.5 * float(row.estimated_amount)
    return None


def _wilson_interval(success: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 1.0
    p = success / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return lo, hi


def _upsert_snapshot(
    db: Session,
    artist_id: str,
    scope_type: str,
    scope_key: str,
    counters: FeedbackCounters,
) -> CalibrationSnapshot:
    row = (
        db.query(CalibrationSnapshot)
        .filter(
            CalibrationSnapshot.artist_id == artist_id,
            CalibrationSnapshot.scope_type == scope_type,
            CalibrationSnapshot.scope_key == scope_key,
        )
        .first()
    )
    if not row:
        row = CalibrationSnapshot(artist_id=artist_id, scope_type=scope_type, scope_key=scope_key)
        db.add(row)

    alpha = _ALPHA_PRIOR + counters.success
    beta = _BETA_PRIOR + counters.failure
    posterior_mean = alpha / (alpha + beta)
    lo, hi = _wilson_interval(counters.success, max(counters.sample_count, 1))

    row.alpha = float(alpha)
    row.beta = float(beta)
    row.sample_count = int(counters.sample_count)
    row.success_count = int(counters.success)
    row.failure_count = int(counters.failure)
    row.posterior_mean = float(posterior_mean)
    row.lower_credible = float(lo)
    row.upper_credible = float(hi)
    row.last_updated_at = datetime.now(timezone.utc)
    return row


def aggregate_feedback_and_update_calibration(artist_id: str, db: Session) -> dict:
    rows = db.query(MLFeedbackEvent).filter(MLFeedbackEvent.artist_id == artist_id).all()

    overall = FeedbackCounters()
    by_subtype: dict[str, FeedbackCounters] = {}
    by_category: dict[str, FeedbackCounters] = {}
    by_segment: dict[str, FeedbackCounters] = {}

    for row in rows:
        success = _is_success(row)
        if success is None:
            continue
        if success:
            overall.success += 1
        else:
            overall.failure += 1

        if row.subtype:
            bucket = by_subtype.setdefault(str(row.subtype), FeedbackCounters())
            if success:
                bucket.success += 1
            else:
                bucket.failure += 1
        if row.category:
            bucket = by_category.setdefault(str(row.category), FeedbackCounters())
            if success:
                bucket.success += 1
            else:
                bucket.failure += 1
        if row.artist_profile_segment:
            bucket = by_segment.setdefault(str(row.artist_profile_segment), FeedbackCounters())
            if success:
                bucket.success += 1
            else:
                bucket.failure += 1

    _upsert_snapshot(db, artist_id, "overall", "overall", overall)
    for key, counters in by_subtype.items():
        _upsert_snapshot(db, artist_id, "subtype", key, counters)
    for key, counters in by_category.items():
        _upsert_snapshot(db, artist_id, "category", key, counters)
    for key, counters in by_segment.items():
        _upsert_snapshot(db, artist_id, "segment", key, counters)

    db.commit()
    return {
        "artist_id": artist_id,
        "event_count": len(rows),
        "overall_sample_count": overall.sample_count,
        "updated_scopes": {
            "subtype": len(by_subtype),
            "category": len(by_category),
            "segment": len(by_segment),
        },
    }


def ingest_feedback_event(
    db: Session,
    *,
    artist_id: str,
    feedback_type: MLFeedbackType,
    source_type: str | None = None,
    source_id: str | None = None,
    anomaly_id: str | None = None,
    claim_id: str | None = None,
    subtype: str | None = None,
    category: str | None = None,
    artist_profile_segment: str | None = None,
    model_version: str | None = None,
    model_prediction: float | None = None,
    human_decision: str | None = None,
    outcome: str | None = None,
    estimated_amount: float | None = None,
    actual_amount: float | None = None,
    payload: dict | None = None,
) -> MLFeedbackEvent:
    row = MLFeedbackEvent(
        artist_id=artist_id,
        feedback_type=feedback_type.value,
        source_type=source_type,
        source_id=source_id,
        anomaly_id=anomaly_id,
        claim_id=claim_id,
        subtype=subtype,
        category=category,
        artist_profile_segment=artist_profile_segment,
        model_version=model_version,
        model_prediction=model_prediction,
        human_decision=human_decision,
        outcome=outcome,
        estimated_amount=estimated_amount,
        actual_amount=actual_amount,
        payload=payload or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
