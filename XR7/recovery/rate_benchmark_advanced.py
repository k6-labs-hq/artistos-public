from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


def advanced_rate_benchmark(
    events: list[dict[str, Any]], peer_baselines: dict[str, dict[str, float]] | None = None
) -> dict[str, Any]:
    """Compute dynamic platform/territory rate benchmarks and drift outliers."""
    baselines = peer_baselines or {
        "spotify:US": {"expected_cpm": 4.0, "peer_percentile_p50": 0.004},
        "youtube:US": {"expected_cpm": 2.5, "peer_percentile_p50": 0.0025},
        "apple music:US": {"expected_cpm": 6.0, "peer_percentile_p50": 0.006},
    }

    by_bucket: dict[str, list[float]] = defaultdict(list)
    drift_flags = []

    for row in events:
        platform = str(row.get("platform") or "unknown").lower()
        territory = str(row.get("territory") or "GLOBAL").upper()
        key = f"{platform}:{territory}"
        unit_value = float(row.get("unit_value") or 0.0)
        by_bucket[key].append(unit_value)

        baseline = baselines.get(key) or baselines.get(f"{platform}:US")
        if baseline:
            expected = float(baseline.get("peer_percentile_p50") or 0.0)
            if expected > 0 and abs(unit_value - expected) / expected > 0.35:
                drift_flags.append(
                    {
                        "platform": platform,
                        "territory": territory,
                        "observed_rate": unit_value,
                        "expected_rate": expected,
                        "drift_pct": round(abs(unit_value - expected) / expected, 6),
                    }
                )

    curves = []
    for bucket, vals in by_bucket.items():
        p, t = bucket.split(":", 1)
        avg = mean(vals) if vals else 0.0
        baseline = baselines.get(bucket) or baselines.get(f"{p}:US") or {}
        curves.append(
            {
                "platform": p,
                "territory": t,
                "observed_avg_rate": round(avg, 6),
                "expected_rate": round(float(baseline.get("peer_percentile_p50") or 0.0), 6),
                "expected_cpm": float(baseline.get("expected_cpm") or 0.0),
                "peer_percentile_comparison": round(
                    (avg / max(float(baseline.get("peer_percentile_p50") or 1e-6), 1e-6)) * 100.0, 2
                ),
            }
        )

    return {
        "dynamic_rate_curves": curves,
        "territory_platform_benchmarks": curves,
        "rate_drift_anomalies": drift_flags,
        "peer_percentile_comparisons": [
            {
                "platform": c["platform"],
                "territory": c["territory"],
                "percent_of_peer_p50": c["peer_percentile_comparison"],
            }
            for c in curves
        ],
    }
