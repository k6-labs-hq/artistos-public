from __future__ import annotations

from typing import Any


def recovery_roi_summary(
    claims: list[dict[str, Any]], anomalies: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compute recovery ROI and payback period for portfolio planning."""
    expected_recovery = sum(float(c.get("recovered_amount") or 0.0) for c in claims)
    if expected_recovery <= 0.0:
        expected_recovery = (
            sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies) * 0.45
        )

    cost_to_recover = max(500.0, (len(claims) * 125.0) + (len(anomalies) * 35.0))
    roi = (expected_recovery - cost_to_recover) / max(cost_to_recover, 1.0)
    monthly_net = max(1.0, expected_recovery / 6.0)
    payback_period = cost_to_recover / monthly_net

    return {
        "cost_to_recover": round(cost_to_recover, 2),
        "expected_recovery": round(expected_recovery, 2),
        "roi": round(roi, 6),
        "payback_period": round(payback_period, 2),
    }
