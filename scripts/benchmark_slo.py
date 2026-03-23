#!/usr/bin/env python3
"""
SLO Benchmark Script — REL-201
==============================
Runs timed requests against key XR7 API paths using FastAPI's TestClient
(no live server needed) and reports p50 / p95 latencies.

Exit 0  → all SLOs met.
Exit 1  → one or more SLO thresholds exceeded.

Usage:
    python scripts/benchmark_slo.py [--iterations N]

Thresholds (p95, ms):
    /health                          50
    /artists/{id}/anomalies          300
    /artists/{id}/dashboard          500
    /artists/{id}/earnings/summary   300
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.base import SessionLocal
from XR7.models.artist import Artist
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SLO thresholds (p95, milliseconds)
# ---------------------------------------------------------------------------
SLO_THRESHOLDS_MS: dict[str, float] = {
    "/health": 50.0,
    "/artists/{id}/anomalies": 300.0,
    "/artists/{id}/dashboard": 500.0,
    "/artists/{id}/earnings/summary": 300.0,
}


def _seed_artist() -> str:
    """Insert a minimal artist row and return its ID."""
    db = SessionLocal()
    try:
        artist_id = str(uuid.uuid4())
        db.add(
            Artist(
                id=artist_id,
                name="SLO Benchmark Artist",
                email=f"slo_{artist_id[:8]}@benchmark.test",
            )
        )
        db.commit()
        return artist_id
    finally:
        db.close()


def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = max(0, int(len(sorted_data) * p / 100) - 1)
    return sorted_data[idx]


def run_benchmark(iterations: int = 50) -> dict[str, dict[str, float]]:
    client = TestClient(app)
    artist_id = _seed_artist()

    endpoints: list[tuple[str, str]] = [
        ("/health", "/health"),
        (f"/artists/{artist_id}/anomalies", "/artists/{id}/anomalies"),
        (f"/artists/{artist_id}/dashboard", "/artists/{id}/dashboard"),
        (f"/artists/{artist_id}/earnings/summary", "/artists/{id}/earnings/summary"),
    ]

    results: dict[str, list[float]] = {label: [] for _, label in endpoints}

    for _ in range(iterations):
        for path, label in endpoints:
            start = time.perf_counter()
            client.get(path)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            results[label].append(elapsed_ms)

    summary: dict[str, dict[str, float]] = {}
    for label, times in results.items():
        summary[label] = {
            "p50_ms": round(_percentile(times, 50), 2),
            "p95_ms": round(_percentile(times, 95), 2),
            "p99_ms": round(_percentile(times, 99), 2),
            "mean_ms": round(statistics.mean(times), 2),
            "samples": len(times),
            "slo_threshold_ms": SLO_THRESHOLDS_MS.get(label, 9999.0),
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="XR7 SLO Benchmark")
    parser.add_argument("--iterations", type=int, default=50, help="Requests per endpoint")
    args = parser.parse_args()

    print(f"\nXR7 SLO Benchmark — {args.iterations} iterations per endpoint\n")
    print(f"{'Endpoint':<45} {'p50':>8} {'p95':>8} {'p99':>8} {'SLO':>8} {'Status':>8}")
    print("-" * 90)

    results = run_benchmark(args.iterations)
    breaches: list[str] = []

    for label, stats in results.items():
        threshold = stats["slo_threshold_ms"]
        p95 = stats["p95_ms"]
        status = "✅ PASS" if p95 <= threshold else "❌ FAIL"
        if p95 > threshold:
            breaches.append(f"{label}: p95={p95:.1f}ms > threshold={threshold:.0f}ms")
        print(
            f"{label:<45} {stats['p50_ms']:>7.1f}ms {p95:>7.1f}ms "
            f"{stats['p99_ms']:>7.1f}ms {threshold:>7.0f}ms {status:>8}"
        )

    print()
    if breaches:
        print("SLO BREACHES:")
        for b in breaches:
            print(f"  • {b}")
        print()
        return 1

    print("All SLOs met.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
