"""Pillar 2 — Referral program service (track, credit, query)."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.artist_referral import ArtistReferral
from xr7_common.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_REFERRAL_FEE_PCT = 5.0  # 5 % of referred artist net recoveries


def create_referral(
    db: Session,
    *,
    referrer_artist_id: str,
    referred_artist_id: str,
    referral_fee_pct: float = _DEFAULT_REFERRAL_FEE_PCT,
) -> ArtistReferral:
    """Register a new referral link and prevent duplicates."""
    # Validate both artists exist
    for aid in (referrer_artist_id, referred_artist_id):
        if not db.query(Artist).filter(Artist.id == aid).first():
            raise ValueError(f"Artist {aid} not found")
    if referrer_artist_id == referred_artist_id:
        raise ValueError("Artist cannot refer themselves")

    existing = (
        db.query(ArtistReferral)
        .filter(
            ArtistReferral.referrer_artist_id == referrer_artist_id,
            ArtistReferral.referred_artist_id == referred_artist_id,
        )
        .first()
    )
    if existing:
        return existing

    ref = ArtistReferral(
        referrer_artist_id=referrer_artist_id,
        referred_artist_id=referred_artist_id,
        referral_fee_pct=referral_fee_pct,
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    logger.info(
        "referral_created",
        extra={"referrer": referrer_artist_id, "referred": referred_artist_id},
    )
    return ref


def credit_referral_on_recovery(
    db: Session,
    *,
    referred_artist_id: str,
    recovery_amount: float,
) -> float:
    """Credit referrer when referred artist receives a payout. Returns amount credited."""
    ref = (
        db.query(ArtistReferral)
        .filter(ArtistReferral.referred_artist_id == referred_artist_id)
        .first()
    )
    if not ref:
        return 0.0
    credit = round(recovery_amount * (ref.referral_fee_pct / 100.0), 6)
    ref.lifetime_earned = (ref.lifetime_earned or 0.0) + credit
    db.commit()
    return credit


def get_referral_tree(db: Session, artist_id: str) -> dict[str, Any]:
    """Return referral tree summary for dashboard."""
    outbound = (
        db.query(ArtistReferral)
        .filter(ArtistReferral.referrer_artist_id == artist_id)
        .all()
    )
    inbound = (
        db.query(ArtistReferral)
        .filter(ArtistReferral.referred_artist_id == artist_id)
        .first()
    )
    return {
        "artist_id": artist_id,
        "referred_by": inbound.referrer_artist_id if inbound else None,
        "referrals_made": len(outbound),
        "total_lifetime_earned": sum(r.lifetime_earned for r in outbound),
        "referral_fee_pct": _DEFAULT_REFERRAL_FEE_PCT,
        "referrals": [
            {
                "referred_artist_id": r.referred_artist_id,
                "fee_pct": r.referral_fee_pct,
                "lifetime_earned": r.lifetime_earned,
            }
            for r in outbound
        ],
    }
