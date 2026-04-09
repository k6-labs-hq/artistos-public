from __future__ import annotations

from typing import Any


def anomaly_recovery_probability(
    anomaly: dict[str, Any], payer_behavior: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Estimate recoverability for one anomaly using value, confidence, and payer behavior."""
    est = float(anomaly.get("estimated_recoverable") or 0.0)
    confidence = float(anomaly.get("confidence_score") or 0.5)
    severity = str(anomaly.get("severity") or "MEDIUM").upper()

    sev_mult = {"LOW": 0.9, "MEDIUM": 1.0, "HIGH": 1.05, "CRITICAL": 1.1}.get(severity, 1.0)
    payer_accept = float((payer_behavior or {}).get("acceptance_probability") or 0.5)
    dispute = float((payer_behavior or {}).get("dispute_likelihood") or 0.5)

    probability = max(
        0.05,
        min(
            0.99, (confidence * 0.55) + (payer_accept * 0.35) + (0.1 * sev_mult) - (0.15 * dispute)
        ),
    )
    expected_amount = est * probability
    effort_hours = max(2.0, 3.0 + (est / 2000.0) + (dispute * 8.0))
    time_to_resolution = int(round(14 + (dispute * 45) + (effort_hours * 1.5)))

    return {
        "probability_of_recovery": round(probability, 6),
        "expected_recovery_amount": round(expected_amount, 2),
        "expected_effort_hours": round(effort_hours, 2),
        "expected_time_to_resolution": time_to_resolution,
    }
