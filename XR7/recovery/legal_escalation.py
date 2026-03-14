from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def maybe_escalate_to_legal(claim: dict[str, Any], blockers: list[dict[str, Any]], threshold_amount: float = 10000.0) -> dict[str, Any]:
    """Escalate claim into legal mode when thresholds and blockers indicate necessity."""
    amount = float(claim.get("recovered_amount") or 0.0)
    status = str(claim.get("status") or "IDENTIFIED")
    has_non_response = any(b.get("type") == "payer_non_response" for b in blockers)

    should_escalate = amount >= threshold_amount or has_non_response or status in {"IN_REVIEW", "ESCALATED"}
    legal_packet = {
        "claim_id": claim.get("id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet_type": "LEGAL_ESCALATION",
        "required_docs": ["evidence_packet", "contract_extract", "timeline_log"],
    }

    return {
        "claim_id": claim.get("id"),
        "legal_threshold_met": should_escalate,
        "legal_packet": legal_packet if should_escalate else None,
        "notify_attorney_role": should_escalate,
        "legal_timeline_days": 30 if should_escalate else 0,
    }
