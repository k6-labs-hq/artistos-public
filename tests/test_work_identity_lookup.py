"""Tests for the work-identity lookup service (MusicBrainz adapter + cache).

The MusicBrainz HTTP adapter is exercised against an in-process stub that
returns canned dicts — we never hit the live API in tests. That gates on
the abstraction we built for exactly this reason: swap the
``WorkIdentitySource`` and the surrounding cache/normalization logic
runs against a known fixture.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from XR7.models.work_identity_cache import WorkIdentityCacheEntry
from XR7.services.work_identity_lookup import (
    WorkIdentityLookup,
    _normalize,
)
from tests.conftest import TestSession


class _FakeSource:
    """In-memory ``WorkIdentitySource`` keyed on normalized inputs."""

    def __init__(self, name: str, answers: dict[tuple[str, str], dict[str, str | None]]):
        self.name = name
        self._answers = answers
        self.call_count = 0

    def fetch(self, artist: str, title: str) -> dict[str, str | None]:
        self.call_count += 1
        key = (_normalize(artist), _normalize(title))
        return self._answers.get(key, {"iswc": None, "isrc": None})


@pytest.fixture
def session():
    s = TestSession()
    try:
        yield s
    finally:
        s.rollback()
        s.close()


def test_normalize_collapses_whitespace_and_punctuation():
    assert _normalize("Some Song!") == "some song"
    assert _normalize("  Two   Spaces  ") == "two spaces"
    assert _normalize("artist's name") == "artist s name"


def test_returns_iswc_from_source(session):
    src = _FakeSource(
        "musicbrainz",
        {("jack tolliver", "broken hearts"): {"iswc": "T-345246800-1", "isrc": None}},
    )
    lookup = WorkIdentityLookup(session, source=src)
    assert lookup.find_iswc("Jack Tolliver", "Broken Hearts") == "T-345246800-1"
    assert src.call_count == 1


def test_cache_hit_skips_second_source_call(session):
    src = _FakeSource(
        "musicbrainz",
        {("jack tolliver", "broken hearts"): {"iswc": "T-345246800-1", "isrc": None}},
    )
    lookup = WorkIdentityLookup(session, source=src)
    lookup.find_iswc("Jack Tolliver", "Broken Hearts")
    lookup.find_iswc("jack  tolliver", "BROKEN HEARTS")  # different casing/spacing
    assert src.call_count == 1, "normalized key should yield a cache hit on the second call"


def test_negative_lookup_is_cached_too(session):
    src = _FakeSource("musicbrainz", {})
    lookup = WorkIdentityLookup(session, source=src)
    assert lookup.find_iswc("Unknown", "Unknown Song") is None
    assert lookup.find_iswc("Unknown", "Unknown Song") is None
    # Without negative-cache the source would be queried twice; ensure
    # we don't pound the API on every re-detection for songs that
    # MusicBrainz doesn't know about.
    assert src.call_count == 1


def test_stale_cache_entry_is_refreshed(session):
    src = _FakeSource(
        "musicbrainz",
        {("jack tolliver", "broken hearts"): {"iswc": "T-345246800-1", "isrc": None}},
    )
    # Seed a stale entry with a different value than what the source will
    # return; after the TTL window passes, lookup should re-query and
    # overwrite.
    stale = WorkIdentityCacheEntry(
        id="wic_test_stale",
        source="musicbrainz",
        artist_normalized="jack tolliver",
        title_normalized="broken hearts",
        artist_raw="Jack Tolliver",
        title_raw="Broken Hearts",
        iswc="T-OLD-VALUE-0",
        isrc=None,
        looked_up_at=datetime.now(timezone.utc) - timedelta(days=400),
    )
    # Use the deterministic cache id so the lookup finds this stale row.
    from XR7.services.work_identity_lookup import _cache_id

    stale.id = _cache_id("musicbrainz", "jack tolliver", "broken hearts")
    session.add(stale)
    session.flush()

    lookup = WorkIdentityLookup(session, source=src, cache_ttl=timedelta(days=30))
    refreshed = lookup.find_iswc("Jack Tolliver", "Broken Hearts")
    assert refreshed == "T-345246800-1"
    assert src.call_count == 1


def test_blank_inputs_short_circuit(session):
    src = _FakeSource("musicbrainz", {})
    lookup = WorkIdentityLookup(session, source=src)
    assert lookup.find_iswc("", "anything") is None
    assert lookup.find_iswc("artist", "") is None
    assert src.call_count == 0


def test_source_exception_falls_back_to_cached_value(session):
    class _Boom:
        name = "musicbrainz"

        def fetch(self, artist: str, title: str):  # noqa: ARG002
            raise RuntimeError("api went sideways")

    from XR7.services.work_identity_lookup import _cache_id

    cached = WorkIdentityCacheEntry(
        id=_cache_id("musicbrainz", "jack tolliver", "broken hearts"),
        source="musicbrainz",
        artist_normalized="jack tolliver",
        title_normalized="broken hearts",
        artist_raw="Jack Tolliver",
        title_raw="Broken Hearts",
        iswc="T-PREVIOUSLY-CACHED-1",
        isrc=None,
        looked_up_at=datetime.now(timezone.utc) - timedelta(days=400),  # stale
    )
    session.add(cached)
    session.flush()

    lookup = WorkIdentityLookup(session, source=_Boom(), cache_ttl=timedelta(days=30))
    # Stale + source raises → we should still return the cached value
    # rather than wiping it or raising. Recovery loop credibility >
    # cache freshness when the upstream is down.
    assert lookup.find_iswc("Jack Tolliver", "Broken Hearts") == "T-PREVIOUSLY-CACHED-1"
