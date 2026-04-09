from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class IdentityConfidenceBand(str, enum.Enum):
    AUTO_ACCEPT = "AUTO_ACCEPT"
    SOFT_CONFIRM = "SOFT_CONFIRM"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


class IdentityDecisionStatus(str, enum.Enum):
    AUTO_ACCEPTED = "AUTO_ACCEPTED"
    PENDING_SOFT_CONFIRM = "PENDING_SOFT_CONFIRM"
    PENDING_EXPLICIT_CONFIRM = "PENDING_EXPLICIT_CONFIRM"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class ArtistIdentityMatch(Base):
    __tablename__ = "artist_identity_matches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    statement_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("statements.id"), nullable=True, index=True
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_band: Mapped[str] = mapped_column(Enum(IdentityConfidenceBand), nullable=False)
    decision_status: Mapped[str] = mapped_column(Enum(IdentityDecisionStatus), nullable=False)
    decision_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    decision_actor: Mapped[str | None] = mapped_column(String, nullable=True)
    decision_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    matched_profile: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    score_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    chain_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class ArtistIdentityMatchAudit(Base):
    __tablename__ = "artist_identity_match_audits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id: Mapped[str] = mapped_column(
        String, ForeignKey("artist_identity_matches.id"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    chain_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class ArtistIdentityMatchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    statement_id: str | None = None
    confidence_score: float
    confidence_band: IdentityConfidenceBand
    decision_status: IdentityDecisionStatus
    decision_reason: str | None = None
    decision_actor: str | None = None
    decision_at: datetime | None = None
    matched_profile: dict[str, Any]
    score_breakdown: dict[str, Any]
    chain_hash: str
    created_at: datetime


class ArtistIdentityMatchAuditSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    match_id: str
    action: str
    actor: str
    payload: dict[str, Any]
    chain_hash: str
    created_at: datetime
