import enum
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class ClaimStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    PREPARED = "PREPARED"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    ACCEPTED = "ACCEPTED"
    PAID = "PAID"
    CLOSED = "CLOSED"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    anomaly_id: Mapped[str] = mapped_column(String, ForeignKey("anomalies.id"), nullable=False)
    claim_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(Enum(ClaimStatus), default=ClaimStatus.IDENTIFIED)
    recovered_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")
    contingency_fee: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClaimSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    anomaly_id: str
    claim_type: str
    status: ClaimStatus
    recovered_amount: float | None = None
    currency: str
    contingency_fee: float | None = None
    evidence: dict | None = None
    created_at: datetime
    updated_at: datetime
