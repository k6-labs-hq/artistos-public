"""Invite-Only Premier Experience: VIP / Founders Circle API endpoints.

Endpoints:
  POST /invite/vip/claim                    – claim a VIP invite code
  GET  /artists/{artist_id}/vip/status      – check VIP status + persona
  POST /admin/artists/{artist_id}/vip/grant – admin toggle VIP
  DELETE /admin/artists/{artist_id}/vip     – admin revoke VIP
  POST /admin/vip/invite-codes              – generate new invite codes (bulk)
  GET  /artists/{artist_id}/vip/drops       – list current VIP Drop items
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.vip import (
    AdminGrantVipRequest,
    ClaimVipInviteRequest,
    ClaimVipInviteResponse,
    FoundersCircleMemberSchema,
    VipDropItem,
    VipInviteCodeSchema,
    VipStatusResponse,
    VipTierLevel,
)
from XR7.services.vip_service import VipService

router = APIRouter(tags=["vip"])

INVITE_BASE_URL = os.environ.get("INVITE_BASE_URL", "https://app.xr7.io/onboard")


# ---------------------------------------------------------------------------
# Claim an invite code → become a VIP
# ---------------------------------------------------------------------------

@router.post("/invite/vip/claim", response_model=ClaimVipInviteResponse, summary="Claim a VIP invite code")
def claim_vip_invite(body: ClaimVipInviteRequest, db: Session = Depends(get_db)) -> ClaimVipInviteResponse:
    """Activate Founders Circle / VIP membership using a single-use invite code."""
    svc = VipService(db)
    try:
        membership = svc.claim_invite(body.artist_id, body.invite_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ClaimVipInviteResponse(
        success=True,
        membership=FoundersCircleMemberSchema.model_validate(membership),
        message="Welcome to the Founders Circle. Your concierge-grade experience is now active.",
    )


# ---------------------------------------------------------------------------
# VIP status check
# ---------------------------------------------------------------------------

@router.get(
    "/artists/{artist_id}/vip/status",
    response_model=VipStatusResponse,
    summary="Get artist VIP/Founders Circle status",
)
def get_vip_status(artist_id: str, db: Session = Depends(get_db)) -> VipStatusResponse:
    svc = VipService(db)
    membership = svc.get_membership(artist_id)
    svc.get_persona(artist_id)
    return VipStatusResponse(
        artist_id=artist_id,
        is_vip=membership is not None,
        tier_level=VipTierLevel(membership.tier_level) if membership else None,
        membership=FoundersCircleMemberSchema.model_validate(membership) if membership else None,
        persona=None  # populated by separate /persona/enrich endpoint
    )


# ---------------------------------------------------------------------------
# VIP Drop catalogue
# ---------------------------------------------------------------------------

@router.get(
    "/artists/{artist_id}/vip/drops",
    response_model=list[VipDropItem],
    summary="List current VIP Drop features available to this member",
)
def get_vip_drops(artist_id: str, db: Session = Depends(get_db)) -> list[VipDropItem]:
    svc = VipService(db)
    if not svc.is_vip(artist_id):
        raise HTTPException(status_code=403, detail="VIP membership required.")
    return [VipDropItem(**item) for item in svc.get_vip_drops()]


# ---------------------------------------------------------------------------
# Admin: grant / revoke VIP
# ---------------------------------------------------------------------------

class AdminVipGrantResponse(BaseModel):
    success: bool
    membership: FoundersCircleMemberSchema


@router.post(
    "/admin/artists/{artist_id}/vip/grant",
    response_model=AdminVipGrantResponse,
    summary="Admin: directly grant VIP membership to an artist",
)
def admin_grant_vip(
    artist_id: str,
    body: AdminGrantVipRequest,
    db: Session = Depends(get_db),
) -> AdminVipGrantResponse:
    svc = VipService(db)
    try:
        membership = svc.admin_grant_vip(
            artist_id,
            tier_level=body.tier_level,
            concierge_analyst_name=body.concierge_analyst_name,
            concierge_analyst_email=body.concierge_analyst_email,
            calendly_link=body.calendly_link,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AdminVipGrantResponse(
        success=True,
        membership=FoundersCircleMemberSchema.model_validate(membership),
    )


class AdminRevokeResponse(BaseModel):
    success: bool
    message: str


@router.delete(
    "/admin/artists/{artist_id}/vip",
    response_model=AdminRevokeResponse,
    summary="Admin: revoke VIP membership",
)
def admin_revoke_vip(artist_id: str, db: Session = Depends(get_db)) -> AdminRevokeResponse:
    svc = VipService(db)
    revoked = svc.revoke_vip(artist_id)
    if not revoked:
        raise HTTPException(status_code=404, detail="No active VIP membership found.")
    return AdminRevokeResponse(success=True, message="VIP membership revoked.")


# ---------------------------------------------------------------------------
# Admin: generate invite codes
# ---------------------------------------------------------------------------

class GenerateInviteCodesRequest(BaseModel):
    count: int = 1
    tier_level: VipTierLevel = VipTierLevel.FOUNDERS_CIRCLE
    expires_in_days: int = 30
    perk_bonus: Optional[str] = None
    admin_id: Optional[str] = None


class GenerateInviteCodesResponse(BaseModel):
    codes: list[VipInviteCodeSchema]
    invite_links: list[str]


@router.post(
    "/admin/vip/invite-codes",
    response_model=GenerateInviteCodesResponse,
    summary="Admin: generate VIP invite codes",
)
def generate_vip_invite_codes(
    body: GenerateInviteCodesRequest,
    db: Session = Depends(get_db),
) -> GenerateInviteCodesResponse:
    if body.count < 1 or body.count > 100:
        raise HTTPException(status_code=400, detail="count must be between 1 and 100.")
    svc = VipService(db)
    codes = []
    links = []
    for _ in range(body.count):
        code_entry = svc.create_invite_code(
            tier_level=body.tier_level,
            created_by_admin_id=body.admin_id,
            expires_in_days=body.expires_in_days,
            perk_bonus=body.perk_bonus,
        )
        codes.append(VipInviteCodeSchema.model_validate(code_entry))
        links.append(f"{INVITE_BASE_URL}?vip_code={code_entry.code}")
    return GenerateInviteCodesResponse(codes=codes, invite_links=links)
