from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.ml_feedback import MLFeedbackType
from XR7.models.review_queue import (
    ReviewAssignment,
    ReviewAssignmentSchema,
    ReviewDecision,
    ReviewDecisionSchema,
    ReviewDecisionType,
    ReviewItem,
    ReviewItemSchema,
    ReviewItemStatus,
    ReviewSourceType,
)
from XR7.services.ml_feedback import ingest_feedback_event
from XR7.services.review_queue import enqueue_review_item, queue_metrics

router = APIRouter(prefix="/review-queue", tags=["review_queue"])


def _require_analyst(
    x_analyst_key: str = Header(default="", alias="X-Analyst-Key"),
    x_analyst_email: str = Header(default="", alias="X-Analyst-Email"),
) -> str:
    expected = os.environ.get("ANALYST_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Analyst API key is not configured.")
    if not x_analyst_key or not hmac.compare_digest(x_analyst_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing analyst key.")
    email = x_analyst_email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="X-Analyst-Email header is required.")
    return email


class CreateReviewItemRequest(BaseModel):
    artist_id: str
    source_type: ReviewSourceType
    source_id: str | None = None
    reason: str
    priority_score: float = 0.0
    payload: dict | None = None


class AssignReviewItemRequest(BaseModel):
    analyst_email: str


class DecideReviewItemRequest(BaseModel):
    decision: ReviewDecisionType
    notes: str | None = None


@router.post("/items", response_model=ReviewItemSchema, status_code=201)
def create_review_item(
    payload: CreateReviewItemRequest,
    _: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    item = enqueue_review_item(
        db,
        artist_id=payload.artist_id,
        source_type=payload.source_type,
        source_id=payload.source_id,
        reason=payload.reason,
        priority_score=payload.priority_score,
        payload=payload.payload,
    )
    return item


@router.get("/items", response_model=list[ReviewItemSchema])
def list_review_items(
    status: str | None = Query(default=None),
    artist_id: str | None = Query(default=None),
    assigned_analyst_email: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    query = db.query(ReviewItem)
    if status:
        query = query.filter(ReviewItem.status == status)
    if artist_id:
        query = query.filter(ReviewItem.artist_id == artist_id)
    if assigned_analyst_email:
        query = query.filter(
            ReviewItem.assigned_analyst_email == assigned_analyst_email.strip().lower()
        )
    return (
        query.order_by(ReviewItem.priority_score.desc(), ReviewItem.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/items/{item_id}/assign", response_model=ReviewAssignmentSchema)
def assign_review_item(
    item_id: str,
    payload: AssignReviewItemRequest,
    actor_email: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    item = db.query(ReviewItem).filter(ReviewItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")

    analyst_email = payload.analyst_email.strip().lower()
    if "@" not in analyst_email:
        raise HTTPException(status_code=422, detail="Invalid analyst email")

    # Close previous open assignment for this item.
    prev = (
        db.query(ReviewAssignment)
        .filter(
            ReviewAssignment.review_item_id == item_id, ReviewAssignment.unassigned_at.is_(None)
        )
        .first()
    )
    if prev:
        prev.unassigned_at = datetime.now(timezone.utc)

    assignment = ReviewAssignment(review_item_id=item_id, analyst_email=analyst_email)
    item.assigned_analyst_email = analyst_email
    item.status = ReviewItemStatus.IN_REVIEW.value
    item.updated_at = datetime.now(timezone.utc)

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    # actor_email is currently only used for authentication/auditing at gateway layer.
    _ = actor_email
    return assignment


@router.post("/items/{item_id}/decision", response_model=ReviewDecisionSchema)
def decide_review_item(
    item_id: str,
    payload: DecideReviewItemRequest,
    analyst_email: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    item = db.query(ReviewItem).filter(ReviewItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")

    decision = ReviewDecision(
        review_item_id=item_id,
        analyst_email=analyst_email,
        decision=payload.decision.value,
        notes=payload.notes,
    )
    db.add(decision)

    if payload.decision in {ReviewDecisionType.APPROVE, ReviewDecisionType.REJECT}:
        item.status = ReviewItemStatus.RESOLVED.value
        item.resolved_at = datetime.now(timezone.utc)
    elif payload.decision == ReviewDecisionType.ESCALATE:
        item.status = ReviewItemStatus.OPEN.value
    else:
        item.status = ReviewItemStatus.IN_REVIEW.value
    item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(decision)

    ingest_feedback_event(
        db,
        artist_id=item.artist_id,
        feedback_type=MLFeedbackType.REVIEW_DECISION,
        source_type=item.source_type,
        source_id=item.source_id,
        anomaly_id=item.source_id if item.source_type == "ANOMALY" else None,
        claim_id=item.source_id if item.source_type == "CLAIM" else None,
        subtype=(item.payload or {}).get("subtype"),
        category=(item.payload or {}).get("category"),
        model_version=(item.payload or {}).get("model_version"),
        model_prediction=(item.payload or {}).get("model_prediction"),
        human_decision=payload.decision.value,
        outcome=payload.decision.value,
        estimated_amount=(item.payload or {}).get("estimated_amount") or item.priority_score,
        actual_amount=(item.payload or {}).get("actual_amount"),
        payload={"notes": payload.notes, "review_item_id": item.id},
    )
    return decision


@router.get("/decisions", response_model=list[ReviewDecisionSchema])
def list_decisions(
    item_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    query = db.query(ReviewDecision)
    if item_id:
        query = query.filter(ReviewDecision.review_item_id == item_id)
    return query.order_by(ReviewDecision.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/metrics")
def review_queue_metrics(
    _: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    metrics = queue_metrics(db)
    by_source = (
        db.query(ReviewItem.source_type, func.count(ReviewItem.id))
        .filter(
            ReviewItem.status.in_([ReviewItemStatus.OPEN.value, ReviewItemStatus.IN_REVIEW.value])
        )
        .group_by(ReviewItem.source_type)
        .all()
    )
    metrics["by_source"] = {source: int(count) for source, count in by_source}

    analyst_rows = (
        db.query(ReviewDecision.analyst_email, func.count(ReviewDecision.id))
        .group_by(ReviewDecision.analyst_email)
        .all()
    )
    per_analyst = []
    for analyst_email, decision_count in analyst_rows:
        overrides = (
            db.query(func.count(ReviewDecision.id))
            .filter(
                ReviewDecision.analyst_email == analyst_email,
                ReviewDecision.decision.in_(["ESCALATE", "REJECT"]),
            )
            .scalar()
            or 0
        )
        agreement = max(0.0, 1.0 - (float(overrides) / max(float(decision_count), 1.0)))
        per_analyst.append(
            {
                "analyst_email": analyst_email,
                "decision_count": int(decision_count),
                "override_rate": round(float(overrides) / max(float(decision_count), 1.0), 6),
                "agreement_with_model": round(agreement, 6),
            }
        )
    metrics["per_analyst_calibration"] = per_analyst
    return metrics


@router.post("/threshold-check")
def check_threshold(
    _: str = Depends(_require_analyst),
    db: Session = Depends(get_db),
):
    metrics = queue_metrics(db)
    return {
        "alert": metrics["threshold_exceeded"],
        **metrics,
        "message": (
            "Review queue threshold exceeded. Notify analyst on-call rotation."
            if metrics["threshold_exceeded"]
            else "Review queue is within normal operating threshold."
        ),
    }
