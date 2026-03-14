from __future__ import annotations

from typing import Any


def compute_next_best_action(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Return highest-impact, fastest, lowest-effort and best-expected-value actions."""
    if not candidates:
        return {
            "highest_impact_action": None,
            "fastest_action": None,
            "lowest_effort_action": None,
            "highest_expected_recovery_action": None,
        }

    def _pick_max(key: str):
        return max(candidates, key=lambda x: float(x.get(key) or 0.0))

    def _pick_min(key: str):
        return min(candidates, key=lambda x: float(x.get(key) or 0.0))

    return {
        "highest_impact_action": _pick_max("impact_score"),
        "fastest_action": _pick_min("time_days"),
        "lowest_effort_action": _pick_min("effort_hours"),
        "highest_expected_recovery_action": _pick_max("expected_recovery"),
    }
