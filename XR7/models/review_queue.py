from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ReviewSourceType(str, enum.Enum):
    ANOMALY = "ANOMALY"
    CLAIM = "CLAIM"
    EVIDENCE = "EVIDENCE"
    ML_CONFIDENCE = "ML_CONFIDENCE"


class ReviewItemStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ReviewDecisionType(str, enum.Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
    REQUEST_INFO = "REQUEST_INFO"


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String, default=ReviewItemStatus.OPEN.value, index=True)
    assigned_analyst_email: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReviewAssignment(Base):
    __tablename__ = "review_assignments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_item_id: Mapped[str] = mapped_column(
        String, ForeignKey("review_items.id"), nullable=False, index=True
    )
    analyst_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_item_id: Mapped[str] = mapped_column(
        String, ForeignKey("review_items.id"), nullable=False, index=True
    )
    analyst_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class ReviewItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    source_type: str
    source_id: str | None = None
    reason: str
    priority_score: float
    status: ReviewItemStatus
    assigned_analyst_email: str | None = None
    payload: dict | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None


class ReviewAssignmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    review_item_id: str
    analyst_email: str
    assigned_at: datetime
    unassigned_at: datetime | None = None


class ReviewDecisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    review_item_id: str
    analyst_email: str
    decision: ReviewDecisionType
    notes: str | None = None
    created_at: datetime
