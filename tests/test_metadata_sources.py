import httpx
import pytest

from XR7.ingestion.metadata_sources import (
    MusicBrainzClient,
    StatementLine,
    reconcile_statement_lines,
)
from XR7.ingestion.metadata_sources.musicbrainz import normalize_isrc

WORK_ID = "8d8bc986-e412-4fbd-8247-cf541d7ff4e8"


def _isrc_payload(iswcs):
    return {
        "recordings": [
            {
                "title": "Crazy Eyes",
                "relations": [
                    {
                        "type": "performance",
                        "work": {"id": WORK_ID, "title": "Crazy Eyes", "iswcs": iswcs},
                    }
                ],
            }
        ]
    }


def _work_payload(iswcs):
    return {
        "id": WORK_ID,
        "title": "Crazy Eyes",
        "iswcs": iswcs,
        "relations": [
            {"type": "composer", "artist": {"id": "a064", "name": "John Oates"}},
            {"type": "lyricist", "artist": {"id": "a064", "name": "John Oates"}},
            {"type": "producer", "artist": {"id": "zzzz", "name": "Not A Writer"}},
        ],
    }


def _client(iswcs, calls=None, isrc_status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        if calls is not None:
            calls.append((request.url.path, request.headers["user-agent"]))
        if request.url.path.startswith("/ws/2/isrc/"):
            if isrc_status != 200:
                return httpx.Response(isrc_status, json={})
            return httpx.Response(200, json=_isrc_payload(iswcs))
        return httpx.Response(200, json=_work_payload(iswcs))

    return MusicBrainzClient(
        "ArtistOS-test/0.1 (test@example.com)",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval_seconds=0,
    )


def test_normalize_isrc():
    assert normalize_isrc("us-rc1 7607839") == "USRC17607839"
    assert normalize_isrc("bad") is None


def test_requires_contactable_user_agent():
    with pytest.raises(ValueError):
        MusicBrainzClient("python-httpx")


def test_resolve_isrc_extracts_writers_only():
    calls = []
    works = _client(["T-345246800-1"], calls).resolve_isrc("USRC17607839")
    assert len(works) == 1
    w = works[0]
    assert w.iswcs == ("T-345246800-1",)
    assert [(c.name, c.role) for c in w.contributors] == [
        ("John Oates", "composer"),
        ("John Oates", "lyricist"),
    ]
    assert all("ArtistOS-test" in ua for _, ua in calls)


def test_resolve_isrc_not_found_returns_empty():
    assert _client([], isrc_status=404).resolve_isrc("USRC17607839") == []


def test_invalid_isrc_raises():
    with pytest.raises(ValueError):
        _client([]).resolve_isrc("nope")


def test_retries_on_503_then_succeeds():
    state = {"n": 0}

    def handler(request):
        if request.url.path.startswith("/ws/2/isrc/"):
            state["n"] += 1
            if state["n"] == 1:
                return httpx.Response(503, headers={"Retry-After": "0"})
            return httpx.Response(200, json={"recordings": []})
        return httpx.Response(200, json={})

    c = MusicBrainzClient(
        "ArtistOS-test/0.1 (t@example.com)",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval_seconds=0,
    )
    assert c.resolve_isrc("USRC17607839") == []
    assert state["n"] == 2


def test_reconcile_iswc_mismatch_is_high():
    c = _client(["T-345246800-1"])
    f = reconcile_statement_lines(
        [StatementLine(isrc="USRC17607839", iswc="T-000000000-0", amount=120.0)], c.resolve_isrc
    )
    assert [x.code for x in f] == ["ISWC_MISMATCH"]
    assert f[0].severity == "high" and f[0].amount_at_stake == 120.0
    assert f[0].evidence_url.endswith(WORK_ID)


def test_reconcile_missing_iswc_on_statement():
    c = _client(["T-345246800-1"])
    f = reconcile_statement_lines([StatementLine(isrc="USRC17607839", amount=5)], c.resolve_isrc)
    assert [x.code for x in f] == ["STATEMENT_MISSING_ISWC"]


def test_reconcile_matching_iswc_formats_no_finding():
    c = _client(["T-345246800-1"])
    f = reconcile_statement_lines(
        [StatementLine(isrc="USRC17607839", iswc="T345246800 1", payee_name="John Oates")],
        c.resolve_isrc,
    )
    assert f == []


def test_reconcile_no_iswc_published():
    c = _client([])
    f = reconcile_statement_lines([StatementLine(isrc="USRC17607839")], c.resolve_isrc)
    assert [x.code for x in f] == ["NO_ISWC_ANYWHERE"]


def test_reconcile_unresolved_and_payee_and_caching():
    c = _client([], isrc_status=404)
    f = reconcile_statement_lines(
        [StatementLine(isrc="USRC17607839"), StatementLine(isrc="USRC17607839")], c.resolve_isrc
    )
    assert [x.code for x in f] == ["ISRC_UNRESOLVED", "ISRC_UNRESOLVED"]

    c2 = _client(["T-345246800-1"])
    f2 = reconcile_statement_lines(
        [StatementLine(isrc="USRC17607839", iswc="T-345246800-1", payee_name="Someone Else")],
        c2.resolve_isrc,
    )
    assert [x.code for x in f2] == ["PAYEE_NOT_CREDITED"]


def test_reconcile_skips_lines_without_isrc():
    assert reconcile_statement_lines([StatementLine(isrc=None)], lambda i: 1 / 0) == []
