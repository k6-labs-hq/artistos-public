from __future__ import annotations

from typing import Any


def generate_recovery_playbook(
    priority_items: list[dict[str, Any]],
    deadline_risk: dict[str, Any],
    evidence_requirements: list[str],
    negotiation_strategy: str,
) -> dict[str, Any]:
    """Generate an artist-wide recovery playbook with timelines and escalation paths."""
    actions = [
        {
            "action": item.get("action") or item.get("action_type") or "REVIEW",
            "item_id": item.get("item_id") or item.get("id"),
            "priority_rank": item.get("priority_rank"),
        }
        for item in priority_items[:10]
    ]

    timelines = {
        "next_7_days": ["File or advance top 3 claims", "Refresh highest-value evidence packets"],
        "next_30_days": ["Execute payer escalation sequence", "Run reconciliation follow-up"],
        "next_90_days": ["Close accepted claims", "Benchmark payer settlement outcomes"],
    }

    escalation = [
        "Tier 1: support ticket",
        "Tier 2: account manager escalation",
        "Tier 3: legal notice",
    ]
    if str(deadline_risk.get("risk_color")) == "RED":
        escalation.append("Emergency legal filing window protection")

    return {
        "recommended_actions": actions,
        "timelines": timelines,
        "escalation_paths": escalation,
        "evidence_requirements": evidence_requirements,
        "negotiation_strategy": negotiation_strategy,
    }
