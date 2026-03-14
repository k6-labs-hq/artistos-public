from __future__ import annotations

from typing import Any


def rank_priority_fast(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Speed-focused prioritization using time-to-cash, responsiveness, evidence, and SLA urgency."""
    scored = []
    for item in items:
        time_to_cash = float(item.get("time_to_cash_days") or 30.0)
        responsiveness = float(item.get("payer_responsiveness") or 0.5)
        evidence = float(item.get("evidence_strength") or 60.0)
        sla_urgency = float(item.get("sla_urgency") or 0.5)
        value = float(item.get("estimated_recoverable") or 0.0)

        speed_score = (
            (value * 0.35)
            + ((1.0 / max(time_to_cash, 1.0)) * 1000.0 * 0.2)
            + (responsiveness * 100.0 * 0.2)
            + (evidence * 0.15)
            + (sla_urgency * 100.0 * 0.1)
        )
        out = dict(item)
        out["speed_priority_score"] = round(speed_score, 4)
        scored.append(out)

    scored.sort(key=lambda x: x.get("speed_priority_score", 0.0), reverse=True)
    for idx, row in enumerate(scored, start=1):
        row["speed_priority_rank"] = idx
    return scored
