import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class EventType(str, enum.Enum):
    STREAM = "STREAM"
    SHOW = "SHOW"
    SALE = "SALE"
    SYNC_USAGE = "SYNC_USAGE"
    BRAND_IMPRESSION = "BRAND_IMPRESSION"
    GRANT_AWARD = "GRANT_AWARD"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        # Matches the unique constraint added in migration 20260422_0035, used by
        # ingestion's INSERT...ON CONFLICT DO NOTHING for re-upload dedup. The
        # constraint was previously only in the migration, not the model, which
        # broke SQLite-backed tests that exercise the ingestion path.
        UniqueConstraint(
            "artist_id",
            "event_type",
            "platform",
            "territory",
            "timestamp",
            "quantity",
            "unit_value",
            name="uq_events_dedup",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(Enum(EventType), nullable=False)
    work_id: Mapped[str | None] = mapped_column(String, ForeignKey("works.id"), nullable=True)
    # Denormalized work title preserved from the source statement when no
    # Work record has been matched yet (common during initial ingestion).
    # Anomaly rules use this for per-track aggregation.
    work_title: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    # Source statement this event was parsed from. Nullable because (a) the upload
    # flow commits events before the Statement row exists (see #333) so we don't
    # enforce DB-level FK, and (b) historical rows pre-dating this column stay NULL.
    statement_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    platform: Mapped[str | None] = mapped_column(String, nullable=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_value: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")


class EventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: EventType
    work_id: str | None = None
    work_title: str | None = None
    artist_id: str
    statement_id: str | None = None
    platform: str | None = None
    territory: str | None = None
    timestamp: datetime
    quantity: int
    unit_value: float
    currency: str
