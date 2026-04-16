"""
Statement upload audit model for XR7 Engine 2.

Every uploaded royalty statement file is tracked here so operators can:
- See what data was loaded for each artist
- Detect duplicate uploads (same file hash, same artist)
- Audit the provenance of every Event/Payment in the database
- Roll back or re-process a statement if the parser is updated
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class Statement(Base):
    """Audit record for an uploaded royalty statement file."""

    __tablename__ = "statements"
    __table_args__ = (
        # Prevents re-processing the same file for the same artist.  The duplicate
        # check in the upload handler sets status=DUPLICATE; this index is the
        # database-level safety net for concurrent uploads.
        UniqueConstraint("artist_id", "file_hash", name="uq_statements_artist_hash"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_hash: Mapped[str] = mapped_column(String, nullable=False)  # SHA-256 of raw bytes
    format_detected: Mapped[str] = mapped_column(
        String, nullable=False
    )  # distrokid / tunecore / etc.
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    events_created: Mapped[int] = mapped_column(Integer, default=0)
    payments_created: Mapped[int] = mapped_column(Integer, default=0)
    skipped_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String, default="PROCESSED"
    )  # PROCESSED / FAILED / DUPLICATE
    error_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    ingestion_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class StatementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    filename: str
    file_hash: str
    format_detected: str
    row_count: int
    events_created: int
    payments_created: int
    skipped_rows: int
    status: str
    error_summary: str | None
    ingestion_metadata_json: str
    uploaded_at: datetime
