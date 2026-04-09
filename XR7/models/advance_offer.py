from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AdvanceOfferStatus(str, enum.Enum):
    PENDING_ARTIST = "PENDING_ARTIST"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class AdvanceOffer(Base):
    __tablename__ = "advance_offers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(
        String, ForeignKey("advance_opportunities.id"), nullable=False, index=True
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    liquidity_advance_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("recoverable_liquidity_advances.id"),
        nullable=True,
        index=True,
    )
    offered_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    advance_fee_percent: Mapped[float] = mapped_column(Float, nullable=False)
    effective_total_fee_cap_percent: Mapped[float] = mapped_column(Float, nullable=False)
    visible_to_artist: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(
        Enum(AdvanceOfferStatus),
        nullable=False,
        default=AdvanceOfferStatus.PENDING_ARTIST,
        index=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
