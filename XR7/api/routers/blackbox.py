"""
Black-Box / Unclaimed Royalties — API endpoints.

GET  /artists/{artist_id}/blackbox/matches
POST /artists/{artist_id}/blackbox/scan   (on-demand trigger)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_artist_access
from XR7.models.base import get_db
from XR7.models.blackbox_match import (
    BlackboxMatch,
    BlackboxMatchSchema,
    BlackboxMatchStatus,
)

router = APIRouter(tags=["blackbox"])


# ---------------------------------------------------------------------------
# Response / request schemas
# ---------------------------------------------------------------------------


class BlackboxMatchListResponse(BaseModel):
    artist_id: str
    matches: list[BlackboxMatchSchema]
    total: int
    total_value_low: float
    total_value_high: float


class BlackboxScanTriggerResponse(BaseModel):
    artist_id: str
    task_id: str | None
    status: str
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/blackbox/matches",
    response_model=BlackboxMatchListResponse,
    summary="List black-box / unclaimed royalty matches for the artist",
)
def list_blackbox_matches(
    artist_id: str,
    status: BlackboxMatchStatus | None = Query(default=None, description="Filter by match status"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> BlackboxMatchListResponse:
    get_artist_or_404(artist_id, db)

    q = db.query(BlackboxMatch).filter(BlackboxMatch.artist_id == artist_id)
    if status is not None:
        q = q.filter(BlackboxMatch.status == status.value)

    rows: list[BlackboxMatch] = q.order_by(BlackboxMatch.created_at.desc()).all()
    schemas = [BlackboxMatchSchema.model_validate(r) for r in rows]

    total_low = sum(float(r.amount_range_low) for r in rows)
    total_high = sum(float(r.amount_range_high) for r in rows)

    return BlackboxMatchListResponse(
        artist_id=artist_id,
        matches=schemas,
        total=len(schemas),
        total_value_low=round(total_low, 2),
        total_value_high=round(total_high, 2),
    )


@router.post(
    "/artists/{artist_id}/blackbox/scan",
    response_model=BlackboxScanTriggerResponse,
    summary="Trigger an on-demand black-box scan for this artist",
)
def trigger_blackbox_scan(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> BlackboxScanTriggerResponse:
    get_artist_or_404(artist_id, db)

    try:
        from XR7.tasks.blackbox import scan_artist_blackbox
        result = scan_artist_blackbox.delay(artist_id)
        task_id = str(result.id) if result else None
        return BlackboxScanTriggerResponse(
            artist_id=artist_id,
            task_id=task_id,
            status="queued",
            message="Black-box scan queued. Results will appear in /blackbox/matches within minutes.",
        )
    except Exception:
        # Celery unavailable (e.g. tests without broker) — run inline
        from XR7.tasks.blackbox import run_blackbox_scan
        summary = run_blackbox_scan(artist_id, db)
        return BlackboxScanTriggerResponse(
            artist_id=artist_id,
            task_id=None,
            status="completed_inline",
            message=(
                f"Scan completed: {summary.get('new_matches', 0)} new matches found "
                f"(${summary.get('total_value_low', 0):,.0f}–"
                f"${summary.get('total_value_high', 0):,.0f})."
            ),
        )
