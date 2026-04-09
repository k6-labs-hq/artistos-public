"""
SLO Benchmark Tests — REL-201
==============================
Runs a reduced iteration count (20) against key API paths via TestClient
and asserts that p95 latencies stay within the configured SLO thresholds.

These tests are intentionally kept lightweight so they run quickly in CI
while still catching gross regressions.  For full load-test evidence use
scripts/benchmark_slo.py with --iterations 200 or higher.
"""

from __future__ import annotations

import time
import uuid

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession  # reuse the shared in-memory DB
from XR7.api.app import app
from XR7.models.artist import Artist

client = TestClient(app)

# ---------------------------------------------------------------------------
# SLO thresholds (p95, milliseconds) — same as scripts/benchmark_slo.py
# ---------------------------------------------------------------------------
SLO_P95_MS: dict[str, float] = {
    "/health": 100.0,  # generous headroom for in-process overhead
    "anomalies": 600.0,
    "dashboard": 1000.0,
    "earnings_summary": 600.0,
}

_ITERATIONS = 20


def _seed_artist() -> str:
    db = TestSession()
    try:
        artist_id = str(uuid.uuid4())
        db.add(Artist(id=artist_id, name="SLO Test Artist", email=f"slo_{artist_id[:8]}@test.com"))
        db.commit()
        return artist_id
    finally:
        db.close()


def _p95(times_ms: list[float]) -> float:
    if not times_ms:
        return 0.0
    sorted_t = sorted(times_ms)
    idx = max(0, int(len(sorted_t) * 0.95) - 1)
    return sorted_t[idx]


def _measure(path: str) -> list[float]:
    times = []
    for _ in range(_ITERATIONS):
        t0 = time.perf_counter()
        client.get(path)
        times.append((time.perf_counter() - t0) * 1000.0)
    return times


class TestSloHealth:
    def test_health_p95_under_threshold(self):
        times = _measure("/health")
        p95 = _p95(times)
        assert (
            p95 <= SLO_P95_MS["/health"]
        ), f"GET /health p95 = {p95:.1f}ms exceeds SLO of {SLO_P95_MS['/health']:.0f}ms"


class TestSloArtistEndpoints:
    @pytest.fixture(scope="class")
    def artist_id(self):
        return _seed_artist()

    def test_anomalies_p95_under_threshold(self, artist_id):
        times = _measure(f"/artists/{artist_id}/anomalies")
        p95 = _p95(times)
        assert (
            p95 <= SLO_P95_MS["anomalies"]
        ), f"GET /anomalies p95 = {p95:.1f}ms exceeds SLO of {SLO_P95_MS['anomalies']:.0f}ms"

    def test_dashboard_p95_under_threshold(self, artist_id):
        times = _measure(f"/artists/{artist_id}/dashboard")
        p95 = _p95(times)
        assert (
            p95 <= SLO_P95_MS["dashboard"]
        ), f"GET /dashboard p95 = {p95:.1f}ms exceeds SLO of {SLO_P95_MS['dashboard']:.0f}ms"

    def test_earnings_summary_p95_under_threshold(self, artist_id):
        times = _measure(f"/artists/{artist_id}/earnings/summary")
        p95 = _p95(times)
        assert (
            p95 <= SLO_P95_MS["earnings_summary"]
        ), f"GET /earnings/summary p95 = {p95:.1f}ms exceeds SLO of {SLO_P95_MS['earnings_summary']:.0f}ms"

    def test_slo_report_keys_present_in_benchmark_script(self):
        """Smoke test: the standalone benchmark script remains importable and defines thresholds."""
        import importlib.util
        from pathlib import Path

        spec = importlib.util.spec_from_file_location(
            "benchmark_slo",
            Path(__file__).parents[1] / "scripts" / "benchmark_slo.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert hasattr(mod, "SLO_THRESHOLDS_MS")
        assert "/health" in mod.SLO_THRESHOLDS_MS
        assert "/artists/{id}/dashboard" in mod.SLO_THRESHOLDS_MS
