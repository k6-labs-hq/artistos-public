"""Pillar 2 — Referral tree for viral growth loops."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ArtistReferral(Base):
    __tablename__ = "artist_referrals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    referred_artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    # Percentage of the referred artist's recovered amount that flows to referrer
    referral_fee_pct: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    lifetime_earned: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
