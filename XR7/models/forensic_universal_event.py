from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ForensicUniversalRoyaltyEvent(Base):
    """Canonical forensic royalty event used by the XR7 workflow pipeline."""

    __tablename__ = "forensic_universal_royalty_events"

    event_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    work_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    artist_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    writer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    publisher_name: Mapped[str | None] = mapped_column(String, nullable=True)
    distributor: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    platform: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    usage_type: Mapped[str | None] = mapped_column(String, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payout_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    payout_currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    statement_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    statement_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_file_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_flags: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    ingestion_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )


class ForensicUniversalRoyaltyEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    work_id: str | None = None
    isrc: str | None = None
    iswc: str | None = None
    title: str | None = None
    artist_name: str | None = None
    writer_name: str | None = None
    publisher_name: str | None = None
    distributor: str | None = None
    platform: str | None = None
    usage_type: str | None = None
    usage_count: int = 0
    payout_amount: float = 0.0
    payout_currency: str = "USD"
    statement_period_start: date | None = None
    statement_period_end: date | None = None
    source_file_id: str | None = None
    confidence_score: float = 0.0
    metadata_flags: str = "{}"
    ingestion_timestamp: datetime


class ForensicUniversalRoyaltyEventCreate(BaseModel):
    work_id: str | None = None
    isrc: str | None = None
    iswc: str | None = None
    title: str | None = None
    artist_name: str | None = None
    writer_name: str | None = None
    publisher_name: str | None = None
    distributor: str | None = None
    platform: str | None = None
    usage_type: str | None = None
    usage_count: int = 0
    payout_amount: float = 0.0
    payout_currency: str = "USD"
    statement_period_start: date | None = None
    statement_period_end: date | None = None
    source_file_id: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata_flags: dict[str, str] | None = None
