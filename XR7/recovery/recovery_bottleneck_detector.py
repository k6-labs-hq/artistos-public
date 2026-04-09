from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def detect_bottlenecks(
    claims: list[dict[str, Any]],
    evidence_strength_by_claim: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Identify stalled claims and operational blockers across recovery workflow."""
    now = datetime.now(timezone.utc)
    evidence_strength_by_claim = evidence_strength_by_claim or {}
    bottlenecks = []

    for c in claims:
        created_at = c.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except Exception:  # noqa: BLE001
                created_at = None
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_days = int((now - created_at).days) if isinstance(created_at, datetime) else 0
        status = str(c.get("status") or "IDENTIFIED")
        claim_id = str(c.get("id"))
        strength = float(
            (evidence_strength_by_claim.get(claim_id) or {}).get("overall_strength_score") or 100.0
        )

        if status in {"SUBMITTED", "FILED", "IN_REVIEW"} and age_days > 30:
            bottlenecks.append(
                {"claim_id": claim_id, "type": "missing_payer_response", "age_days": age_days}
            )
        if status in {"IDENTIFIED", "PREPARED"} and age_days > 10:
            bottlenecks.append(
                {"claim_id": claim_id, "type": "stalled_claim", "age_days": age_days}
            )
        if strength < 40.0:
            bottlenecks.append(
                {"claim_id": claim_id, "type": "missing_evidence", "strength": strength}
            )

    return {
        "total_bottlenecks": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "summary": {
            "stalled_claims": sum(1 for b in bottlenecks if b["type"] == "stalled_claim"),
            "missing_evidence": sum(1 for b in bottlenecks if b["type"] == "missing_evidence"),
            "missing_payer_response": sum(
                1 for b in bottlenecks if b["type"] == "missing_payer_response"
            ),
        },
    }
