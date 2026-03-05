import enum
import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class LedgerRecordType(str, enum.Enum):
    EVENT = "EVENT"
    PAYMENT = "PAYMENT"


class FeedbackOutcome(str, enum.Enum):
    DISMISSED = "DISMISSED"
    FILED = "FILED"
    SETTLED = "SETTLED"
    RECOVERED = "RECOVERED"


class RoyaltyLedgerEntry(Base):
    __tablename__ = "royalty_ledger_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    record_type: Mapped[str] = mapped_column(Enum(LedgerRecordType), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String, nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contract_version: Mapped[str | None] = mapped_column(String, nullable=True)
    work_id: Mapped[str | None] = mapped_column(String, nullable=True)
    event_type: Mapped[str | None] = mapped_column(String, nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    rate: Mapped[float] = mapped_column(Float, default=0.0)
    expected_amount: Mapped[float] = mapped_column(Float, default=0.0)
    received_amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    fx_rate_used: Mapped[float | None] = mapped_column(Float, nullable=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ContractTermSnapshot(Base):
    __tablename__ = "contract_term_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    contract_id: Mapped[str | None] = mapped_column(String, ForeignKey("contracts.id"), nullable=True)
    term_key: Mapped[str] = mapped_column(String, nullable=False)
    term_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    effective_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    extracted_from: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class RecoveryOutcomeFeedback(Base):
    __tablename__ = "recovery_outcome_feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    anomaly_id: Mapped[str | None] = mapped_column(String, ForeignKey("anomalies.id"), nullable=True)
    claim_id: Mapped[str | None] = mapped_column(String, ForeignKey("claims.id"), nullable=True)
    outcome: Mapped[str] = mapped_column(Enum(FeedbackOutcome), nullable=False)
    recovered_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason_code: Mapped[str | None] = mapped_column(String, nullable=True)
    analyst_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class RoyaltyLedgerEntryCreate(BaseModel):
    source: str
    record_type: LedgerRecordType
    source_file: str | None = None
    source_row: int | None = None
    contract_version: str | None = None
    work_id: str | None = None
    event_type: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    quantity: float = 0.0
    rate: float = 0.0
    expected_amount: float = 0.0
    received_amount: float = 0.0
    currency: str = "USD"
    fx_rate_used: float | None = None
    territory: str | None = None


class RoyaltyLedgerEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    source: str
    record_type: LedgerRecordType
    source_file: str | None
    source_row: int | None
    contract_version: str | None
    work_id: str | None
    event_type: str | None
    period_start: date | None
    period_end: date | None
    quantity: float
    rate: float
    expected_amount: float
    received_amount: float
    currency: str
    fx_rate_used: float | None
    territory: str | None
    ingested_at: datetime


class ContractTermSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    contract_id: str | None
    term_key: str
    term_value: str
    confidence_score: float
    effective_start: date | None
    effective_end: date | None
    extracted_from: str | None
    created_at: datetime


class RecoveryOutcomeFeedbackCreate(BaseModel):
    anomaly_id: str | None = None
    claim_id: str | None = None
    outcome: FeedbackOutcome
    recovered_amount: float | None = None
    reason_code: str | None = None
    analyst_note: str | None = None


class RecoveryOutcomeFeedbackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    anomaly_id: str | None
    claim_id: str | None
    outcome: FeedbackOutcome
    recovered_amount: float | None
    reason_code: str | None
    analyst_note: str | None
    created_at: datetime
