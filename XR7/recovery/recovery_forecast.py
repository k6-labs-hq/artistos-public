from __future__ import annotations

from typing import Any


def forecast_recovery_portfolio(base_expected_recovery: float, payer_adjustment: float = 1.0) -> dict[str, Any]:
    """Forecast expected recovery at 30/60/90 day horizons with confidence intervals."""
    base = max(0.0, float(base_expected_recovery)) * max(0.5, min(1.5, float(payer_adjustment or 1.0)))
    r30 = base * 0.35
    r60 = base * 0.65
    r90 = base

    return {
        "expected_recovery_next_30_days": round(r30, 2),
        "expected_recovery_next_60_days": round(r60, 2),
        "expected_recovery_next_90_days": round(r90, 2),
        "confidence_intervals": {
            "30_days": [round(r30 * 0.82, 2), round(r30 * 1.18, 2)],
            "60_days": [round(r60 * 0.82, 2), round(r60 * 1.18, 2)],
            "90_days": [round(r90 * 0.82, 2), round(r90 * 1.18, 2)],
        },
        "payer_adjusted_timelines": {
            "payer_adjustment": round(float(payer_adjustment or 1.0), 6),
        },
    }
