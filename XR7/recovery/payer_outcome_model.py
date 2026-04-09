from __future__ import annotations

from typing import Any


def likely_outcome_for_claim(
    claim: dict[str, Any], payer_profile: dict[str, Any]
) -> dict[str, Any]:
    """Predict likely settlement percent/time/outcome and escalation probability."""
    accept = float(payer_profile.get("settlement_likelihood") or 0.6)
    dispute = float(payer_profile.get("dispute_likelihood") or 0.4)
    settle_time = int((payer_profile.get("response_latency") or {}).get("rolling_30") or 30)

    likely_pct = max(0.25, min(0.95, (accept * 0.7) + ((1.0 - dispute) * 0.3)))
    likely_outcome = "ACCEPTED" if likely_pct >= 0.55 else "PARTIAL_SETTLEMENT"

    return {
        "claim_id": claim.get("id"),
        "likely_settlement_percent": round(likely_pct, 6),
        "likely_settlement_time": settle_time,
        "likely_dispute_outcome": likely_outcome,
        "likely_need_for_escalation": round(dispute, 6),
    }
