"""SQLAlchemy model for individual fingerprint match results.

Each row represents a single normalized match result produced by a provider
adapter and stored after orchestrator processing.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class FingerprintMatch(Base):
    __tablename__ = "fingerprint_matches"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(
        String, ForeignKey("fingerprint_jobs.id"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    track_id: Mapped[str | None] = mapped_column(String, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True)
    ipi: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    artist_name: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    match_type: Mapped[str] = mapped_column(String, default="unknown", nullable=False)
    platform: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    royalty_status: Mapped[str] = mapped_column(String, default="unknown", nullable=False)
    anomaly_type: Mapped[str] = mapped_column(String, default="none", nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
