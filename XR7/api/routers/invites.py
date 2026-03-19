"""Private invite-only access system API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models import (
    Invite,
    InviteChannel,
    InviteGenerateRequest,
    InviteRole,
    InviteSchema,
    InviteStatus,
    InviteValidateRequest,
    InviteValidationResponse,
    InviteWithTokenSchema,
    get_db,
)
from XR7.services.branding import inject_branding_metadata
from XR7.services.invite_service import get_invite_service

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("/generate", response_model=InviteWithTokenSchema)
def generate_invite(
    request: Request,
    req: InviteGenerateRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Generate and send a personalized invite.

    This endpoint creates a new invite token and prepares it for sending
    via email, Instagram DM, SMS, or manual distribution.

    The invite link will direct the recipient to a premium onboarding
    portal pre-populated with their name.
    """
    service = get_invite_service(db)

    # Create the invite
    invite, token = service.create_invite(
        recipient_name=req.recipient_name,
        recipient_email=req.recipient_email,
        channel=req.channel,
        role=req.role,
        is_vip=req.is_vip,
        custom_message=req.custom_message,
        referring_agent_id=req.referring_agent_id,
        campaign=req.campaign,
    )

    # Mark as sent (caller responsible for actual email/DM delivery)
    invite = service.send_invite(
        invite.id,
        ip_address=request.client.host if request.client else None,
    )

    # Return invite with token
    result = InviteWithTokenSchema.model_validate(invite)
    result.invite_token = token
    return inject_branding_metadata(db, result.model_dump())


