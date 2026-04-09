from __future__ import annotations

from typing import Any

from XR7.ml.forecaster import EarningsForecaster


class RoyaltyOptimizer:
    def __init__(self):
        self.forecaster = EarningsForecaster()

    def simulate_scenario(self, artist_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        baseline = self.forecaster.forecast([], horizon_days=90)
        base_total = float(baseline.get("predicted_total") or 0.0)
        uplift = 0.0
        if changes.get("distro_switch"):
            uplift += 0.08
        if changes.get("pro_change"):
            uplift += 0.04
        if changes.get("ai_opt_in"):
            uplift += 0.05
        if changes.get("fraud_reduction"):
            uplift += 0.07
        projected = round(base_total * (1.0 + uplift), 2)
        return {
            "artist_id": artist_id,
            "baseline": round(base_total, 2),
            "projected": projected,
            "delta": round(projected - base_total, 2),
            "changes": changes,
        }

    def visualize_delta(self, simulation: dict[str, Any]) -> dict[str, Any]:
        return {
            "chart": "bar",
            "labels": ["baseline", "projected", "delta"],
            "values": [
                simulation.get("baseline"),
                simulation.get("projected"),
                simulation.get("delta"),
            ],
        }
