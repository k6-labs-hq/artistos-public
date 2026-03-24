"""
Black Box Countdown — API endpoints.

GET  /artists/{artist_id}/anomalies/countdown
GET  /artists/{artist_id}/anomalies/{anomaly_id}/countdown
POST /admin/society-rules/freeze
"""
from __future__ import annotations

import os
import hmac
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.modules.black_box_countdown import BlackBoxCountdown, apply_freeze
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["black_box_countdown"])


def _require_admin(x_admin_key: str = Header(default="", alias="X-Admin-Key")) -> None:
    expected = os.environ.get("ADMIN_API_KEY") or os.environ.get("WIDGET_ADMIN_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API key not configured.")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")


@router.get("/artists/{artist_id}/anomalies/countdown")
def get_all_countdowns(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """All anomalies with countdown metadata, sorted by urgency."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = BlackBoxCountdown(db)
    result = engine.compute_all(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/anomalies/{anomaly_id}/countdown")
def get_single_countdown(
    artist_id: str,
    anomaly_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Single anomaly countdown detail."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = BlackBoxCountdown(db)
    result = engine.compute_single(artist_id, anomaly_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return inject_branding_metadata(db, result)


class FreezeRequest(BaseModel):
    society: str
    freeze_until: datetime
    reason: str | None = None


@router.post("/admin/society-rules/freeze")
def freeze_society_redistribution(
    body: FreezeRequest,
    _admin: None = Depends(_require_admin),
) -> dict[str, Any]:
    """Apply a redistribution freeze event to a society (admin only)."""
    freeze_until = body.freeze_until
    if freeze_until.tzinfo is None:
        freeze_until = freeze_until.replace(tzinfo=timezone.utc)
    apply_freeze(body.society, freeze_until)
    return {
        "society": body.society.upper(),
        "freeze_until": freeze_until.isoformat(),
        "reason": body.reason,
        "status": "freeze_applied",
    }
