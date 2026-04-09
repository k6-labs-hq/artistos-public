"""
Blackbox Match — XR7 Engine 2.

Tracks unclaimed / black-box royalty pool matches surfaced by the weekly
scanner task. Each record refers to a specific collection society's
redistribution list entry that appears to belong to the artist.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class BlackboxMatchStatus(str, enum.Enum):
    NEW = "new"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    DISMISSED = "dismissed"


class BlackboxMatchType(str, enum.Enum):
    NAME_ALIAS = "name_alias"
    IPI_CAE = "ipi_cae"
    PRO_WRITER_ID = "pro_writer_id"
    TITLE_FUZZY = "title_fuzzy"


class BlackboxSourceList(str, enum.Enum):
    MLC_BLACKBOX = "mlc_blackbox"
    FOREIGN_REDISTRIBUTION = "foreign_redistribution"
    PRO_UNCLAIMED_POOL = "pro_unclaimed_pool"


class BlackboxMatch(Base):
    """One matched entry from a black-box / unclaimed royalty list."""

    __tablename__ = "blackbox_matches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    society: Mapped[str] = mapped_column(String, nullable=False, index=True)
    match_type: Mapped[str] = mapped_column(
        String, nullable=False, default=BlackboxMatchType.NAME_ALIAS.value
    )
    matched_identifier: Mapped[str | None] = mapped_column(String, nullable=True)
    source_list: Mapped[str] = mapped_column(
        String, nullable=False, default=BlackboxSourceList.MLC_BLACKBOX.value
    )
    amount_range_low: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    amount_range_high: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    redistribution_window_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    urgency_days_remaining: Mapped[int] = mapped_column(Integer, nullable=False, default=365)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=BlackboxMatchStatus.NEW.value, index=True
    )
    # FK to anomaly created alongside this match
    anomaly_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("anomalies.id"), nullable=True, index=True
    )
    raw_society_data_json: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class BlackboxMatchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    society: str
    match_type: BlackboxMatchType
    matched_identifier: str | None = None
    source_list: BlackboxSourceList
    amount_range_low: float
    amount_range_high: float
    territory: str | None = None
    redistribution_window_end_date: datetime
    urgency_days_remaining: int
    status: BlackboxMatchStatus
    anomaly_id: str | None = None
    created_at: datetime
    updated_at: datetime
