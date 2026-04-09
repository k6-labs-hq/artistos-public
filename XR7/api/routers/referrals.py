"""Pillar 2 — Referral program endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.services.referral_service import create_referral, get_referral_tree

router = APIRouter(tags=["referrals"])


class ReferralRequest(BaseModel):
    referred_artist_id: str


@router.post("/artists/{artist_id}/referrals")
def register_referral(
    artist_id: str,
    payload: ReferralRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Register a new artist referral link.

    The referrer earns a percentage of the referred artist's net recoveries.
    """
    try:
        ref = create_referral(
            db,
            referrer_artist_id=artist_id,
            referred_artist_id=payload.referred_artist_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "referral_id": ref.id,
            "referred_artist_id": ref.referred_artist_id,
            "referral_fee_pct": ref.referral_fee_pct,
            "message": "Referral registered. You will earn a share of their net recoveries.",
        },
    )


@router.get("/artists/{artist_id}/referrals")
def get_referrals(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Return the referral tree and lifetime earnings for this artist."""
    tree = get_referral_tree(db, artist_id)
    return inject_branding_metadata(db, tree)
