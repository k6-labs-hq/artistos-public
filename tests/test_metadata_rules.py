import pytest

from XR7.anomaly.engine import AnomalyEngine
from XR7.anomaly.rules.metadata_rules import run_metadata_rules
from XR7.ingestion.metadata_sources import ResolvedWork, WorkContributor
from XR7.ingestion.metadata_sources.resolver import CachingResolver, build_default_resolver
from XR7.recovery.finding_labels import friendly_finding_label

GOOD = "USRC17607839"


def _rw(iswcs=("T-345246800-1",), writers=("John Oates",)):
    return ResolvedWork(
        isrc=GOOD,
        source="musicbrainz",
        source_url="https://musicbrainz.org/work/x",
        work_title="Crazy Eyes",
        iswcs=tuple(iswcs),
        contributors=tuple(WorkContributor(n, "composer") for n in writers),
    )


def _works():
    return [
        {"id": "w1", "title": "Crazy Eyes", "isrc": GOOD, "iswc": "T-000000000-0"},
        {"id": "w2", "title": "Bad Code", "isrc": "NOT-AN-ISRC", "iswc": None},
        {"id": "w3", "title": "No ISRC", "isrc": None, "iswc": None},
    ]


def _events():
    return [{"work_id": "w1", "quantity": 1000, "unit_value": 0.002}]


def test_mismatch_and_invalid_isrc_findings():
    out = run_metadata_rules("a1", _works(), _events(), lambda i: [_rw()])
    by = {f["subtype"]: f for f in out}
    assert set(by) == {"METADATA_ISWC_MISMATCH", "METADATA_INVALID_ISRC_FORMAT"}
    m = by["METADATA_ISWC_MISMATCH"]
    assert m["severity"] == "HIGH" and m["estimated_recoverable"] == 0.0
    assert m["actual_amount"] == 2.0 and m["identity_key"] == "w1:ISWC_MISMATCH"
    assert m["evidence"]["source_url"] == "https://musicbrainz.org/work/x"


def test_resolver_error_is_skipped_not_raised():
    def boom(_):
        raise RuntimeError("network down")

    out = run_metadata_rules("a1", _works(), _events(), boom)
    assert [f["subtype"] for f in out] == ["METADATA_INVALID_ISRC_FORMAT"]


def test_lookup_cap_prioritises_highest_earning():
    works = [{"id": f"w{i}", "title": "t", "isrc": f"USRC1760783{i}", "iswc": None} for i in range(5)]
    events = [{"work_id": f"w{i}", "quantity": 1, "unit_value": float(i)} for i in range(5)]
    seen = []
    run_metadata_rules("a", works, events, lambda i: seen.append(i) or [], max_lookups=2)
    assert seen == ["USRC17607834", "USRC17607833"]


def test_caching_resolver_caches_hits_and_misses_not_errors():
    calls = []
    c = CachingResolver(lambda i: calls.append(i) or [_rw()])
    c(GOOD), c(GOOD)
    assert len(calls) == 1

    n = {"n": 0}

    def flaky(i):
        n["n"] += 1
        if n["n"] == 1:
            raise RuntimeError("x")
        return []

    c2 = CachingResolver(flaky)
    with pytest.raises(RuntimeError):
        c2(GOOD)
    assert c2(GOOD) == [] and n["n"] == 2


def test_default_resolver_off_without_env(monkeypatch):
    monkeypatch.delenv("MUSICBRAINZ_USER_AGENT", raising=False)
    assert build_default_resolver() is None


def test_labels_never_leak_raw_ids():
    assert friendly_finding_label("METADATA_ISWC_MISMATCH").startswith("Work Code")


class _FakeQuery:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *a, **k):
        return self

    def all(self):
        return self._rows


class _W:
    id, title, isrc, iswc = "w1", "Crazy Eyes", GOOD, "T-000000000-0"


class _Session:
    def query(self, model):
        return _FakeQuery([_W()])


def test_engine_hook_off_by_default_and_on_when_injected(monkeypatch):
    monkeypatch.delenv("MUSICBRAINZ_USER_AGENT", raising=False)
    off = AnomalyEngine(None, None)
    assert off._detect_metadata_anomalies("a", _events(), _Session()) == []
    on = AnomalyEngine(None, None, metadata_resolver=lambda i: [_rw()])
    out = on._detect_metadata_anomalies("a", _events(), _Session())
    assert [f["subtype"] for f in out] == ["METADATA_ISWC_MISMATCH"]
