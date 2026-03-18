"""Pillar 1 — Real-time Trust & Transparency trace feed."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.services.trust_trace import get_latest_trace

router = APIRouter(tags=["trust"])


@router.get("/artists/{artist_id}/trust/trace")
def get_trust_trace(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Return the real-time pipeline trace feed for this artist.

    Each entry contains stage, sub_stage, confidence (0-1), eta_seconds,
    and a plain-English explanation of what XR7 is doing right now.
    """
    events = get_latest_trace(db, artist_id)
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "trace": events,
        "latest_stage": events[-1]["stage"] if events else None,
    })
