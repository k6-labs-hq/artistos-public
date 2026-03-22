"""
Catalog Fix Issue — XR7 Engine 2.

Persists fixable catalog issues surfaced by the catalog health scorer.
Each record tracks the lifecycle of one actionable item: pending → requested
→ resolved (or expired). A pre-filled email/letter template is generated and
stored in ``template_payload`` when the artist requests the fix.
"""
from __future__ import annotations

import enum
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CatalogFixStatus(str, enum.Enum):
    PENDING = "pending"
    REQUESTED = "requested"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class FixSuggestedAction(str, enum.Enum):
    EMAIL_DISTRIBUTOR = "email_distributor"
    REGISTER_ML = "register_ml"
    FIX_SPLITS = "fix_splits"
    CLAIM_CONTENT_ID = "claim_content_id"
    OTHER = "other"


class CatalogFixCategory(str, enum.Enum):
    METADATA_COMPLETENESS = "metadata_completeness"
    REGISTRATION_STATUS = "registration_status"
    SPLIT_CONFLICTS = "split_conflicts"
    IDENTIFIER_MISMATCHES = "identifier_mismatches"
    CONTENT_ID_ISSUES = "content_id_issues"


class FixPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CatalogFixIssue(Base):
    """One fixable catalog issue for an artist."""

    __tablename__ = "catalog_fix_issues"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    priority: Mapped[str] = mapped_column(
        String, nullable=False, default=FixPriority.MEDIUM.value
    )
    description: Mapped[str] = mapped_column(String, nullable=False)
    # JSON-serialised list[{"title": str, "isrc": str | None}]
    affected_works_json: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_recoverable_usd: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    suggested_action: Mapped[str] = mapped_column(
        String, nullable=False, default=FixSuggestedAction.OTHER.value
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=CatalogFixStatus.PENDING.value, index=True
    )
    requested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Pre-filled template generated when artist hits /request
    template_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def affected_works(self) -> list[dict[str, Any]]:
        if not self.affected_works_json:
            return []
        try:
            return json.loads(self.affected_works_json)
        except (ValueError, TypeError):
            return []

    @affected_works.setter
    def affected_works(self, value: list[dict[str, Any]]) -> None:
        self.affected_works_json = json.dumps(value)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class AffectedWork(BaseModel):
    title: str
    isrc: str | None = None


class CatalogFixIssueSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    category: CatalogFixCategory
    priority: FixPriority
    description: str
    affected_works: list[AffectedWork] = []
    estimated_recoverable_usd: float
    suggested_action: FixSuggestedAction
    status: CatalogFixStatus
    requested_at: datetime | None = None
    resolved_at: datetime | None = None
    expires_at: datetime | None = None
    template_payload: dict | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_with_works(cls, row: CatalogFixIssue) -> "CatalogFixIssueSchema":
        data = {c.key: getattr(row, c.key) for c in row.__table__.columns}  # type: ignore[union-attr]
        data["affected_works"] = row.affected_works
        return cls.model_validate(data)
