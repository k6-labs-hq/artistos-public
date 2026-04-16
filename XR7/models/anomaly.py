import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
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
    recoverability_class: Mapped[str | None] = mapped_column(String, nullable=True)
    legal_basis: Mapped[str | None] = mapped_column(String, nullable=True)
    redistribution_risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    urgent_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)


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
    recoverability_class: str | None = None
    legal_basis: str | None = None
    redistribution_risk_score: int | None = None
    trust_score: float | None = None
    urgent_flag: bool | None = False
    created_at: datetime
    deleted_at: datetime | None = None


class BlackBoxExpirationSchema(BaseModel):
    payer_or_society: str | None = None
    royalty_type: str | None = None
    is_expired: bool
    expiration_date: str | None = None
    days_remaining: int | None = None
    rule_applied: str | None = None
    explanation: str
    P_already_redistributed: float | None = None
    P_still_recoverable: float | None = None
    p10_expiration_date: str | None = None
    p50_expiration_date: str | None = None
    p90_expiration_date: str | None = None
    redistribution_risk_score: int | None = None
    probability_narrative: str | None = None
    freeze_event: dict[str, Any] | None = None
    model_version: str | None = None


class RecoverabilityClassificationSchema(BaseModel):
    recoverability_class: str
    rationale: str
    legal_basis: str
    recommended_action: str
    confidence_score: float


class RecoverabilityPayloadSchema(BaseModel):
    black_box_expiration: BlackBoxExpirationSchema
    recoverability: RecoverabilityClassificationSchema
    legal_basis: str
    contract_recoverability: dict[str, Any] | None = None
    recoverability_explainer_line: str | None = None
    claim_draft_allowed: bool


class AnomalyWithRecoverabilitySchema(AnomalySchema):
    recovery_probability: dict[str, Any]
    black_box_expiration: BlackBoxExpirationSchema
    recoverability: RecoverabilityClassificationSchema
    legal_basis: str
    contract_recoverability: dict[str, Any] | None = None
    recoverability_explainer_line: str | None = None
    redistribution_risk_score: int | None = None
    trust_score: float | None = None
    urgent_flag: bool | None = None
    claim_draft_allowed: bool


class DetectAnomaliesResponseSchema(BaseModel):
    artist_id: str
    detected: list[dict[str, Any]]


class AnomalyRecoveryProbabilityResponseSchema(BaseModel):
    anomaly_id: str
    probability_of_recovery: float | None = None
    expected_recovery_amount: float | None = None
    expected_effort_hours: float | None = None
    expected_time_to_resolution: int | None = None
    black_box_expiration: BlackBoxExpirationSchema
    recoverability: RecoverabilityClassificationSchema
    legal_basis: str
    contract_recoverability: dict[str, Any] | None = None
    recoverability_explainer_line: str | None = None
    redistribution_risk_score: int | None = None
    trust_score: float | None = None
    urgent_flag: bool | None = None
    claim_draft_allowed: bool


class AnomalyExplainWithRecoverabilitySchema(BaseModel):
    anomaly_id: str
    explanation: str
    black_box_expiration: BlackBoxExpirationSchema | None = None
    recoverability: RecoverabilityClassificationSchema | None = None
    legal_basis: str | None = None
    contract_recoverability: dict[str, Any] | None = None
    recoverability_explainer_line: str | None = None
    redistribution_risk_score: int | None = None
    trust_score: float | None = None
    urgent_flag: bool | None = None
    claim_draft_allowed: bool | None = None
