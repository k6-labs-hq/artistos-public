from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    founder_cohort_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=2500)
    founder_fee_percent: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    founder_slots_filled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    standard_contingency_fee_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
