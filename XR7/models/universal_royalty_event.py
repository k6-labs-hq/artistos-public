from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class UniversalRoyaltyEvent(Base):
    __tablename__ = "universal_royalty_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    work_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    work_title: Mapped[str | None] = mapped_column(String, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    ipi: Mapped[str | None] = mapped_column(String, nullable=True)
    statement_period: Mapped[str | None] = mapped_column(String, nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class UniversalRoyaltyEventRowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    source_type: str
    source_name: str
    record_type: str
    event_type: str
    amount: float
    quantity: float
    unit_value: float
    currency: str
    territory: str | None
    work_id: str | None
    work_title: str | None
    isrc: str | None
    ipi: str | None
    statement_period: str | None
    source_ref: str | None
    metadata_json: str
    ingested_at: datetime
