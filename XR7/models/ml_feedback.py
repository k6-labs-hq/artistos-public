from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class MLFeedbackType(str, enum.Enum):
    REVIEW_DECISION = "REVIEW_DECISION"
    CLAIM_OUTCOME = "CLAIM_OUTCOME"
    RECOVERY_RESULT = "RECOVERY_RESULT"
    FORECAST_OUTCOME = "FORECAST_OUTCOME"
    ANOMALY_OUTCOME = "ANOMALY_OUTCOME"


class MLFeedbackEvent(Base):
    __tablename__ = "ml_feedback_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    feedback_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    anomaly_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    claim_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    subtype: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    artist_profile_segment: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    model_prediction: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_decision: Mapped[str | None] = mapped_column(String, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class CalibrationSnapshot(Base):
    __tablename__ = "ml_calibration_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scope_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    alpha: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    beta: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    posterior_mean: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    lower_credible: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    upper_credible: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class MLFeedbackEventCreate(BaseModel):
    feedback_type: MLFeedbackType
    source_type: str | None = None
    source_id: str | None = None
    anomaly_id: str | None = None
    claim_id: str | None = None
    subtype: str | None = None
    category: str | None = None
    artist_profile_segment: str | None = None
    model_version: str | None = None
    model_prediction: float | None = None
    human_decision: str | None = None
    outcome: str | None = None
    estimated_amount: float | None = None
    actual_amount: float | None = None
    payload: dict[str, Any] | None = None


class MLFeedbackEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    feedback_type: MLFeedbackType
    source_type: str | None = None
    source_id: str | None = None
    anomaly_id: str | None = None
    claim_id: str | None = None
    subtype: str | None = None
    category: str | None = None
    artist_profile_segment: str | None = None
    model_version: str | None = None
    model_prediction: float | None = None
    human_decision: str | None = None
    outcome: str | None = None
    estimated_amount: float | None = None
    actual_amount: float | None = None
    payload: dict[str, Any] | None = None
    created_at: datetime


class CalibrationSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    scope_type: str
    scope_key: str
    alpha: float
    beta: float
    sample_count: int
    success_count: int
    failure_count: int
    posterior_mean: float
    lower_credible: float
    upper_credible: float
    last_updated_at: datetime
