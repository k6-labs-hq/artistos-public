from __future__ import annotations

from collections import defaultdict
from typing import Any


def build_underpayment_heatmap(
    anomalies: list[dict[str, Any]], claims: list[dict[str, Any]]
) -> dict[str, Any]:
    """Aggregate leakage by platform/territory/work/payer for heatmap visualizations."""
    by_platform: dict[str, float] = defaultdict(float)
    by_territory: dict[str, float] = defaultdict(float)
    by_work: dict[str, float] = defaultdict(float)

    for a in anomalies:
        value = float(a.get("estimated_recoverable") or 0.0)
        by_platform[str(a.get("platform") or "unknown")] += value
        by_territory[str(a.get("territory") or "GLOBAL")] += value
        by_work[str(a.get("work_id") or "unknown_work")] += value

    by_payer: dict[str, float] = defaultdict(float)
    for c in claims:
        value = float(c.get("recovered_amount") or 0.0)
        by_payer[str(c.get("payer") or "unknown_payer")] += value

    return {
        "leakage_by_platform": dict(by_platform),
        "leakage_by_territory": dict(by_territory),
        "leakage_by_work": dict(by_work),
        "leakage_by_payer": dict(by_payer),
    }
