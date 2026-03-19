"""VIP Referral Programme + Early Access endpoints.

Endpoints:
  POST /artists/{artist_id}/vip/referral      – create a referral invite
  GET  /artists/{artist_id}/vip/referrals     – list artist's referrals
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.vip import (
    CreateVipReferralRequest,
    CreateVipReferralResponse,
    VipReferralSchema,
)
from XR7.services.vip_service import VipService

import os

router = APIRouter(tags=["vip"])

INVITE_BASE_URL = os.environ.get("INVITE_BASE_URL", "https://app.xr7.io/onboard")


@router.post(
    "/artists/{artist_id}/vip/referral",
    response_model=CreateVipReferralResponse,
    summary="VIP member refers another elite creator",
)
def create_vip_referral(
    artist_id: str,
    body: CreateVipReferralRequest,
    db: Session = Depends(get_db),
) -> CreateVipReferralResponse:
    svc = VipService(db)
    try:
        referral, code_entry = svc.create_referral(artist_id, body.referred_email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    membership = svc.get_membership(artist_id)
    return CreateVipReferralResponse(
        referral_id=referral.id,
        invite_code=code_entry.code,
        invite_link=f"{INVITE_BASE_URL}?vip_code={code_entry.code}",
        slots_remaining=membership.referral_slots_remaining if membership else 0,
    )


@router.get(
    "/artists/{artist_id}/vip/referrals",
    response_model=list[VipReferralSchema],
    summary="List VIP referrals made by this artist",
)
def list_vip_referrals(
    artist_id: str,
    db: Session = Depends(get_db),
) -> list[VipReferralSchema]:
    svc = VipService(db)
    if not svc.is_vip(artist_id):
        raise HTTPException(status_code=403, detail="VIP membership required.")
    from XR7.models.vip import VipReferral
    rows = (
        db.query(VipReferral)
        .filter(VipReferral.referrer_artist_id == artist_id)
        .order_by(VipReferral.created_at.desc())
        .all()
    )
    return [VipReferralSchema.model_validate(r) for r in rows]
