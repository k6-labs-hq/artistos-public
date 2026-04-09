"""Pillar 5 — Rights scan, registration packets, cash advance offer."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_artist_access
from XR7.models.base import get_db
from XR7.models.liquidity_advance import RecoverableLiquidityAdvance
from XR7.models.rights_scan import RightsScanResult
from XR7.services.advance_offer_engine import accept_advance, compute_advance_offer
from XR7.services.branding import inject_branding_metadata
from XR7.services.rights_scanner import persist_and_generate_packets, scan_rights_gaps

router = APIRouter(tags=["sovereignty"])


# ---------------------------------------------------------------------------
# Rights Scan
# ---------------------------------------------------------------------------


@router.get("/artists/{artist_id}/rights/scan")
def scan_rights(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Scan catalog for missing ISRC/ISWC/UPC/PRO/foreign registrations."""
    get_artist_or_404(artist_id, db)

    gaps = scan_rights_gaps(db, artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "gaps_found": len(gaps),
            "gaps": gaps,
        },
    )


@router.post("/artists/{artist_id}/rights/register")
def register_rights_packets(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Generate and persist auto-registration packets for all detected gaps."""
    get_artist_or_404(artist_id, db)

    gaps = scan_rights_gaps(db, artist_id)
    results = persist_and_generate_packets(db, artist_id, gaps)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "packets_generated": len(results),
            "packets": [
                {
                    "id": r.id,
                    "gap_type": r.gap_type,
                    "territory": r.territory,
                    "submission_status": r.submission_status,
                    "work_id": r.work_id,
                }
                for r in results
            ],
        },
    )


@router.get("/artists/{artist_id}/rights/gaps")
def list_rights_gaps(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """List all persisted rights scan results for this artist."""
    rows = (
        db.query(RightsScanResult)
        .filter(RightsScanResult.artist_id == artist_id)
        .order_by(RightsScanResult.scanned_at.desc())
        .all()
    )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "count": len(rows),
            "gaps": [
                {
                    "id": r.id,
                    "gap_type": r.gap_type,
                    "territory": r.territory,
                    "work_id": r.work_id,
                    "submission_status": r.submission_status,
                    "notes": r.notes,
                    "scanned_at": r.scanned_at.isoformat() if r.scanned_at else None,
                }
                for r in rows
            ],
        },
    )


# ---------------------------------------------------------------------------
# Cash Advance Offer
# ---------------------------------------------------------------------------


class AdvanceOfferRequest(BaseModel):
    predicted_low_forecast: float = Field(gt=0)
    currency: str = "USD"
    advance_fee_pct: float = Field(default=3.0, ge=0, le=20)


class AdvanceAcceptRequest(BaseModel):
    advance_id: str


@router.post("/artists/{artist_id}/advance/offer")
def create_advance_offer(
    artist_id: str,
    payload: AdvanceOfferRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Compute and return a cash advance offer backed by predicted recovery.

    Safe advance = 60% of the predicted-low earnings forecast; repaid
    automatically when the recovery arrives.
    """
    result = compute_advance_offer(
        db,
        artist_id,
        predicted_low_forecast=payload.predicted_low_forecast,
        currency=payload.currency,
        advance_fee_pct=payload.advance_fee_pct,
    )
    return inject_branding_metadata(db, result)


@router.post("/artists/{artist_id}/advance/accept")
def accept_advance_offer(
    artist_id: str,
    payload: AdvanceAcceptRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Accept a pending advance offer. Triggers Trolley disbursement queue."""
    result = accept_advance(db, advance_id=payload.advance_id, artist_id=artist_id)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/advance/history")
def list_advance_history(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    advances = (
        db.query(RecoverableLiquidityAdvance)
        .filter(RecoverableLiquidityAdvance.artist_id == artist_id)
        .order_by(RecoverableLiquidityAdvance.offered_at.desc())
        .all()
    )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "count": len(advances),
            "advances": [
                {
                    "id": a.id,
                    "offered_amount": a.offered_amount,
                    "currency": a.currency,
                    "advance_fee_pct": a.advance_fee_pct,
                    "status": a.status,
                    "offered_at": a.offered_at.isoformat() if a.offered_at else None,
                    "accepted_at": a.accepted_at.isoformat() if a.accepted_at else None,
                    "disbursed_at": a.disbursed_at.isoformat() if a.disbursed_at else None,
                }
                for a in advances
            ],
        },
    )
