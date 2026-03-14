from __future__ import annotations

from statistics import mean
from typing import Any


def payer_behavior_profile(payer_id: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    """Build payer behavior metrics from historical claim outcomes."""
    payer_key = str(payer_id or "unknown").strip().lower()
    rows = [c for c in claims if str(c.get("payer", "unknown")).strip().lower() == payer_key]

    if not rows:
        return {
            "payer_id": payer_id,
            "acceptance_probability": 0.5,
            "average_settlement_time": 45,
            "typical_settlement_percent": 0.7,
            "dispute_likelihood": 0.5,
            "escalation_requirements": ["standard_follow_up"],
        }

    accepted = [c for c in rows if str(c.get("status")) in {"ACCEPTED", "PAID", "CLOSED"}]
    disputed = [c for c in rows if str(c.get("status")) in {"REJECTED", "ESCALATED", "IN_REVIEW"}]

    settlement_days = [int(c.get("settlement_days") or 45) for c in rows]
    settlement_pct = [float(c.get("settlement_percent") or 0.7) for c in rows]

    dispute_likelihood = min(1.0, max(0.0, len(disputed) / max(len(rows), 1)))
    escalation = ["standard_follow_up"]
    if dispute_likelihood >= 0.35:
        escalation.append("legal_notice")
    if dispute_likelihood >= 0.6:
        escalation.append("executive_escalation")

    return {
        "payer_id": payer_id,
        "acceptance_probability": round(len(accepted) / max(len(rows), 1), 6),
        "average_settlement_time": int(round(mean(settlement_days))) if settlement_days else 45,
        "typical_settlement_percent": round(mean(settlement_pct), 6) if settlement_pct else 0.7,
        "dispute_likelihood": round(dispute_likelihood, 6),
        "escalation_requirements": escalation,
    }
