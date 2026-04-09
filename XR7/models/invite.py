"""Private invite system for XR7 access control."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, DateTime, Enum as SQLEnum, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class InviteStatus(str, Enum):
    """Invite lifecycle status."""
    PENDING = "pending"         # Created, not yet sent
    SENT = "sent"               # Sent to recipient
    OPENED = "opened"           # Recipient opened the link
    REDEEMED = "redeemed"       # Recipient completed onboarding
    EXPIRED = "expired"         # Token expired
    REVOKED = "revoked"         # Manually revoked


class InviteChannel(str, Enum):
    """How the invite was sent."""
    EMAIL = "email"
    INSTAGRAM_DM = "instagram_dm"
    SMS = "sms"
    MANUAL = "manual"


class InviteRole(str, Enum):
    """Role the invitee will assume upon redemption."""
    ARTIST = "artist"
    WRITER = "writer"
    DIRECTOR = "director"
    ACTOR = "actor"
    STUDIO = "studio"
    DISTRIBUTOR = "distributor"
    MANAGER = "manager"
    AGENT = "agent"
    ANALYST = "analyst"


class Invite(Base):
    """Private invite for XR7 access."""

    __tablename__ = "invites"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Recipient info (no sex assumptions)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Invite metadata
    status: Mapped[InviteStatus] = mapped_column(
        SQLEnum(InviteStatus),
        nullable=False,
        default=InviteStatus.PENDING,
        index=True,
    )
    channel: Mapped[InviteChannel] = mapped_column(
        SQLEnum(InviteChannel),
        nullable=False,
        default=InviteChannel.MANUAL,
    )
    role: Mapped[InviteRole] = mapped_column(
        SQLEnum(InviteRole),
        nullable=False,
        default=InviteRole.ARTIST,
    )

    # Invite token (encrypted in production)
    invite_token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    token_expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Referral tracking
    referring_agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    referring_manager_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "vip_kickoff", "festival_2026"

    # Premium features
    is_vip: Mapped[bool] = mapped_column(default=False, index=True)
    custom_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Event timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    redeemed_by_artist_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    # Security: track redemption
    is_single_use_consumed: Mapped[bool] = mapped_column(default=False)
    redemption_ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv4 or IPv6

    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Custom tracking data

    __table_args__ = (
        Index("ix_invites_token_status", "invite_token", "status"),
        Index("ix_invites_recipient_status", "recipient_email", "status"),
        Index("ix_invites_created_status", "created_at", "status"),
    )

    def is_expired(self) -> bool:
        """Check if invite token has expired."""
        return datetime.now(timezone.utc).replace(tzinfo=None) > self.token_expiration

    def is_valid(self) -> bool:
        """Check if invite is valid for redemption."""
        return (
            self.status in {InviteStatus.SENT, InviteStatus.OPENED}
            and not self.is_expired()
            and not self.is_single_use_consumed
        )


class InviteEvent(Base):
    """Track invite lifecycle events for audit trail."""

    __tablename__ = "invite_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    invite_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "created", "sent", "opened", "redeemed", etc.
    event_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_invite_events_invite_id_created", "invite_id", "created_at"),
    )


class InviteAnalytics(Base):
    """Pre-computed analytics for invite campaigns."""

    __tablename__ = "invite_analytics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Counts
    invites_created: Mapped[int] = mapped_column(default=0)
    invites_sent: Mapped[int] = mapped_column(default=0)
    invites_opened: Mapped[int] = mapped_column(default=0)
    invites_redeemed: Mapped[int] = mapped_column(default=0)
    invites_expired: Mapped[int] = mapped_column(default=0)

    # Ratios (computed)
    open_rate: Mapped[Optional[float]] = mapped_column(nullable=True)  # opened / sent
    redemption_rate: Mapped[Optional[float]] = mapped_column(nullable=True)  # redeemed / opened

    # Role breakdown (JSON)
    role_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_invite_analytics_campaign_date", "campaign", "date"),
    )


# Pydantic Schemas for API
class InviteCreate(BaseModel):
    """Request to create an invite."""

    recipient_name: str = Field(..., min_length=1, max_length=255)
    recipient_email: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)
    channel: InviteChannel = InviteChannel.MANUAL
    role: InviteRole = InviteRole.ARTIST
    is_vip: bool = False
    custom_message: Optional[str] = None
    referring_agent_id: Optional[str] = None
    referring_manager_id: Optional[str] = None
    campaign: Optional[str] = None


class InviteGenerateRequest(BaseModel):
    """Request to generate/send an invite."""

    recipient_name: str = Field(..., min_length=1, max_length=255)
    recipient_email: Optional[str] = Field(None, max_length=255)
    channel: InviteChannel = InviteChannel.EMAIL
    role: InviteRole = InviteRole.ARTIST
    is_vip: bool = False
    custom_message: Optional[str] = None
    referring_agent_id: Optional[str] = None
    campaign: Optional[str] = None


class InviteValidateRequest(BaseModel):
    """Request to validate an invite token."""

    invite_token: str = Field(..., min_length=1)


class InviteRedeemRequest(BaseModel):
    """Request to redeem an invite."""

    invite_token: str = Field(..., min_length=1)
    artist_email: str = Field(..., min_length=1, max_length=255)


class InviteSchema(BaseModel):
    """Invite response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_name: str
    recipient_email: Optional[str]
    status: InviteStatus
    channel: InviteChannel
    role: InviteRole
    is_vip: bool
    created_at: datetime
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    redeemed_at: Optional[datetime]
    token_expiration: datetime
    campaign: Optional[str]
    referring_agent_id: Optional[str]


class InviteWithTokenSchema(InviteSchema):
    """Invite response with token (only after generation)."""

    invite_token: str


class InviteValidationResponse(BaseModel):
    """Response from invite validation."""

    is_valid: bool
    invite_id: Optional[str] = None
    recipient_name: Optional[str] = None
    error: Optional[str] = None


class InviteAnalyticsSchema(BaseModel):
    """Analytics response."""

    model_config = ConfigDict(from_attributes=True)

    campaign: Optional[str]
    date: datetime
    invites_created: int
    invites_sent: int
    invites_opened: int
    invites_redeemed: int
    open_rate: Optional[float]
    redemption_rate: Optional[float]
    role_distribution: Optional[dict]
