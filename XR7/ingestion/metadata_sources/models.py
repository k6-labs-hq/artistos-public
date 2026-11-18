from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class WorkContributor:
    name: str
    role: str  # composer | lyricist | writer | ...
    source_id: str | None = None  # e.g. MusicBrainz artist MBID


@dataclass(frozen=True)
class ResolvedWork:
    """A composition resolved from a recording identifier by an external source."""

    isrc: str
    source: str
    source_url: str
    work_title: str
    source_work_id: str | None = None
    iswcs: tuple[str, ...] = ()
    contributors: tuple[WorkContributor, ...] = ()
    recording_title: str | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
