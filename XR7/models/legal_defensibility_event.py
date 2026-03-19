from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class LegalDefensibilityEvent(Base):
    __tablename__ = "legal_defensibility_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    anomaly_id: Mapped[str | None] = mapped_column(String, ForeignKey("anomalies.id"), nullable=True)
    claim_id: Mapped[str | None] = mapped_column(String, ForeignKey("claims.id"), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    rule_version: Mapped[str | None] = mapped_column(String, nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_review_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    input_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
