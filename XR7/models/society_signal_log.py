from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class SocietySignalLog(Base):
    __tablename__ = "society_signal_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String, nullable=False)
    signal_type: Mapped[str] = mapped_column(String, nullable=False)
    payer_or_society: Mapped[str] = mapped_column(String, nullable=False, index=True)
    affected_anomaly_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    classification_impact_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
