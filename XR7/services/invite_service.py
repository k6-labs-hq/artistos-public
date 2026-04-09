"""High-level invite system management service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

import jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.invite import (
    Invite,
    InviteChannel,
    InviteEvent,
    InviteRole,
    InviteStatus,
)
from XR7.services.invite_token_service import invite_token_generator


class InviteService:
    """Manage the complete invite lifecycle."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def create_invite(
        self,
        recipient_name: str,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        channel: InviteChannel = InviteChannel.MANUAL,
        role: InviteRole = InviteRole.ARTIST,
        is_vip: bool = False,
        custom_message: Optional[str] = None,
        referring_agent_id: Optional[str] = None,
        referring_manager_id: Optional[str] = None,
        campaign: Optional[str] = None,
    ) -> tuple[Invite, str]:
        """Create a new invite and generate its token.

        Args:
            recipient_name: Invitee name (no sex assumptions)
            recipient_email: Email address
            recipient_phone: Phone number
            channel: How invite will be sent
            role: Role to assign upon redemption
            is_vip: Whether to grant VIP status
            custom_message: Custom message to include
            referring_agent_id: ID of referring agent
            referring_manager_id: ID of referring manager
            campaign: Campaign identifier

        Returns:
            Tuple of (Invite record, invite_token)
        """
        invite_id = str(uuid4())

        # Generate JWT token (72-hour expiration)
        invite_token = invite_token_generator.generate(
            invite_id=invite_id,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            is_vip=is_vip,
            referring_agent_id=referring_agent_id,
            campaign=campaign,
            expiration_hours=72,
        )

        # Compute token expiration
        token_expiration = datetime.now(timezone.utc) + timedelta(hours=72)

        # Create database record
        invite = Invite(
            id=invite_id,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            status=InviteStatus.PENDING,
            channel=channel,
            role=role,
            invite_token=invite_token,
            token_expiration=token_expiration,
            is_vip=is_vip,
            custom_message=custom_message,
            referring_agent_id=referring_agent_id,
            referring_manager_id=referring_manager_id,
            campaign=campaign,
        )
        self.db.add(invite)
        self.db.flush()

        # Record "created" event
        self._record_event(
            invite_id=invite_id,
            event_type="created",
            event_data={"channel": channel.value, "role": role.value},
        )

        self.db.commit()
        return invite, invite_token

    def send_invite(
        self,
        invite_id: str,
        ip_address: Optional[str] = None,
    ) -> Invite:
        """Mark an invite as sent.

        Args:
            invite_id: ID of invite to send
            ip_address: Sender's IP address (for audit)

        Returns:
            Updated Invite record

        Raises:
            ValueError: If invite not found or already sent
        """
        invite = self.db.query(Invite).filter(Invite.id == invite_id).first()
        if not invite:
            raise ValueError(f"Invite {invite_id} not found")
        if invite.status != InviteStatus.PENDING:
            raise ValueError(f"Invite {invite_id} is already {invite.status}")

        invite.status = InviteStatus.SENT
        invite.sent_at = datetime.now(timezone.utc)
        self.db.commit()

        self._record_event(
            invite_id=invite_id,
            event_type="sent",
            ip_address=ip_address,
        )

        return invite

    def validate_invite(self, invite_token: str) -> dict:
        """Validate an invite token and return metadata.

        Args:
            invite_token: JWT token from invite link

        Returns:
            Dict with {
                "is_valid": bool,
                "invite_id": str or None,
                "recipient_name": str or None,
                "is_vip": bool,
                "error": str or None,
            }
        """
        # First, check JWT signature
        try:
            payload = invite_token_generator.validate(invite_token)
        except jwt.InvalidTokenError as exc:
            return {
                "is_valid": False,
                "invite_id": None,
                "recipient_name": None,
                "error": str(exc),
            }

        invite_id = payload.get("invite_id")
        recipient_name = payload.get("recipient_name")
        is_vip = payload.get("is_vip", False)

        # Then, check database status
        invite = self.db.query(Invite).filter(Invite.id == invite_id).first()
        if not invite:
            return {
                "is_valid": False,
                "invite_id": invite_id,
                "recipient_name": recipient_name,
                "error": "Invite not found in system",
            }

        if not invite.is_valid():
            error = "Invite is no longer active"
            if invite.is_single_use_consumed:
                error = "Invite has already been redeemed"
            elif invite.is_expired():
                error = "Invite has expired"
            return {
                "is_valid": False,
                "invite_id": invite_id,
                "recipient_name": recipient_name,
                "error": error,
            }

        return {
            "is_valid": True,
            "invite_id": invite_id,
            "recipient_name": recipient_name,
            "is_vip": is_vip,
            "error": None,
        }

    def open_invite(
        self,
        invite_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Invite:
        """Record that an invite link was opened (click through).

        Args:
            invite_token: JWT token from invite link
            ip_address: Visitor's IP address
            user_agent: Browser user-agent string

        Returns:
            Updated Invite record

        Raises:
            ValueError: If token invalid or invite not openable
        """
        validation = self.validate_invite(invite_token)
        if not validation["is_valid"]:
            raise ValueError(validation.get("error", "Invalid invite"))

        invite_id = validation["invite_id"]
        invite = self.db.query(Invite).filter(Invite.id == invite_id).first()

        if invite.status == InviteStatus.PENDING:
            pass  # OK to mark as opened
        elif invite.status in {InviteStatus.SENT, InviteStatus.OPENED}:
            pass  # OK to mark as opened
        else:
            raise ValueError(f"Cannot open invite with status {invite.status}")

        invite.status = InviteStatus.OPENED
        invite.opened_at = datetime.now(timezone.utc)
        self.db.commit()

        self._record_event(
            invite_id=invite_id,
            event_type="opened",
            ip_address=ip_address,
            event_data={"user_agent": user_agent or ""},
        )

        return invite

    def redeem_invite(
        self,
        invite_token: str,
        artist_id: str,
        ip_address: Optional[str] = None,
    ) -> Invite:
        """Redeem an invite, creating artist account.

        Args:
            invite_token: JWT token from invite link
            artist_id: ID of newly created artist account
            ip_address: Visitor's IP address

        Returns:
            Updated Invite record

        Raises:
            ValueError: If token invalid, expired, or already used
        """
        validation = self.validate_invite(invite_token)
        if not validation["is_valid"]:
            raise ValueError(validation.get("error", "Invalid invite"))

        invite_id = validation["invite_id"]
        invite = self.db.query(Invite).filter(Invite.id == invite_id).first()

        if invite.is_single_use_consumed:
            raise ValueError("Invite has already been redeemed")

        invite.status = InviteStatus.REDEEMED
        invite.redeemed_at = datetime.now(timezone.utc)
        invite.redeemed_by_artist_id = artist_id
        invite.is_single_use_consumed = True
        invite.redemption_ip_address = ip_address
        self.db.commit()

        self._record_event(
            invite_id=invite_id,
            event_type="redeemed",
            ip_address=ip_address,
            event_data={"artist_id": artist_id},
        )

        return invite

    def revoke_invite(self, invite_id: str, reason: Optional[str] = None) -> Invite:
        """Revoke an invite (cannot be redeemed).

        Args:
            invite_id: ID of invite to revoke
            reason: Reason for revocation

        Returns:
            Updated Invite record
        """
        invite = self.db.query(Invite).filter(Invite.id == invite_id).first()
        if not invite:
            raise ValueError(f"Invite {invite_id} not found")

        invite.status = InviteStatus.REVOKED
        self.db.commit()

        self._record_event(
            invite_id=invite_id,
            event_type="revoked",
            event_data={"reason": reason or ""},
        )

        return invite

    def get_invite(self, invite_id: str) -> Optional[Invite]:
        """Retrieve an invite by ID."""
        return self.db.query(Invite).filter(Invite.id == invite_id).first()

    def get_invite_by_token(self, invite_token: str) -> Optional[Invite]:
        """Retrieve an invite by token."""
        return self.db.query(Invite).filter(Invite.invite_token == invite_token).first()

    def list_invites(
        self,
        status: Optional[InviteStatus] = None,
        campaign: Optional[str] = None,
        is_vip: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Invite], int]:
        """List invites with optional filtering.

        Returns:
            Tuple of (list of invites, total count)
        """
        query = self.db.query(Invite)

        if status:
            query = query.filter(Invite.status == status)
        if campaign:
            query = query.filter(Invite.campaign == campaign)
        if is_vip is not None:
            query = query.filter(Invite.is_vip == is_vip)

        total = query.count()
        invites = query.order_by(Invite.created_at.desc()).offset(offset).limit(limit).all()
        return invites, total

    def get_analytics(
        self,
        campaign: Optional[str] = None,
        days: int = 30,
    ) -> dict:
        """Compute invite analytics.

        Args:
            campaign: Filter by campaign
            days: Number of days to look back

        Returns:
            Dict with analytics metrics
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        query = self.db.query(Invite).filter(Invite.created_at >= cutoff)
        if campaign:
            query = query.filter(Invite.campaign == campaign)

        total_created = query.count()
        total_sent = query.filter(Invite.sent_at.isnot(None)).count()
        total_opened = query.filter(Invite.opened_at.isnot(None)).count()
        total_redeemed = query.filter(Invite.redeemed_at.isnot(None)).count()
        total_expired = query.filter(Invite.status == InviteStatus.EXPIRED).count()

        # Compute rates
        open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
        redemption_rate = (total_redeemed / total_opened * 100) if total_opened > 0 else 0

        # Role distribution
        role_dist = {}
        role_counts = self.db.query(Invite.role, func.count(Invite.id)).filter(
            Invite.created_at >= cutoff
        )
        if campaign:
            role_counts = role_counts.filter(Invite.campaign == campaign)
        for role, count in role_counts.group_by(Invite.role).all():
            role_dist[role.value] = count

        return {
            "period_days": days,
            "campaign": campaign,
            "invites_created": total_created,
            "invites_sent": total_sent,
            "invites_opened": total_opened,
            "invites_redeemed": total_redeemed,
            "invites_expired": total_expired,
            "open_rate_percent": round(open_rate, 2),
            "redemption_rate_percent": round(redemption_rate, 2),
            "role_distribution": role_dist,
        }

    def _record_event(
        self,
        invite_id: str,
        event_type: str,
        ip_address: Optional[str] = None,
        event_data: Optional[dict] = None,
        user_agent: Optional[str] = None,
    ) -> InviteEvent:
        """Internal: record an invite lifecycle event.

        Args:
            invite_id: ID of invite
            event_type: Type of event
            ip_address: IP address
            event_data: Additional data
            user_agent: Browser user-agent

        Returns:
            Created InviteEvent record
        """
        event = InviteEvent(
            id=str(uuid4()),
            invite_id=invite_id,
            event_type=event_type,
            event_data=event_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(event)
        self.db.flush()
        return event


def get_invite_service(db: Session) -> InviteService:
    """Dependency injection for invite service."""
    return InviteService(db)
