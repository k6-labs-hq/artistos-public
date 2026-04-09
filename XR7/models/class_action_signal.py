"""Pillar 8 — Crowdsourced class-action evidence aggregation signals."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ClassActionSignal(Base):
    """Aggregated payer-drift signal across multiple artists — potential class action."""

    __tablename__ = "class_action_signals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payer_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    anomaly_type: Mapped[str] = mapped_column(String, nullable=False)
    affected_artist_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_estimated_loss: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    # List of artist IDs contributing to this signal
    contributing_artist_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    packet_url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="active"
    )  # active | escalated | resolved
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_detected_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
