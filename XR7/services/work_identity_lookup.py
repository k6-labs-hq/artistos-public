"""Resolve cross-source work identifiers (ISWC, ISRC) by external lookup.

Royalty data arrives keyed on different identifiers per payer:

- BMI/ASCAP statements carry the PRO's internal work id (`work_no`) +
  the human title.
- MLC indexes by **ISWC** (the composition identifier).
- Distributors carry **ISRC** (the sound-recording identifier).

Cross-source claims require translating between these. The simplest
free source is MusicBrainz, which exposes both ISWC (via Work entities)
and ISRC (via Recording entities) for an `(artist, title)` query.

This module defines a payer-agnostic interface plus a MusicBrainz
adapter. The adapter caches every lookup in the `work_identity_cache`
table — including negative results — so re-running ingestion on the
same corpus is free and we stay inside MusicBrainz's 1 req/sec budget.

See issue #278.
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from sqlalchemy.orm import Session

from XR7.ingestion.metadata_sources.musicbrainz import MusicBrainzClient
from XR7.models.work_identity_cache import WorkIdentityCacheEntry
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Lookups age out after this long. MusicBrainz data is reasonably stable
# but a song's ISWC sometimes gets registered weeks after release, so we
# don't want to cache a negative-result forever.
_CACHE_TTL = timedelta(days=30)

# The 1 req/sec floor is enforced process-wide in
# XR7.ingestion.metadata_sources.musicbrainz.throttle (shared with the ISRC
# resolver). Different workers still pace independently; volumes are low
# enough that we don't need a Redis-coordinated limiter.
_MB_MIN_INTERVAL_SECONDS = 1.0


def _normalize(value: str) -> str:
    """Lowercase + collapse whitespace + strip punctuation noise so cache
    hits don't depend on the caller's casing/spacing conventions."""
    if not value:
        return ""
    lowered = value.lower().strip()
    # Drop punctuation that's typically inconsistent across sources
    # ('feat.' vs 'featuring', stray quotes, leading 'the ', etc.).
    cleaned = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def _cache_id(source: str, artist_normalized: str, title_normalized: str) -> str:
    """Deterministic ID so a re-lookup upserts the same row."""
    h = hashlib.sha256(f"{source}|{artist_normalized}|{title_normalized}".encode()).hexdigest()
    return f"wic_{h[:24]}"


class WorkIdentitySource(Protocol):
    """An adapter that resolves `(artist, title)` to canonical identifiers."""

    name: str  # cache discriminator: "musicbrainz", "discogs", etc.

    def fetch(self, artist: str, title: str) -> dict[str, str | None]:
        """Return `{"iswc": str|None, "isrc": str|None}`.

        Should raise on transport errors. A no-match result is `{"iswc":
        None, "isrc": None}` — distinct from an exception.
        """
        ...


class MusicBrainzSource:
    """MusicBrainz REST adapter. Free, no auth, 1 req/sec rate cap."""

    name = "musicbrainz"
    _BASE = "https://musicbrainz.org/ws/2"

    def __init__(self, user_agent: str | None = None) -> None:
        # MusicBrainz requires a descriptive User-Agent — `python-httpx/X.Y`
        # gets rate-limited harder. Identify ourselves so support requests
        # are answerable if we accidentally hammer the service.
        self.user_agent = (
            user_agent or "XR7/1.0 (https://k6-labs.com; jtrent@k6-labs.com)"
        )
        # HTTP, retry/backoff and the process-wide 1 req/sec throttle live in the
        # shared client so this adapter and the ISRC resolver can't exceed the
        # budget together.
        self._client = MusicBrainzClient(self.user_agent, min_interval_seconds=_MB_MIN_INTERVAL_SECONDS)

    def fetch(self, artist: str, title: str) -> dict[str, str | None]:
        if not (artist and title):
            return {"iswc": None, "isrc": None}

        result: dict[str, str | None] = {"iswc": None, "isrc": None}

        # First lookup: works (ISWC). We query by artist + work title and
        # take the highest-scoring match's first ISWC if it has any.
        work_resp = self._get(
            "/work",
            {
                "query": f'artist:"{artist}" AND work:"{title}"',
                "fmt": "json",
                "limit": "3",
            },
        )
        works = (work_resp or {}).get("works") or []
        for w in works:
            iswcs = w.get("iswcs") or []
            if iswcs:
                result["iswc"] = iswcs[0]
                break

        # Second lookup: recordings (ISRC). Recording entities carry ISRCs
        # directly on the body via inc=isrcs, but the search API doesn't
        # return them inline — we'd need a second GET to /recording/<mbid>?inc=isrcs.
        # That's a third API call per row, doubling our budget. For now
        # we skip ISRC backfill from the search path; callers that need
        # ISRC can wire it later. ISWC is the bridge MLC needs anyway.
        return result

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any] | None:
        """Return parsed JSON, or None on 404 (a genuine no-match).

        Transport/server failures RAISE (per the ``WorkIdentitySource`` contract) so
        ``WorkIdentityLookup`` falls back to cache and does NOT write a negative
        cache row for what was really an outage.
        """
        return self._client.get_json(path, params)


def is_enabled() -> bool:
    """Module-level feature flag. Off by default; set
    XR7_WORK_IDENTITY_LOOKUP=1 to turn on. Keeps the BMI parser
    self-contained and the test suite hermetic when off.
    """
    return os.environ.get("XR7_WORK_IDENTITY_LOOKUP", "").strip().lower() in {"1", "true", "yes"}


class WorkIdentityLookup:
    """Cached lookup over one or more `WorkIdentitySource` adapters."""

    def __init__(
        self,
        db: Session,
        source: WorkIdentitySource | None = None,
        cache_ttl: timedelta = _CACHE_TTL,
    ) -> None:
        self.db = db
        self.source = source or MusicBrainzSource()
        self.cache_ttl = cache_ttl

    def find_iswc(self, artist: str, title: str) -> str | None:
        return self._lookup(artist, title).get("iswc")

    def find_isrc(self, artist: str, title: str) -> str | None:
        return self._lookup(artist, title).get("isrc")

    def _lookup(self, artist: str, title: str) -> dict[str, str | None]:
        artist_n = _normalize(artist)
        title_n = _normalize(title)
        if not (artist_n and title_n):
            return {"iswc": None, "isrc": None}

        cache_id = _cache_id(self.source.name, artist_n, title_n)
        existing = (
            self.db.query(WorkIdentityCacheEntry)
            .filter(WorkIdentityCacheEntry.id == cache_id)
            .first()
        )
        if existing is not None:
            age = datetime.now(timezone.utc) - (
                existing.looked_up_at.replace(tzinfo=timezone.utc)
                if existing.looked_up_at.tzinfo is None
                else existing.looked_up_at
            )
            if age < self.cache_ttl:
                return {"iswc": existing.iswc, "isrc": existing.isrc}

        # Stale or absent — refresh from source.
        try:
            fresh = self.source.fetch(artist, title)
        except Exception:  # noqa: BLE001
            logger.exception(
                "work-identity source raised; falling back to cached or null",
                extra={"source": self.source.name, "artist": artist, "title": title},
            )
            if existing is not None:
                return {"iswc": existing.iswc, "isrc": existing.isrc}
            return {"iswc": None, "isrc": None}

        if existing is None:
            self.db.add(
                WorkIdentityCacheEntry(
                    id=cache_id,
                    source=self.source.name,
                    artist_normalized=artist_n,
                    title_normalized=title_n,
                    artist_raw=artist,
                    title_raw=title,
                    iswc=fresh.get("iswc"),
                    isrc=fresh.get("isrc"),
                    looked_up_at=datetime.now(timezone.utc),
                )
            )
        else:
            existing.iswc = fresh.get("iswc")
            existing.isrc = fresh.get("isrc")
            existing.looked_up_at = datetime.now(timezone.utc)
        self.db.flush()
        return fresh