@router.post("/validate", response_model=InviteValidationResponse)
def validate_invite(
    req: InviteValidateRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Validate an invite token and check eligibility.

    This is called by the frontend when the user clicks the invite link.
    It verifies the JWT signature, expiration, and database status.

    Returns:
    - is_valid: boolean
    - invite_id: the invite ID (if found)
    - recipient_name: the invitee's name for personalization
    - error: error message (if not valid)
    """
    service = get_invite_service(db)
    validation = service.validate_invite(req.invite_token)
    return inject_branding_metadata(db, validation)


@router.post("/open")
def open_invite(
    request: Request,
    req: InviteValidateRequest,
    db: Session = Depends(get_db),
) -> InviteSchema:
    """Record that an invite link was opened (click-through tracking).

    Called when the user clicks the invite link and the welcome screen
    is displayed.
    """
    service = get_invite_service(db)

    try:
        invite = service.open_invite(
            req.invite_token,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = InviteSchema.model_validate(invite)
    return inject_branding_metadata(db, result.model_dump())


@router.post("/redeem")
def redeem_invite(
    request: Request,
    invite_token: str,
    artist_id: str,
    db: Session = Depends(get_db),
) -> InviteSchema:
    """Redeem an invite and link it to a newly created artist account.

    Called after the user completes onboarding and an artist record
    is created. The invite is marked as redeemed (single-use) and linked
    to the artist.
    """
    service = get_invite_service(db)

    try:
        invite = service.redeem_invite(
            invite_token,
            artist_id=artist_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = InviteSchema.model_validate(invite)
    return inject_branding_metadata(db, result.model_dump())


@router.get("/{invite_id}", response_model=InviteSchema)
def get_invite(
    invite_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Get invite details by ID.

    Accessible after validation or by admins.
    """
    service = get_invite_service(db)
    invite = service.get_invite(invite_id)

    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    result = InviteSchema.model_validate(invite)
    return inject_branding_metadata(db, result.model_dump())


@router.get("/", response_model=dict)
def list_invites(
    status: Optional[InviteStatus] = Query(None),
    campaign: Optional[str] = Query(None),
    is_vip: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    """List invites (admin/dashboard endpoint).

    Optionally filter by status, campaign, or VIP flag.
    """
    service = get_invite_service(db)
    invites, total = service.list_invites(
        status=status,
        campaign=campaign,
        is_vip=is_vip,
        limit=limit,
        offset=offset,
    )

    result = {
        "invites": [InviteSchema.model_validate(inv).model_dump() for inv in invites],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
    return inject_branding_metadata(db, result)


@router.post("/{invite_id}/revoke")
def revoke_invite(
    invite_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
) -> InviteSchema:
    """Revoke an invite (admin endpoint).

    Once revoked, the invite cannot be redeemed.
    """
    service = get_invite_service(db)

    try:
        invite = service.revoke_invite(invite_id, reason=reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    result = InviteSchema.model_validate(invite)
    return inject_branding_metadata(db, result.model_dump())


@router.get("/analytics/summary")
def get_analytics(
    campaign: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict:
    """Get invite analytics for dashboard.

    Returns:
    - invites_created
    - invites_sent
    - invites_opened
    - invites_redeemed
    - open_rate_percent
    - redemption_rate_percent
    - role_distribution
    """
    service = get_invite_service(db)
    analytics = service.get_analytics(campaign=campaign, days=days)
    return inject_branding_metadata(db, analytics)


# ======================================
# Email & Webhook Automation Endpoints
# ======================================


@router.post("/email-trigger")
def email_triggered_invite(
    sender_email: str,
    sender_name: str,
    message_body: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Auto-generate invite when artist emails inquiry.

    Webhook: called by email parsing service when someone
    emails XR7 with keywords like "analysis", "royalties", "help".

    Automatically:
    1. Creates an invite
    2. Sends personalized reply with invite link
    3. Tracks campaign as "email_inquiry"
    """
    service = get_invite_service(db)

    # Create invite
    invite, token = service.create_invite(
        recipient_name=sender_name or "Creator",
        recipient_email=sender_email,
        channel=InviteChannel.EMAIL,
        role=InviteRole.ARTIST,
        campaign="email_inquiry",
        custom_message=message_body,
    )

    # Mark as sent
    service.send_invite(invite.id)

    return inject_branding_metadata(
        db,
        {
            "success": True,
            "invite_id": invite.id,
            "sender_email": sender_email,
            "invite_link": f"/onboarding/invite/{token}",
        },
    )


@router.post("/instagram-webhook")
async def instagram_dm_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Handle Instagram DM webhooks for auto-responders.

    When someone DMs @yourartistpage with keywords
    ("analysis", "royalties", "help", "XR7", "TV/Film", "music"),
    automatically:
    1. Parse sender name from IG profile
    2. Create invite
    3. Send auto-reply with personalized link
    4. Track as "instagram_dm" channel

    Integration: Connect to Instagram Business Graph API webhook.
    """
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    # Parse DM data (Instagram Business Graph format)
    # Expected: {"from": {"name": "..."}, "text": "..."}
    sender_name = body.get("from", {}).get("name", "Creator")
    sender_id = body.get("from", {}).get("id")
    message_text = body.get("text", "").lower()

    # Check for keywords
    keywords = {"analysis", "royalties", "help", "xr7", "tv/film", "music"}
    if not any(kw in message_text for kw in keywords):
        # Not an inquiry, ignore
        return {"handled": False, "reason": "No keywords matched"}

    service = get_invite_service(db)

    # Create invite
    invite, token = service.create_invite(
        recipient_name=sender_name,
        channel=InviteChannel.INSTAGRAM_DM,
        role=InviteRole.ARTIST,
        campaign="instagram_inquiry",
        metadata={"instagram_user_id": sender_id, "message": message_text},
    )

    # Mark as sent
    service.send_invite(invite.id)

    return inject_branding_metadata(
        db,
        {
            "success": True,
            "invite_id": invite.id,
            "instagram_user_id": sender_id,
            "invite_link": f"/onboarding/invite/{token}",
            "auto_reply": f"Your private XR7 analysis session is ready: /onboarding/invite/{token}",
        },
    )


# ======================================
# Dashboard Management Endpoints
# ======================================


@router.post("/dashboard/quick-generate")
def dashboard_quick_generate(
    recipient_name: str,
    recipient_email: Optional[str] = None,
    role: InviteRole = InviteRole.ARTIST,
    campaign: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Quick invite generation for internal dashboard (Matt's admin panel).

    One-click invite creation with instant link copy.
    """
    service = get_invite_service(db)

    invite, token = service.create_invite(
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        channel=InviteChannel.MANUAL,
        role=role,
        campaign=campaign or "manual_generation",
    )

    service.send_invite(invite.id)

    # Generate the invite link
    invite_link = f"https://xr7.app/onboarding/invite/{token}"

    return inject_branding_metadata(
        db,
        {
            "success": True,
            "invite_id": invite.id,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "invite_link": invite_link,
            "expires_at": invite.token_expiration.isoformat(),
            "copy_ready": True,
        },
    )
