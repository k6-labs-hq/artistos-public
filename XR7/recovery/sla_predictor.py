from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def predict_claim_sla_dates(claim: dict[str, Any], payer_behavior: dict[str, Any] | None = None) -> dict[str, Any]:
    """Predict payer response/settlement/deposit dates for a claim."""
    created_at = claim.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except Exception:  # noqa: BLE001
            created_at = None
    if not isinstance(created_at, datetime):
        created_at = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    behavior = payer_behavior or {}
    settle_days = int(behavior.get("average_settlement_time") or 45)
    response_days = max(3, int(round(settle_days * 0.35)))
    deposit_days = max(5, int(round(settle_days * 0.2)))

    response_date = created_at + timedelta(days=response_days)
    settlement_date = created_at + timedelta(days=settle_days)
    deposit_date = settlement_date + timedelta(days=deposit_days)

    return {
        "expected_response_date": response_date.isoformat(),
        "expected_settlement_date": settlement_date.isoformat(),
        "expected_deposit_date": deposit_date.isoformat(),
    }
