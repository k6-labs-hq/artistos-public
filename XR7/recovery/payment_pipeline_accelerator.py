from __future__ import annotations


def billing_acceleration_status(claim_count: int, failed_disbursements: int = 0) -> dict:
    """Return Celero acceleration signals for pre-auth, batching, prediction and retry posture."""
    batching_efficiency = max(0.1, min(1.0, 1.0 - (failed_disbursements / max(claim_count, 1))))
    return {
        "pre_authorization_checks": "enabled",
        "faster_settlement_prediction_days": max(2, 7 - min(5, claim_count // 10)),
        "payout_batching_optimization": {
            "enabled": True,
            "efficiency_score": round(batching_efficiency, 6),
        },
        "retry_logic": {
            "enabled": True,
            "failed_disbursements": int(failed_disbursements),
            "max_retries": 4,
        },
    }
