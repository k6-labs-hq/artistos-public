"""Pillar 6 — Natural-language conversational messages + weekly story feed."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class MessageCategory(str, enum.Enum):
    ONBOARDING = "onboarding"
    COMFORT = "comfort"
    CLAIM = "claim"
    SOL_ALERT = "sol_alert"
    DEPOSIT = "deposit"
    RECOVERY = "recovery"
    WEEKLY_STORY = "weekly_story"
    SYSTEM = "system"


class ArtistMessage(Base):
    """Outbound message feed entry shown to the artist."""

    __tablename__ = "artist_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        Enum(MessageCategory), nullable=False, default=MessageCategory.SYSTEM
    )
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
