"""Batch ingestion job models — multi-file upload with per-file progress."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class BatchIngestionJob(Base):
    __tablename__ = "batch_ingestion_jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    org_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    # Unique per artist per upload attempt to support idempotent re-submission
    idempotency_key: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending", index=True
    )  # pending / running / partial / done / failed
    total_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Plain-text summary of any top-level errors
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class BatchIngestionFile(Base):
    __tablename__ = "batch_ingestion_files"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String, ForeignKey("batch_ingestion_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending"
    )  # pending / processing / done / failed
    parsed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class BatchIngestionJobCreate(BaseModel):
    filenames: list[str]
    idempotency_key: str | None = None
    org_id: str | None = None


class BatchIngestionFileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: str
    filename: str
    status: str
    parsed_rows: int
    error_msg: str | None
    processed_at: datetime | None
    created_at: datetime


class BatchIngestionJobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    artist_id: str
    org_id: str | None
    idempotency_key: str | None
    status: str
    total_files: int
    processed_files: int
    failed_files: int
    error_summary: str | None
    submitted_at: datetime
    completed_at: datetime | None
    created_at: datetime
