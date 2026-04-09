"""SQLAlchemy model for fingerprinting jobs.

Each row represents a single fingerprinting request, tracking its lifecycle
from submission through to completion or failure.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class FingerprintJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class FingerprintJobMode(str, enum.Enum):
    REALTIME = "realtime"
    BATCH = "batch"
    REFERENCE = "reference"


class FingerprintJob(Base):
    __tablename__ = "fingerprint_jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum(FingerprintJobStatus),
        default=FingerprintJobStatus.PENDING,
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(
        Enum(FingerprintJobMode),
        default=FingerprintJobMode.REALTIME,
        nullable=False,
    )
    # Comma-separated list of provider names used for this job
    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_s3_key: Mapped[str | None] = mapped_column(String, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    tenant_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    job_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
