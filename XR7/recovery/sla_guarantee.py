from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def sla_status_for_artist(claims: list[dict[str, Any]], target_days: int = 45) -> dict[str, Any]:
    """Track SLA timers, breach counts, and forward-looking breach risk."""
    now = datetime.now(timezone.utc)
    timers = []
    breaches = 0
    forecasts = []

    for c in claims:
        created = c.get("created_at")
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created)
            except Exception:  # noqa: BLE001
                created = None
        if not isinstance(created, datetime):
            continue
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        age = max(0, (now - created).days)
        remaining = target_days - age
        breached = remaining < 0 and str(c.get("status")) not in {"PAID", "CLOSED"}
        if breached:
            breaches += 1
        timers.append(
            {
                "claim_id": c.get("id"),
                "age_days": age,
                "days_remaining": remaining,
                "breached": breached,
            }
        )

        forecast_risk = "LOW"
        if remaining <= 0:
            forecast_risk = "HIGH"
        elif remaining <= 7:
            forecast_risk = "MEDIUM"
        forecasts.append({"claim_id": c.get("id"), "forecast_breach_risk": forecast_risk})

    return {
        "sla_timers": timers,
        "sla_breaches": breaches,
        "sla_forecasts": forecasts,
        "target_days": target_days,
    }
