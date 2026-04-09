from __future__ import annotations

from typing import Any


def portfolio_expected_recovery_value(
    anomalies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    catalog_health: float,
    payer_behavior_rows: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    historical_recovery_rate: float,
) -> dict[str, Any]:
    """Estimate portfolio-level expected recovery value range and horizon."""
    total_est = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
    anomaly_density = len(anomalies) / max(1.0, float(len(contracts) or 1))
    payer_accept = sum(
        float(r.get("acceptance_probability") or 0.5) for r in payer_behavior_rows
    ) / max(1.0, float(len(payer_behavior_rows) or 1))

    health_factor = max(0.6, min(1.3, (catalog_health / 100.0) + 0.4))
    density_penalty = max(0.65, min(1.0, 1.0 - (anomaly_density * 0.03)))
    recovery_rate = max(0.1, min(0.95, float(historical_recovery_rate or 0.5)))

    expected = total_est * recovery_rate * payer_accept * health_factor * density_penalty
    low = expected * 0.82
    high = expected * 1.18

    open_claims = [c for c in claims if str(c.get("status")) not in {"PAID", "CLOSED"}]
    horizon = int(round(30 + (len(open_claims) * 4) + (anomaly_density * 6)))

    return {
        "total_expected_recovery_low": round(max(0.0, low), 2),
        "total_expected_recovery_high": round(max(0.0, high), 2),
        "confidence_interval": [round(max(0.0, low), 2), round(max(0.0, high), 2)],
        "recovery_horizon_days": max(14, horizon),
        "reasoning_summary": (
            "Range uses anomaly density, catalog health, payer acceptance behavior, contract complexity, "
            "and historical recovery rate to estimate portfolio outcomes."
        ),
    }
