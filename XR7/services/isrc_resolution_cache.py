from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Callable

from sqlalchemy.orm import Session

from XR7.ingestion.metadata_sources.models import ResolvedWork, WorkContributor
from XR7.models.isrc_resolution_cache import IsrcResolutionCacheEntry

Resolver = Callable[[str], list[ResolvedWork]]


def _entry_id(source: str, isrc: str) -> str:
    return "irc_" + hashlib.sha256(f"{source}|{isrc}".encode()).hexdigest()[:24]


def _dump(works: list[ResolvedWork]) -> str:
    return json.dumps(
        [
            {
                "isrc": w.isrc,
                "source": w.source,
                "source_url": w.source_url,
                "work_title": w.work_title,
                "source_work_id": w.source_work_id,
                "iswcs": list(w.iswcs),
                "recording_title": w.recording_title,
                "retrieved_at": w.retrieved_at.isoformat(),
                "contributors": [
                    {"name": c.name, "role": c.role, "source_id": c.source_id}
                    for c in w.contributors
                ],
            }
            for w in works
        ]
    )


def _load(payload: str) -> list[ResolvedWork]:
    return [
        ResolvedWork(
            isrc=d["isrc"],
            source=d["source"],
            source_url=d["source_url"],
            work_title=d["work_title"],
            source_work_id=d.get("source_work_id"),
            iswcs=tuple(d.get("iswcs") or ()),
            recording_title=d.get("recording_title"),
            retrieved_at=datetime.fromisoformat(d["retrieved_at"]),
            contributors=tuple(
                WorkContributor(c["name"], c["role"], c.get("source_id"))
                for c in d.get("contributors") or ()
            ),
        )
        for d in json.loads(payload)
    ]


class DbCachingResolver:
    """Database-backed cache around a resolver (shared across workers and restarts).

    Positive results live ``ttl``; "no linked work" results live the shorter
    ``negative_ttl`` so upstream fixes are picked up. Resolver exceptions
    propagate and are never cached, so an outage can't masquerade as "no match".
    Uses flush(), not commit(): the caller owns the transaction.
    """

    def __init__(
        self,
        db: Session,
        inner: Resolver,
        source: str = "musicbrainz",
        ttl: timedelta = timedelta(days=30),
        negative_ttl: timedelta = timedelta(days=7),
    ):
        self.db = db
        self.inner = inner
        self.source = source
        self.ttl = ttl
        self.negative_ttl = negative_ttl

    def __call__(self, isrc: str) -> list[ResolvedWork]:
        entry_id = _entry_id(self.source, isrc)
        existing = self.db.get(IsrcResolutionCacheEntry, entry_id)
        now = datetime.now(timezone.utc)
        if existing is not None:
            looked = existing.looked_up_at
            looked = looked.replace(tzinfo=timezone.utc) if looked.tzinfo is None else looked
            works = _load(existing.payload_json)
            if now - looked < (self.ttl if works else self.negative_ttl):
                return works

        works = self.inner(isrc)  # may raise; deliberately uncached
        payload = _dump(works)
        if existing is None:
            self.db.add(
                IsrcResolutionCacheEntry(
                    id=entry_id,
                    source=self.source,
                    isrc=isrc,
                    payload_json=payload,
                    looked_up_at=now,
                )
            )
        else:
            existing.payload_json = payload
            existing.looked_up_at = now
        self.db.flush()
        return works
