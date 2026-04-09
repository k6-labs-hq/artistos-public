from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def auto_file_payload(claim: dict[str, Any], channel: str = "email") -> dict[str, Any]:
    """Build a deterministic auto-filing payload for payer delivery adapters."""
    return {
        "claim_id": claim.get("id"),
        "artist_id": claim.get("artist_id"),
        "channel": channel,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "status": "QUEUED",
        "template": "standard_dispute_notice_v1",
    }


def auto_follow_up_plan(claim: dict[str, Any], cadence_days: int = 7) -> dict[str, Any]:
    return {
        "claim_id": claim.get("id"),
        "enabled": True,
        "cadence_days": max(1, int(cadence_days)),
        "sequence": ["follow_up_1", "follow_up_2", "follow_up_3"],
    }


def auto_escalation_plan(
    claim: dict[str, Any], payer_profile: dict[str, Any] | None = None
) -> dict[str, Any]:
    profile = payer_profile or {}
    triggers = list(profile.get("auto_escalation_triggers") or ["escalate_after_21_days"])
    return {
        "claim_id": claim.get("id"),
        "enabled": True,
        "triggers": triggers,
        "sequence": ["account_manager", "legal_notice", "executive_path"],
    }
