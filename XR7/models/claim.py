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
    FUNDS_RECEIVED = "FUNDS_RECEIVED"
    DISBURSEMENT_FAILED = "DISBURSEMENT_FAILED"
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
    platform_fee_percent: Mapped[float] = mapped_column(Float, nullable=False, default=12.0)
    platform_fee_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    artist_net_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    remittance_method: Mapped[str | None] = mapped_column(String, nullable=True)
    remittance_reference_number: Mapped[str | None] = mapped_column(String, nullable=True)
    remittance_received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trolley_payment_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    trolley_payment_status: Mapped[str | None] = mapped_column(String, nullable=True)
    trolley_fx_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    trolley_local_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    trolley_local_currency: Mapped[str | None] = mapped_column(String, nullable=True)
    payout_retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payout_failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    payer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    payer_contact: Mapped[str | None] = mapped_column(String, nullable=True)
    original_due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    proof_submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    sol_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    governing_law_state: Mapped[str] = mapped_column(String, nullable=False, default="USA")
    contract_type: Mapped[str] = mapped_column(String, nullable=False, default="recording")
    infringement_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    discovery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sol_window_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sol_citation_source: Mapped[str | None] = mapped_column(String, nullable=True)
    communications: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    anomaly_report: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    supporting_documents: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    attorney_file_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attorney_file_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trust_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    attorney_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    legal_defensibility_report: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    claim_strength_rating: Mapped[str | None] = mapped_column(String, nullable=True)
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
    platform_fee_percent: float = 12.0
    platform_fee_amount: float | None = None
    artist_net_amount: float | None = None
    remittance_method: str | None = None
    remittance_reference_number: str | None = None
    remittance_received_at: datetime | None = None
    trolley_payment_id: str | None = None
    trolley_payment_status: str | None = None
    trolley_fx_rate: float | None = None
    trolley_local_amount: float | None = None
    trolley_local_currency: str | None = None
    payout_retry_count: int = 0
    payout_failure_reason: str | None = None
    evidence: dict[str, Any] | None = None
    payer_name: str | None = None
    payer_contact: str | None = None
    original_due_date: datetime | None = None
    proof_submitted_at: datetime | None = None
    grace_period_days: int = 60
    sol_deadline: datetime | None = None
    governing_law_state: str = "USA"
    contract_type: str = "recording"
    infringement_date: datetime | None = None
    discovery_date: datetime | None = None
    sol_window_years: int | None = None
    sol_citation_source: str | None = None
    communications: list[dict[str, Any]] | None = None
    anomaly_report: dict[str, Any] | None = None
    supporting_documents: list[dict[str, Any]] | None = None
    attorney_file_generated: bool = False
    attorney_file_generated_at: datetime | None = None
    trust_score: float | None = None
    attorney_review_required: bool = False
    legal_defensibility_report: dict[str, Any] | None = None
    claim_strength_rating: str | None = None
    created_at: datetime
    updated_at: datetime
