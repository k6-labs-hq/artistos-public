from __future__ import annotations


def classify_fast_path(
    payer_responsiveness: float,
    evidence_strength: float,
    contract_clarity: float,
    historical_success: float,
    anomaly_subtype: str | None = None,
) -> dict:
    """Classify claims into FAST_PATH/STANDARD/COMPLEX/HIGH FRICTION buckets."""
    score = (
        (payer_responsiveness * 0.35)
        + ((evidence_strength / 100.0) * 0.3)
        + (contract_clarity * 0.2)
        + (historical_success * 0.15)
    )
    subtype = str(anomaly_subtype or "").lower()
    if "ownership" in subtype or "rights" in subtype:
        score -= 0.15

    label = "STANDARD"
    if score >= 0.78:
        label = "FAST_PATH"
    elif score < 0.35:
        label = "HIGH FRICTION"
    elif score < 0.55:
        label = "COMPLEX"

    return {
        "classification": label,
        "classification_score": round(max(0.0, min(1.0, score)), 6),
    }
