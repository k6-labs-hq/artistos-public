from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any


def _days_between(start: datetime | None, end: datetime | None) -> int:
    if not start or not end:
        return 0
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return max(0, int((end - start).days))


def compute_recovery_funnel(anomalies: list[dict[str, Any]], claims: list[dict[str, Any]], deposits: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute anomaly-to-deposit funnel metrics including drop-off and bottlenecks."""
    anomaly_count = len(anomalies)
    claim_count = len(claims)
    accepted = sum(1 for c in claims if str(c.get("status")) in {"ACCEPTED", "PAID", "CLOSED"})
    paid = sum(1 for c in claims if str(c.get("status")) in {"PAID", "CLOSED"})
    deposited = len(deposits)

    stage_times = {
        "identified_to_submitted": [],
        "submitted_to_accepted": [],
        "accepted_to_paid": [],
    }
    for c in claims:
        created = c.get("created_at")
        updated = c.get("updated_at")
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created)
            except Exception:  # noqa: BLE001
                created = None
        if isinstance(updated, str):
            try:
                updated = datetime.fromisoformat(updated)
            except Exception:  # noqa: BLE001
                updated = None
        days = _days_between(created, updated)
        status = str(c.get("status"))
        if status in {"SUBMITTED", "FILED", "IN_REVIEW"}:
            stage_times["identified_to_submitted"].append(days)
        if status in {"ACCEPTED", "PAID", "CLOSED"}:
            stage_times["submitted_to_accepted"].append(days)
        if status in {"PAID", "CLOSED"}:
            stage_times["accepted_to_paid"].append(days)

    averages = {k: (round(mean(v), 2) if v else 0.0) for k, v in stage_times.items()}

    drops = {
        "anomaly_to_claim_dropoff": max(0, anomaly_count - claim_count),
        "claim_to_accepted_dropoff": max(0, claim_count - accepted),
        "accepted_to_paid_dropoff": max(0, accepted - paid),
        "paid_to_deposited_dropoff": max(0, paid - deposited),
    }
    bottleneck = max(drops, key=drops.get) if drops else "none"

    predicted_next = "CLAIM_CREATION"
    if claim_count > 0:
        predicted_next = "ACCEPTANCE" if accepted < claim_count else "DEPOSIT"

    return {
        "counts": {
            "anomalies": anomaly_count,
            "claims": claim_count,
            "accepted": accepted,
            "paid": paid,
            "deposited": deposited,
        },
        "drop_off_points": drops,
        "bottlenecks": {
            "primary": bottleneck,
            "value": drops.get(bottleneck, 0),
        },
        "average_time_in_stage_days": averages,
        "predicted_next_stage": predicted_next,
    }
