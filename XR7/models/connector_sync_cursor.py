"""Connector Sync Cursor — tracks the last fetch position per connector.

Allows connectors to resume incremental fetches without re-processing
the full history.  The cursor_value is provider-specific (ISO timestamp,
sequence number, page token, etc.).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ConnectorSyncCursor(Base):
    __tablename__ = "connector_sync_cursors"
    __table_args__ = (
        UniqueConstraint("artist_id", "integration", name="uq_sync_cursor"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    integration: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Opaque cursor value (ISO timestamp, sequence id, page token…)
    cursor_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_successful_fetch_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetch_count: Mapped[int] = mapped_column(String, nullable=False, default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ConnectorSyncCursorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    artist_id: str
    integration: str
    cursor_value: str | None
    last_successful_fetch_at: datetime | None
    fetch_count: str
    created_at: datetime
    updated_at: datetime
