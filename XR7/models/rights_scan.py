"""Pillar 5 — Rights registration scan results (ISRC/ISWC/UPC/PRO gaps)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class RightsScanResult(Base):
    __tablename__ = "rights_scan_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    work_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    # e.g. "missing_isrc", "missing_iswc", "missing_pro", "unregistered_foreign"
    gap_type: Mapped[str] = mapped_column(String, nullable=False)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    # Structured auto-generated registration packet
    registration_packet: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    submission_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
