#!/usr/bin/env python3
"""
Performance regression checker for CI/CD.

Validates that performance metrics meet defined budgets.

Usage:
    python scripts/ci/check_performance_regression.py benchmarks.json

Exit codes:
    0 - All budgets met
    1 - One or more budgets exceeded
"""

from __future__ import annotations

import json
import sys

# Performance budgets (in seconds)
BUDGETS = {
    "test_health_endpoint_latency": 0.050,  # 50ms
    "test_readiness_endpoint_latency": 0.100,  # 100ms
    "test_openapi_spec_latency": 0.200,  # 200ms
}

# p95 threshold multiplier
P95_MULTIPLIER = 1.5  # p95 should be < 1.5x mean


def check_regression(benchmark_file: str) -> int:
    """Check if any benchmarks exceed performance budgets.

    Args:
        benchmark_file: Path to pytest-benchmark JSON output

    Returns:
        0 if all budgets met, 1 if any exceeded
    """
    try:
        with open(benchmark_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Benchmark file not found: {benchmark_file}")
        return 1
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in benchmark file: {benchmark_file}")
        return 1

    benchmarks = data.get("benchmarks", [])
    if not benchmarks:
        print("⚠️  No benchmarks found in file")
        return 0

    print("🔍 Checking performance budgets...\n")

    failures = []
    for bench in benchmarks:
        name = bench["name"]
        stats = bench["stats"]
        mean = stats["mean"]
        stddev = stats["stddev"]
        p95 = mean + (1.96 * stddev)  # Approximate p95

        budget = BUDGETS.get(name)
        if budget is None:
            print(f"⚠️  {name}: No budget defined (mean: {mean*1000:.2f}ms)")
            continue

        status = "✅" if mean <= budget else "❌"
        print(f"{status} {name}")
        print(f"   Mean: {mean*1000:.2f}ms (budget: {budget*1000:.0f}ms)")
        print(f"   StdDev: ±{stddev*1000:.2f}ms")
        print(f"   p95 (approx): {p95*1000:.2f}ms")

        if mean > budget:
            failures.append(
                {
                    "name": name,
                    "mean": mean,
                    "budget": budget,
                    "exceeded_by": ((mean - budget) / budget) * 100,
                }
            )

        # Check p95 multiplier
        if p95 > (mean * P95_MULTIPLIER):
            print(
                f"   ⚠️  High variance: p95 is {p95/mean:.2f}x mean (expected < {P95_MULTIPLIER}x)"
            )

        print()

    if failures:
        print("\n❌ PERFORMANCE REGRESSION DETECTED\n")
        for fail in failures:
            print(
                f"  {fail['name']}: {fail['mean']*1000:.2f}ms "
                f"(exceeds budget by {fail['exceeded_by']:.1f}%)"
            )
        print(f"\n{len(failures)} of {len(benchmarks)} benchmarks exceeded performance budgets.")
        return 1

    print(f"✅ All {len(benchmarks)} benchmarks meet performance budgets!")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_performance_regression.py <benchmarks.json>")
        sys.exit(1)

    sys.exit(check_regression(sys.argv[1]))
