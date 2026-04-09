from __future__ import annotations

from typing import Any


def reconstruct_historical_underpayment(
    events: list[dict[str, Any]], payments: list[dict[str, Any]]
) -> dict[str, Any]:
    """Reconstruct expected vs actual earnings and infer root-cause drivers."""
    expected = sum(
        float(
            e.get("expected_amount")
            or (float(e.get("unit_value") or 0.0) * float(e.get("quantity") or 0.0))
        )
        for e in events
    )
    actual = sum(float(p.get("amount") or 0.0) for p in payments)
    delta = expected - actual

    causes = []
    if delta > 0:
        causes.append("underreported_usage_or_rate_mismatch")
    if any(float(e.get("unit_value") or 0.0) <= 0.0 for e in events):
        causes.append("invalid_event_pricing_rows")
    if len(payments) == 0:
        causes.append("missing_payment_records")

    return {
        "expected_earnings": round(expected, 2),
        "actual_earnings": round(actual, 2),
        "delta": round(delta, 2),
        "root_cause_analysis": causes,
    }
