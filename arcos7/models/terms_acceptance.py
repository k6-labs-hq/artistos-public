"""
TermsAcceptance — immutable audit ledger for Artist T&C acceptances.

Each row records a single acceptance event and is never updated or deleted.
The ``text_sha256`` column stores the SHA-256 hash of the T&C text that was
presented at the moment of acceptance, so the exact version can always be
reconstructed even if the live text changes later.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class TermsAcceptance(Base):
    __tablename__ = "terms_acceptances"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    # Version identifier from arcos7.legal.terms.TERMS_VERSION
    terms_version: Mapped[str] = mapped_column(String, nullable=False)
    # SHA-256 hex-digest of the exact T&C text shown to the artist
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    # Timestamp of acceptance (UTC, set server-side — artist cannot supply it)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    # Network metadata for audit / fraud-prevention purposes
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)


class TermsAcceptanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    terms_version: str
    text_sha256: str
    accepted_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
