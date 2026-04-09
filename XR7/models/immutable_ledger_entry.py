from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ImmutableLedgerEntry(Base):
    __tablename__ = "immutable_ledger_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(String, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    prior_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    entry_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class ImmutableLedgerEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    entry_type: str
    payload_json: str
    prior_hash: str | None
    entry_hash: str
    created_at: datetime


def compute_entry_hash(
    *, artist_id: str, entry_type: str, payload_json: str, prior_hash: str | None
) -> str:
    raw = f"{artist_id}|{entry_type}|{payload_json}|{prior_hash or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
