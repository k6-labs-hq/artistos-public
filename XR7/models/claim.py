import enum
import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ClaimStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    PREPARED = "PREPARED"
    FILED = "FILED"
    SUBMITTED = "SUBMITTED"
    PROOF_SUBMITTED = "PROOF_SUBMITTED"
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
    payer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    payer_contact: Mapped[str | None] = mapped_column(String, nullable=True)
    original_due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    proof_submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    sol_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    communications: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    anomaly_report: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    supporting_documents: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    attorney_file_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attorney_file_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


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
    payer_name: str | None = None
    payer_contact: str | None = None
    original_due_date: datetime | None = None
    proof_submitted_at: datetime | None = None
    grace_period_days: int = 60
    sol_deadline: datetime | None = None
    communications: list[dict[str, Any]] | None = None
    anomaly_report: dict[str, Any] | None = None
    supporting_documents: list[dict[str, Any]] | None = None
    attorney_file_generated: bool = False
    attorney_file_generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
