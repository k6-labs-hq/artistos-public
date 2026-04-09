from __future__ import annotations

from statistics import mean
from typing import Any


def build_payer_response_profile(payer_id: str, claim_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute rolling payer responsiveness metrics with anomaly/escalation signals."""
    key = str(payer_id or "unknown").strip().lower()
    rows = [r for r in claim_rows if str(r.get("payer") or "unknown").strip().lower() == key]

    if not rows:
        return {
            "payer_id": payer_id,
            "response_latency": {"rolling_7": 14, "rolling_30": 21, "rolling_90": 30},
            "dispute_likelihood": 0.5,
            "settlement_likelihood": 0.5,
            "escalation_thresholds": {"warn_days": 14, "critical_days": 30},
            "historical_behavior_patterns": ["insufficient_history"],
            "behavior_anomalies": [],
            "auto_escalation_triggers": [],
        }

    latency = [int(r.get("response_days") or 21) for r in rows]
    disputes = [r for r in rows if str(r.get("status")) in {"REJECTED", "ESCALATED", "IN_REVIEW"}]
    settled = [r for r in rows if str(r.get("status")) in {"ACCEPTED", "PAID", "CLOSED"}]

    rolling_7 = int(round(mean(latency[-7:]))) if latency else 21
    rolling_30 = int(round(mean(latency[-30:]))) if latency else rolling_7
    rolling_90 = int(round(mean(latency[-90:]))) if latency else rolling_30

    dispute_likelihood = round(len(disputes) / max(len(rows), 1), 6)
    settlement_likelihood = round(len(settled) / max(len(rows), 1), 6)

    anomalies = []
    if rolling_7 > max(rolling_30 * 1.3, 1):
        anomalies.append(
            {"type": "latency_spike", "rolling_7": rolling_7, "rolling_30": rolling_30}
        )
    if dispute_likelihood >= 0.45:
        anomalies.append({"type": "high_dispute_likelihood", "value": dispute_likelihood})

    triggers = []
    if rolling_7 >= 21:
        triggers.append("escalate_after_21_days")
    if dispute_likelihood >= 0.55:
        triggers.append("immediate_legal_review")

    patterns = [
        "slow_weekly_cycle" if rolling_7 > 14 else "stable_cycle",
        "dispute_heavy" if dispute_likelihood > 0.4 else "cooperative",
    ]

    return {
        "payer_id": payer_id,
        "response_latency": {
            "rolling_7": rolling_7,
            "rolling_30": rolling_30,
            "rolling_90": rolling_90,
        },
        "dispute_likelihood": dispute_likelihood,
        "settlement_likelihood": settlement_likelihood,
        "escalation_thresholds": {
            "warn_days": max(10, rolling_30),
            "critical_days": max(21, rolling_90),
        },
        "historical_behavior_patterns": patterns,
        "behavior_anomalies": anomalies,
        "auto_escalation_triggers": triggers,
    }
