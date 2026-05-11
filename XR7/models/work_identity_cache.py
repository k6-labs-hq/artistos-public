"""Cache table for external work-identity lookups (MusicBrainz, Discogs).

External catalog APIs are rate-limited (MusicBrainz: 1 req/sec without auth)
and return the same answer for stable inputs over weeks, so caching the
results lets us re-run ingestion on the same corpus without re-querying
and lets the BMI parser apply ISWC enrichment per-row without pacing
slowdowns. See issue #278 for the broader rationale.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class WorkIdentityCacheEntry(Base):
    """One cached `(source, artist, title) → (iswc, isrc)` answer.

    `artist_normalized` + `title_normalized` are stored lowercase and
    whitespace-trimmed so cache hits don't depend on the caller's casing
    or punctuation conventions. The original strings the lookup was made
    with are kept on `artist_raw` / `title_raw` for audit.

    Negative caches matter: when MusicBrainz has no match, we still want
    to remember that so we don't pound the API on every re-detection.
    `iswc` and `isrc` can both be NULL — interpret that as "we looked,
    nothing found." Use `looked_up_at` + TTL to age them out.
    """

    __tablename__ = "work_identity_cache"
    __table_args__ = (
        UniqueConstraint(
            "source", "artist_normalized", "title_normalized", name="uq_work_identity_cache_key"
        ),
        Index("ix_work_identity_cache_iswc", "iswc"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # "musicbrainz" | "discogs"
    artist_normalized: Mapped[str] = mapped_column(String, nullable=False)
    title_normalized: Mapped[str] = mapped_column(String, nullable=False)
    artist_raw: Mapped[str] = mapped_column(String, nullable=False)
    title_raw: Mapped[str] = mapped_column(String, nullable=False)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True)
    looked_up_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
