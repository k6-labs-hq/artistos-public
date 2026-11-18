from __future__ import annotations

import os
import time
from typing import Callable

from XR7.ingestion.metadata_sources.models import ResolvedWork
from XR7.ingestion.metadata_sources.musicbrainz import MusicBrainzClient

Resolver = Callable[[str], list[ResolvedWork]]


class CachingResolver:
    """In-process TTL cache around a resolver.

    Empty results (ISRC not linked to a work) are cached for a shorter time so a
    fix upstream is picked up sooner. Errors are never cached. This cache is
    per-process; a shared/persistent cache is a separate follow-up.
    """

    def __init__(self, inner: Resolver, ttl_seconds: float = 86400.0, negative_ttl_seconds: float = 3600.0):
        self._inner = inner
        self._ttl = ttl_seconds
        self._neg_ttl = negative_ttl_seconds
        self._store: dict[str, tuple[float, list[ResolvedWork]]] = {}

    def __call__(self, isrc: str) -> list[ResolvedWork]:
        now = time.monotonic()
        hit = self._store.get(isrc)
        if hit and hit[0] > now:
            return hit[1]
        works = self._inner(isrc)
        self._store[isrc] = (now + (self._ttl if works else self._neg_ttl), works)
        return works


_default: Resolver | None = None


def build_default_resolver() -> Resolver | None:
    """Return a cached MusicBrainz resolver, or None when not configured.

    Enabled by setting ``MUSICBRAINZ_USER_AGENT`` to something like
    ``ArtistOS/1.0 (ops@yourdomain.com)`` (MusicBrainz requires a contactable UA).
    When unset, metadata lookups are off and no network calls are made.
    """
    global _default
    user_agent = os.environ.get("MUSICBRAINZ_USER_AGENT", "").strip()
    if not user_agent:
        return None
    if _default is None:
        _default = CachingResolver(MusicBrainzClient(user_agent).resolve_isrc)
    return _default
