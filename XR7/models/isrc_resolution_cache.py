"""Persistent cache for ISRC -> work resolutions (MusicBrainz et al.).

Sibling of ``work_identity_cache`` (which is keyed on artist+title). This one is
keyed on ISRC and stores the full resolved payload (work title, ISWCs, writer
credits, evidence URL) as JSON so audits can cite the source without re-fetching.
An empty list is a valid cached value: "looked, no linked work".
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class IsrcResolutionCacheEntry(Base):
    __tablename__ = "isrc_resolution_cache"
    __table_args__ = (
        UniqueConstraint("source", "isrc", name="uq_isrc_resolution_cache_key"),
        Index("ix_isrc_resolution_cache_isrc", "isrc"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    isrc: Mapped[str] = mapped_column(String, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    looked_up_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
