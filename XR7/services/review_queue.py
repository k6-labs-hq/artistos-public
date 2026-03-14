from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.review_queue import ReviewItem, ReviewItemStatus, ReviewSourceType


def enqueue_review_item(
    db: Session,
    *,
    artist_id: str,
    source_type: ReviewSourceType,
    source_id: str | None,
    reason: str,
    priority_score: float = 0.0,
    payload: dict | None = None,
) -> ReviewItem:
    """Create or upsert an open review item for a given source."""
    existing = None
    if source_id:
        existing = (
            db.query(ReviewItem)
            .filter(
                ReviewItem.artist_id == artist_id,
                ReviewItem.source_type == source_type.value,
                ReviewItem.source_id == source_id,
                ReviewItem.status.in_([ReviewItemStatus.OPEN.value, ReviewItemStatus.IN_REVIEW.value]),
            )
            .first()
        )

    if existing:
        existing.reason = reason
        existing.priority_score = max(float(existing.priority_score or 0.0), float(priority_score or 0.0))
        existing.payload = payload or existing.payload
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    item = ReviewItem(
        artist_id=artist_id,
        source_type=source_type.value,
        source_id=source_id,
        reason=reason,
        priority_score=float(priority_score or 0.0),
        status=ReviewItemStatus.OPEN.value,
        payload=payload or {},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def queue_metrics(db: Session) -> dict:
    open_count = db.query(func.count(ReviewItem.id)).filter(ReviewItem.status == ReviewItemStatus.OPEN.value).scalar() or 0
    in_review_count = (
        db.query(func.count(ReviewItem.id)).filter(ReviewItem.status == ReviewItemStatus.IN_REVIEW.value).scalar() or 0
    )
    threshold = int(os.environ.get("REVIEW_QUEUE_ALERT_THRESHOLD", "25"))
    return {
        "open_count": int(open_count),
        "in_review_count": int(in_review_count),
        "alert_threshold": threshold,
        "threshold_exceeded": int(open_count) >= threshold,
    }
