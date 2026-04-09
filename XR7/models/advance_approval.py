from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ApprovalStage(str, enum.Enum):
    ANALYST = "ANALYST"
    EXECUTIVE = "EXECUTIVE"


class ApprovalDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AdvanceApproval(Base):
    __tablename__ = "advance_approvals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id: Mapped[str] = mapped_column(
        String, ForeignKey("advance_opportunities.id"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(Enum(ApprovalStage), nullable=False)
    decision: Mapped[str] = mapped_column(Enum(ApprovalDecision), nullable=False)
    actor_subject: Mapped[str] = mapped_column(String, nullable=False)
    actor_role: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
