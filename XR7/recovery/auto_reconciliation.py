from __future__ import annotations

from typing import Any


def auto_reconcile_claim(claim: dict[str, Any], payments: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect silent payer corrections and auto-close claim when reconciled."""
    expected = float(claim.get("recovered_amount") or 0.0)
    total_paid = sum(float(p.get("amount") or 0.0) for p in payments)
    matched = total_paid >= max(1.0, expected)

    return {
        "claim_id": claim.get("id"),
        "silently_corrected": matched,
        "auto_closed": matched,
        "reconciliation_evidence": {
            "expected": round(expected, 2),
            "paid": round(total_paid, 2),
            "delta": round(total_paid - expected, 2),
        },
        "status_update": "CLOSED" if matched else str(claim.get("status") or "IN_REVIEW"),
    }
