import enum
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AnomalyCategory(str, enum.Enum):
    ROYALTY = "ROYALTY"
    TOURING = "TOURING"
    MERCH = "MERCH"
    SYNC = "SYNC"
    PLATFORM = "PLATFORM"
    BRAND = "BRAND"
    GRANT = "GRANT"


class AnomalySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"


class Anomaly(Base):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    category: Mapped[str] = mapped_column(Enum(AnomalyCategory), nullable=False)
    subtype: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(Enum(AnomalySeverity), nullable=False)
    expected_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_recoverable: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    time_window_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    time_window_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(Enum(AnomalyStatus), default=AnomalyStatus.OPEN)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    feature_snapshot: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AnomalySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    category: AnomalyCategory
    subtype: str
    severity: AnomalySeverity
    expected_amount: float | None = None
    actual_amount: float | None = None
    estimated_recoverable: float | None = None
    confidence_score: float
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    territory: str | None = None
    status: AnomalyStatus
    description: str | None = None
    anomaly_score: float | None = None
    model_version: str | None = None
    feature_snapshot: str | None = None
    created_at: datetime
