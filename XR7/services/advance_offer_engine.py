"""Pillar 5 — Cash advance offer engine backed by recoverable forecast."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.liquidity_advance import AdvanceStatus, RecoverableLiquidityAdvance
from xr7_common.logging import get_logger

logger = get_logger(__name__)

_ADVANCE_OFFER_EXPIRY_DAYS = 7
_MAX_ADVANCE_PCT_OF_FORECAST = 0.60   # Never advance more than 60 % of predicted low


def compute_advance_offer(
    db: Session,
    artist_id: str,
    *,
    predicted_low_forecast: float,
    currency: str = "USD",
    advance_fee_pct: float = 3.0,
) -> dict[str, Any]:
    """Compute a safe advance offer and persist it.

    The offer is capped at 60 % of the predicted-low recovery forecast to
    ensure repayment probability remains > 95 %.
    """
    if predicted_low_forecast <= 0:
        return {
            "artist_id": artist_id,
            "eligible": False,
            "reason": "No positive predicted recovery forecast available.",
        }

    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        return {"artist_id": artist_id, "eligible": False, "reason": "Artist not found."}

    offered_amount = round(predicted_low_forecast * _MAX_ADVANCE_PCT_OF_FORECAST, 2)
    expires_at = datetime.now(timezone.utc) + timedelta(days=_ADVANCE_OFFER_EXPIRY_DAYS)

    advance = RecoverableLiquidityAdvance(
        artist_id=artist_id,
        offered_amount=offered_amount,
        currency=currency,
        predicted_low_forecast=predicted_low_forecast,
        advance_fee_pct=advance_fee_pct,
        status=AdvanceStatus.OFFERED,
        notes=f"Auto-computed at {_MAX_ADVANCE_PCT_OF_FORECAST*100:.0f}% of predicted low forecast.",
        expires_at=expires_at,
    )
    db.add(advance)
    db.commit()
    db.refresh(advance)

    logger.info(
        "advance_offer_created",
        extra={"artist_id": artist_id, "offered_amount": offered_amount},
    )
    return {
        "artist_id": artist_id,
        "eligible": True,
        "advance_id": advance.id,
        "offered_amount": offered_amount,
        "currency": currency,
        "advance_fee_pct": advance_fee_pct,
        "net_to_artist": round(offered_amount * (1 - advance_fee_pct / 100), 2),
        "predicted_low_forecast": predicted_low_forecast,
        "expires_at": expires_at.isoformat(),
        "status": advance.status,
    }


def accept_advance(db: Session, *, advance_id: str, artist_id: str) -> dict[str, Any]:
    """Mark an advance as accepted, ready for Trolley disbursement."""
    advance = (
        db.query(RecoverableLiquidityAdvance)
        .filter(
            RecoverableLiquidityAdvance.id == advance_id,
            RecoverableLiquidityAdvance.artist_id == artist_id,
        )
        .first()
    )
    if not advance:
        return {"error": "Advance offer not found."}
    if advance.status != AdvanceStatus.OFFERED:
        return {"error": f"Advance is in {advance.status} state, cannot accept."}
    advance.status = AdvanceStatus.ACCEPTED
    advance.accepted_at = datetime.now(timezone.utc)
    db.commit()
    return {"advance_id": advance_id, "status": advance.status, "message": "Advance accepted. Disbursement queued."}
