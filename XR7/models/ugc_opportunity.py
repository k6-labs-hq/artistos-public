"""
UGC Opportunity — XR7 Engine 2.

Tracks YouTube / TikTok / Meta UGC revenue opportunities found during
content scanning — un-monetized Content ID matches, unauthorized uses, etc.
Each row represents one video/post where the artist's music was detected
but is not yet monetized.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class UGCPlatform(str, enum.Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    META = "meta"
    INSTAGRAM = "instagram"
    OTHER = "other"


class UGCOpportunityStatus(str, enum.Enum):
    DETECTED = "detected"
    CLAIM_DRAFTED = "claim_drafted"
    CLAIM_SUBMITTED = "claim_submitted"
    MONETIZED = "monetized"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class UGCOpportunity(Base):
    """
    One UGC revenue opportunity — a video/post using the artist's music
    without an active monetization claim.
    """

    __tablename__ = "ugc_opportunities"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    # FK to the anomaly created alongside this opportunity
    anomaly_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("anomalies.id"), nullable=True, index=True
    )
    platform: Mapped[str] = mapped_column(
        String, nullable=False, default=UGCPlatform.YOUTUBE.value, index=True
    )
    video_url: Mapped[str] = mapped_column(String, nullable=False)
    video_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    video_title: Mapped[str | None] = mapped_column(String, nullable=True)
    channel_name: Mapped[str | None] = mapped_column(String, nullable=True)
    matched_work_title: Mapped[str | None] = mapped_column(String, nullable=True)
    matched_isrc: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_recoverable: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=UGCOpportunityStatus.DETECTED.value,
        index=True,
    )
    is_monetized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    claim_draft_json: Mapped[str | None] = mapped_column(String, nullable=True)
    content_id_asset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    last_scanned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class UGCOpportunitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    anomaly_id: str | None = None
    platform: UGCPlatform
    video_url: str
    video_id: str | None = None
    video_title: str | None = None
    channel_name: str | None = None
    matched_work_title: str | None = None
    matched_isrc: str | None = None
    estimated_views: int
    estimated_recoverable: float
    status: UGCOpportunityStatus
    is_monetized: bool
    content_id_asset_id: str | None = None
    detected_at: datetime
    last_scanned_at: datetime
    updated_at: datetime
