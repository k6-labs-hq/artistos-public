from __future__ import annotations


def compute_recovery_speed_score(
    claim_throughput: float,
    payer_mix_risk: float,
    catalog_complexity: float,
    anomaly_density: float,
    evidence_completeness: float,
) -> dict:
    """Compute artist-level recovery speed score (0-100)."""
    raw = (
        (claim_throughput * 35.0)
        + ((1.0 - payer_mix_risk) * 20.0)
        + ((1.0 - catalog_complexity) * 15.0)
        + ((1.0 - anomaly_density) * 15.0)
        + ((evidence_completeness / 100.0) * 15.0)
    )
    score = max(0.0, min(100.0, raw))
    tier = "SLOW"
    if score >= 75:
        tier = "FAST"
    elif score >= 50:
        tier = "MODERATE"
    return {"recovery_speed_score": round(score, 2), "speed_tier": tier}
