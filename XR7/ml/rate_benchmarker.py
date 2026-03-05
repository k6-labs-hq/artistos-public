"""
Comparable-Rate Benchmarker for XR7 Engine 2.

Artists are often underpaid not because a payment is missing entirely, but
because the rate applied is below the industry standard.  This module
maintains configurable benchmark rates for each event type and territory,
then compares each artist's actual payment rates against those benchmarks to:

1. Identify rate tiers (ABOVE_MARKET, AT_MARKET, BELOW_MARKET, CRITICAL).
2. Quantify the estimated underpayment per event / payment.
3. Produce a per-category underpayment report for use in claim evidence packets.

Default benchmark rates are based on publicly available industry data as of
2024.  They should be updated regularly and can be overridden per deployment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Benchmark data
# ---------------------------------------------------------------------------

# Structure: {event_type: {territory: {"p25": ..., "p50": ..., "p75": ...}}}
# p25 = 25th percentile (low end of market)
# p50 = median (true market rate)
# p75 = 75th percentile (upper end of market)
DEFAULT_BENCHMARKS: dict[str, dict[str, dict[str, float]]] = {
    "STREAM": {
        "DEFAULT": {"p25": 0.0030, "p50": 0.0040, "p75": 0.0055},
        "US":      {"p25": 0.0032, "p50": 0.0042, "p75": 0.0060},
        "GB":      {"p25": 0.0028, "p50": 0.0038, "p75": 0.0052},
    },
    "SALE": {
        "DEFAULT": {"p25": 0.05,  "p50": 0.09,   "p75": 0.15},
        "US":      {"p25": 0.06,  "p50": 0.10,   "p75": 0.18},
    },
    "SYNC_USAGE": {
        # Sync licence fees vary enormously by usage type; these are
        # typical per-minute/per-placement rates for indie artists.
        "DEFAULT": {"p25": 500.0, "p50": 2000.0, "p75": 10000.0},
        "US":      {"p25": 750.0, "p50": 3000.0, "p75": 15000.0},
    },
    "SHOW": {
        # Per-show guarantees for emerging/mid-level artists (USD)
        "DEFAULT": {"p25": 500.0,  "p50": 2500.0,  "p75": 10000.0},
        "US":      {"p25": 750.0,  "p50": 3000.0,  "p75": 12000.0},
    },
    "BRAND_IMPRESSION": {
        # CPM-style rate (cost per 1,000 impressions)
        "DEFAULT": {"p25": 0.002, "p50": 0.010, "p75": 0.050},
    },
}

# Rate-tier thresholds (fraction of p50 median)
_ABOVE_MARKET_MULTIPLIER = 1.10     # > 110 % of median
_AT_MARKET_LOWER = 0.90             # 90–110 % of median → AT_MARKET
_BELOW_MARKET_LOWER = 0.50          # 50–90 % of median → BELOW_MARKET
# Below 50 % of median → CRITICAL


class RateTier:
    ABOVE_MARKET = "ABOVE_MARKET"
    AT_MARKET = "AT_MARKET"
    BELOW_MARKET = "BELOW_MARKET"
    CRITICAL = "CRITICAL"
    NO_BENCHMARK = "NO_BENCHMARK"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_benchmark(
    event_type: str,
    territory: str | None,
    benchmarks: dict,
) -> dict | None:
    """Return the benchmark dict for a given event_type / territory."""
    et_bench = benchmarks.get(event_type.upper())
    if et_bench is None:
        return None
    if territory:
        for key in (territory.upper(), territory.upper()[:2]):
            if key in et_bench:
                return et_bench[key]
    return et_bench.get("DEFAULT")


def _classify_rate_tier(actual: float, p50: float) -> str:
    if p50 <= 0:
        return RateTier.NO_BENCHMARK
    ratio = actual / p50
    if ratio >= _ABOVE_MARKET_MULTIPLIER:
        return RateTier.ABOVE_MARKET
    if ratio >= _AT_MARKET_LOWER:
        return RateTier.AT_MARKET
    if ratio >= _BELOW_MARKET_LOWER:
        return RateTier.BELOW_MARKET
    return RateTier.CRITICAL


# ---------------------------------------------------------------------------
# Core comparison function
# ---------------------------------------------------------------------------

def compare_event_rates(
    artist_id: str,
    events: list[dict],
    benchmarks: dict | None = None,
) -> list[dict]:
    """
    Compare each event's ``unit_value`` against the applicable benchmark.

    Parameters
    ----------
    artist_id:
        Used to populate returned result dicts.
    events:
        List of event dicts.  Each dict should have ``event_type``,
        ``unit_value``, ``quantity``, and optionally ``territory``.
    benchmarks:
        Override the default benchmark tables.

    Returns
    -------
    List of comparison dicts, one per input event, each containing:
    - ``event_type``, ``unit_value``, ``territory``
    - ``benchmark_p25/p50/p75``
    - ``rate_tier``: see :class:`RateTier`
    - ``shortfall_per_unit``: how far below the median the rate is (0 if at/above)
    - ``estimated_underpayment``: shortfall_per_unit × quantity
    """
    bench = benchmarks or DEFAULT_BENCHMARKS
    results: list[dict] = []

    for event in events:
        et = str(event.get("event_type", ""))
        uv = float(event.get("unit_value", 0.0) or 0.0)
        qty = float(event.get("quantity", 1) or 1)
        territory = event.get("territory")

        bm = _get_benchmark(et, territory, bench)
        if bm is None:
            results.append(
                {
                    "artist_id": artist_id,
                    "event_type": et,
                    "unit_value": uv,
                    "quantity": qty,
                    "territory": territory,
                    "benchmark_p25": None,
                    "benchmark_p50": None,
                    "benchmark_p75": None,
                    "rate_tier": RateTier.NO_BENCHMARK,
                    "shortfall_per_unit": 0.0,
                    "estimated_underpayment": 0.0,
                }
            )
            continue

        p25, p50, p75 = bm["p25"], bm["p50"], bm["p75"]
        tier = _classify_rate_tier(uv, p50)
        shortfall = max(0.0, p50 - uv)
        underpayment = round(shortfall * qty, 4)

        results.append(
            {
                "artist_id": artist_id,
                "event_type": et,
                "unit_value": uv,
                "quantity": qty,
                "territory": territory,
                "benchmark_p25": p25,
                "benchmark_p50": p50,
                "benchmark_p75": p75,
                "rate_tier": tier,
                "shortfall_per_unit": round(shortfall, 6),
                "estimated_underpayment": underpayment,
            }
        )

    return results


# ---------------------------------------------------------------------------
# Aggregate report
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkReport:
    """Summary of rate comparison results for one artist."""

    artist_id: str
    total_estimated_underpayment: float
    by_event_type: dict[str, dict] = field(default_factory=dict)
    critical_count: int = 0
    below_market_count: int = 0
    at_market_count: int = 0
    above_market_count: int = 0
    comparisons: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "artist_id": self.artist_id,
            "total_estimated_underpayment": round(self.total_estimated_underpayment, 4),
            "by_event_type": self.by_event_type,
            "tier_counts": {
                "CRITICAL": self.critical_count,
                "BELOW_MARKET": self.below_market_count,
                "AT_MARKET": self.at_market_count,
                "ABOVE_MARKET": self.above_market_count,
            },
            "comparisons": self.comparisons,
        }


class RateBenchmarker:
    """
    High-level interface for rate benchmarking.

    Usage::

        benchmarker = RateBenchmarker()
        report = benchmarker.benchmark(artist_id, events)
    """

    def __init__(self, benchmarks: dict | None = None):
        self._benchmarks = benchmarks or DEFAULT_BENCHMARKS

    def benchmark(self, artist_id: str, events: list[dict]) -> BenchmarkReport:
        """
        Run a full rate comparison for all events and return a
        :class:`BenchmarkReport`.
        """
        comparisons = compare_event_rates(artist_id, events, self._benchmarks)

        total_underpayment = 0.0
        by_type: dict[str, dict] = {}
        critical_count = below_count = at_count = above_count = 0

        for c in comparisons:
            total_underpayment += c["estimated_underpayment"]
            et = c["event_type"]
            tier = c["rate_tier"]

            if et not in by_type:
                by_type[et] = {
                    "event_count": 0,
                    "total_underpayment": 0.0,
                    "worst_tier": tier,
                    "avg_unit_value": 0.0,
                    "_values": [],
                }
            by_type[et]["event_count"] += 1
            by_type[et]["total_underpayment"] += c["estimated_underpayment"]
            by_type[et]["_values"].append(c["unit_value"])

            # Track worst tier (most problematic)
            _tier_order = {
                RateTier.CRITICAL: 0,
                RateTier.BELOW_MARKET: 1,
                RateTier.AT_MARKET: 2,
                RateTier.ABOVE_MARKET: 3,
                RateTier.NO_BENCHMARK: 4,
            }
            current_worst = by_type[et]["worst_tier"]
            if _tier_order.get(tier, 4) < _tier_order.get(current_worst, 4):
                by_type[et]["worst_tier"] = tier

            if tier == RateTier.CRITICAL:
                critical_count += 1
            elif tier == RateTier.BELOW_MARKET:
                below_count += 1
            elif tier == RateTier.AT_MARKET:
                at_count += 1
            elif tier == RateTier.ABOVE_MARKET:
                above_count += 1

        # Finalise per-type averages
        for et, summary in by_type.items():
            vals = summary.pop("_values", [])
            summary["avg_unit_value"] = round(float(np.mean(vals)) if vals else 0.0, 6)
            summary["total_underpayment"] = round(summary["total_underpayment"], 4)

        return BenchmarkReport(
            artist_id=artist_id,
            total_estimated_underpayment=total_underpayment,
            by_event_type=by_type,
            critical_count=critical_count,
            below_market_count=below_count,
            at_market_count=at_count,
            above_market_count=above_count,
            comparisons=comparisons,
        )
