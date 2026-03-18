from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AdvanceOpportunityStatus(str, enum.Enum):
    QUEUED_ANALYST = "QUEUED_ANALYST"
    ANALYST_APPROVED = "ANALYST_APPROVED"
    ANALYST_REJECTED = "ANALYST_REJECTED"
    QUEUED_EXEC = "QUEUED_EXEC"
    EXEC_APPROVED = "EXEC_APPROVED"
    EXEC_REJECTED = "EXEC_REJECTED"
    OFFER_GENERATED = "OFFER_GENERATED"
    EXPIRED = "EXPIRED"


class AdvanceOpportunity(Base):
    __tablename__ = "advance_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False, index=True)
    anomaly_id: Mapped[str | None] = mapped_column(String, ForeignKey("anomalies.id"), nullable=True, index=True)
    claim_id: Mapped[str | None] = mapped_column(String, ForeignKey("claims.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        Enum(AdvanceOpportunityStatus),
        nullable=False,
        default=AdvanceOpportunityStatus.QUEUED_ANALYST,
        index=True,
    )
    model_score: Mapped[float] = mapped_column(Float, nullable=False)
    ensemble_scores: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    predicted_recovery_amount: Mapped[float] = mapped_column(Float, nullable=False)
    max_advance_amount: Mapped[float] = mapped_column(Float, nullable=False)
    proposed_advance_fee_percent: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    executive_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
