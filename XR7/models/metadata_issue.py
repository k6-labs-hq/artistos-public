from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class MetadataIssue(Base):
    __tablename__ = "metadata_issues"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    issue_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False, default="MEDIUM")
    issue_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_system: Mapped[str | None] = mapped_column(String, nullable=True)
    work_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("works.id"), nullable=True, index=True
    )
    event_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("events.id"), nullable=True, index=True
    )
    before_value_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    after_value_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    repair_status: Mapped[str] = mapped_column(
        String, nullable=False, default="DETECTED", index=True
    )
    repair_rationale: Mapped[str | None] = mapped_column(String, nullable=True)
    chain_of_custody_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    projected_leakage_avoided: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    repaired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class MetadataIssueSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    issue_type: str
    severity: str
    issue_key: str
    source_system: str | None = None
    work_id: str | None = None
    event_id: str | None = None
    before_value_json: str
    after_value_json: str
    confidence_score: float
    repair_status: str
    repair_rationale: str | None = None
    chain_of_custody_hash: str | None = None
    projected_leakage_avoided: float
    created_at: datetime
    repaired_at: datetime | None = None
