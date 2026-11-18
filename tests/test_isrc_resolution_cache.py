from datetime import datetime, timedelta, timezone

import httpx
import pytest

from XR7.ingestion.metadata_sources import MusicBrainzClient, ResolvedWork, WorkContributor
from XR7.ingestion.metadata_sources import musicbrainz as mb
from XR7.models.isrc_resolution_cache import IsrcResolutionCacheEntry
from XR7.services.isrc_resolution_cache import DbCachingResolver
from XR7.services.work_identity_lookup import MusicBrainzSource, WorkIdentityLookup
from tests.conftest import TestSession

ISRC = "USRC17607839"


@pytest.fixture
def session():
    s = TestSession()
    s.query(IsrcResolutionCacheEntry).delete()
    s.commit()
    yield s
    s.rollback()
    s.close()


def _work():
    return ResolvedWork(
        isrc=ISRC,
        source="musicbrainz",
        source_url="https://musicbrainz.org/work/x",
        work_title="Crazy Eyes",
        source_work_id="x",
        iswcs=("T-345246800-1",),
        contributors=(WorkContributor("John Oates", "composer", "a064"),),
        recording_title="Crazy Eyes",
    )


def test_db_cache_roundtrip_and_hit(session):
    calls = []
    r = DbCachingResolver(session, lambda i: calls.append(i) or [_work()])
    first = r(ISRC)
    second = DbCachingResolver(session, lambda i: 1 / 0)(ISRC)  # new instance: served from DB
    assert len(calls) == 1
    assert second[0].iswcs == ("T-345246800-1",)
    assert second[0].contributors[0] == WorkContributor("John Oates", "composer", "a064")
    assert second[0].retrieved_at == first[0].retrieved_at


def test_db_cache_negative_has_shorter_ttl(session):
    calls = []
    r = DbCachingResolver(session, lambda i: calls.append(i) or [], negative_ttl=timedelta(days=7))
    r(ISRC)
    r(ISRC)
    assert len(calls) == 1
    row = session.query(IsrcResolutionCacheEntry).one()
    row.looked_up_at = datetime.now(timezone.utc) - timedelta(days=8)
    session.flush()
    r(ISRC)
    assert len(calls) == 2


def test_db_cache_does_not_cache_errors(session):
    def boom(_):
        raise RuntimeError("outage")

    with pytest.raises(RuntimeError):
        DbCachingResolver(session, boom)(ISRC)
    assert session.query(IsrcResolutionCacheEntry).count() == 0


def _source_with(handler) -> MusicBrainzSource:
    src = MusicBrainzSource()
    src._client = MusicBrainzClient(
        src.user_agent,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval_seconds=0,
        max_retries=0,
    )
    return src


def test_existing_source_still_returns_iswc():
    src = _source_with(lambda req: httpx.Response(200, json={"works": [{"iswcs": ["T-1"]}]}))
    assert src.fetch("a", "t") == {"iswc": "T-1", "isrc": None}


def test_existing_source_404_is_a_real_no_match():
    assert _source_with(lambda req: httpx.Response(404)).fetch("a", "t") == {"iswc": None, "isrc": None}


def test_outage_raises_and_is_not_negative_cached(session):
    """Regression: a 503/transport failure used to come back as 'no match' and get
    cached as a negative for 30 days. It must now raise so the lookup skips caching."""
    from XR7.models.work_identity_cache import WorkIdentityCacheEntry

    session.query(WorkIdentityCacheEntry).delete()
    session.commit()
    src = _source_with(lambda req: httpx.Response(503))
    with pytest.raises(RuntimeError):
        src.fetch("outage artist", "outage title")
    lookup = WorkIdentityLookup(session, source=src)
    assert lookup.find_iswc("outage artist", "outage title") is None
    assert session.query(WorkIdentityCacheEntry).count() == 0


def test_throttle_is_shared_across_callers(monkeypatch):
    sleeps = []
    monkeypatch.setattr(mb.time, "sleep", lambda s: sleeps.append(s))
    mb._LAST_CALL = mb.time.monotonic()
    mb.throttle(1.0)  # a call "just happened" via the other caller
    assert sleeps and 0 < sleeps[0] <= 1.0
