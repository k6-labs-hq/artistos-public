from __future__ import annotations

import re
import threading
import time

import httpx

from XR7.ingestion.metadata_sources.models import ResolvedWork, WorkContributor

_ISRC_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{3}\d{7}$")
_WRITER_ROLES = {"composer", "lyricist", "writer", "librettist", "arranger"}


# One process-wide throttle shared by EVERY MusicBrainz caller (this client and
# XR7.services.work_identity_lookup.MusicBrainzSource) so the 1 req/sec budget holds
# even when both run in the same worker.
_THROTTLE_LOCK = threading.Lock()
_LAST_CALL = 0.0


def throttle(min_interval_seconds: float = 1.0) -> None:
    global _LAST_CALL  # noqa: PLW0603
    with _THROTTLE_LOCK:
        wait = min_interval_seconds - (time.monotonic() - _LAST_CALL)
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL = time.monotonic()


def normalize_isrc(value: str | None) -> str | None:
    cleaned = re.sub(r"[\s-]", "", str(value or "")).upper()
    return cleaned if _ISRC_RE.match(cleaned) else None


class MusicBrainzClient:
    """Resolve ISRC -> recording -> work (ISWC, writers) via the MusicBrainz web service.

    MusicBrainz asks for a meaningful User-Agent and at most 1 request/second.
    Both are enforced here. Data is CC0 but incomplete: many works have no ISWC,
    so an empty ``iswcs`` means "not known to MusicBrainz", not "does not exist".
    """

    BASE_URL = "https://musicbrainz.org/ws/2"
    SOURCE = "musicbrainz"

    def __init__(
        self,
        user_agent: str,
        http_client: httpx.Client | None = None,
        min_interval_seconds: float = 1.0,
        max_retries: int = 3,
    ):
        if not user_agent or "/" not in user_agent:
            raise ValueError("MusicBrainz requires a User-Agent like App/1.0 (contact@example.com)")
        self._headers = {"User-Agent": user_agent, "Accept": "application/json"}
        self._client = http_client or httpx.Client(timeout=15.0)
        self._min_interval = min_interval_seconds
        self._max_retries = max_retries

    def get_json(self, path: str, params: dict[str, str]) -> dict | None:
        """Throttled GET returning parsed JSON; None on 404; raises on other failures."""
        return self._get(path, params)

    def _get(self, path: str, params: dict[str, str]) -> dict | None:
        params = {**params, "fmt": "json"}
        for attempt in range(self._max_retries + 1):
            throttle(self._min_interval)
            resp = self._client.get(f"{self.BASE_URL}{path}", params=params, headers=self._headers)
            if resp.status_code == 404:
                return None
            if resp.status_code in (429, 503) and attempt < self._max_retries:
                time.sleep(min(float(resp.headers.get("Retry-After", 2**attempt)), 5.0))
                continue
            if resp.status_code >= 400:
                raise RuntimeError(f"MusicBrainz {path} failed ({resp.status_code}): {resp.text[:200]}")
            return resp.json()
        return None

    def resolve_isrc(self, isrc: str) -> list[ResolvedWork]:
        """Return the works linked to every recording carrying this ISRC (may be empty)."""
        code = normalize_isrc(isrc)
        if code is None:
            raise ValueError(f"Invalid ISRC: {isrc!r}")
        data = self._get(f"/isrc/{code}", {"inc": "work-rels"})
        if not data:
            return []

        results: dict[str, ResolvedWork] = {}
        for recording in data.get("recordings", []):
            for rel in recording.get("relations", []):
                work = rel.get("work")
                if rel.get("type") != "performance" or not work:
                    continue
                work_id = work["id"]
                if work_id in results:
                    continue
                detail = self._get(f"/work/{work_id}", {"inc": "artist-rels"}) or work
                results[work_id] = ResolvedWork(
                    isrc=code,
                    source=self.SOURCE,
                    source_url=f"https://musicbrainz.org/work/{work_id}",
                    source_work_id=work_id,
                    work_title=detail.get("title") or work.get("title", ""),
                    iswcs=tuple(detail.get("iswcs") or work.get("iswcs") or ()),
                    contributors=_contributors(detail),
                    recording_title=recording.get("title"),
                )
        return list(results.values())


def _contributors(work: dict) -> tuple[WorkContributor, ...]:
    seen: set[tuple[str, str]] = set()
    out: list[WorkContributor] = []
    for rel in work.get("relations", []):
        artist = rel.get("artist")
        role = rel.get("type")
        if not artist or role not in _WRITER_ROLES:
            continue
        key = (artist.get("id", ""), role)
        if key in seen:
            continue
        seen.add(key)
        out.append(WorkContributor(name=artist.get("name", ""), role=role, source_id=artist.get("id")))
    return tuple(out)
