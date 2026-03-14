from __future__ import annotations

from typing import Any


def payer_risk_score(payer_id: str, behavior: dict[str, Any]) -> dict[str, Any]:
    """Score payer-side risk using behavior profile metrics."""
    acceptance = float(behavior.get("acceptance_probability") or 0.5)
    dispute = float(behavior.get("dispute_likelihood") or 0.5)
    speed = float(behavior.get("average_settlement_time") or 45)
    settlement_pct = float(behavior.get("typical_settlement_percent") or 0.7)
    escalation_complexity = len(behavior.get("escalation_requirements") or [])

    score = 0.0
    score += (1.0 - acceptance) * 30.0
    score += dispute * 30.0
    score += min(30.0, (speed / 90.0) * 20.0)
    score += (1.0 - settlement_pct) * 10.0
    score += min(10.0, escalation_complexity * 2.0)

    normalized = max(0.0, min(100.0, score))
    risk_band = "LOW"
    if normalized >= 70:
        risk_band = "HIGH"
    elif normalized >= 40:
        risk_band = "MEDIUM"

    return {
        "payer_id": payer_id,
        "underpayment_likelihood": round((1.0 - acceptance), 6),
        "dispute_likelihood": round(dispute, 6),
        "settlement_speed": round(speed, 2),
        "evidence_requirements": behavior.get("escalation_requirements") or ["standard_follow_up"],
        "historical_behavior": behavior,
        "risk_score": round(normalized, 2),
        "risk_band": risk_band,
    }
