"""Pillar 5 — Cash advance offers backed by predicted earnings."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AdvanceStatus(str, enum.Enum):
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DISBURSED = "DISBURSED"
    REPAID = "REPAID"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class RecoverableLiquidityAdvance(Base):
    __tablename__ = "recoverable_liquidity_advances"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    offered_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    predicted_low_forecast: Mapped[float] = mapped_column(Float, nullable=False)
    advance_fee_pct: Mapped[float] = mapped_column(Float, nullable=False, default=3.0)
    status: Mapped[str] = mapped_column(
        Enum(AdvanceStatus), nullable=False, default=AdvanceStatus.OFFERED
    )
    trolley_payment_id: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    offered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
