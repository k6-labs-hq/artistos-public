from __future__ import annotations

from typing import Any


def optimize_recovery_playbook(
    base_playbook: dict[str, Any], payer_profile: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Optimize playbook sequence by payer behavior and estimate uplift/time savings."""
    profile = payer_profile or {}
    dispute = float(profile.get("dispute_likelihood") or 0.4)

    sequence = ["evidence_package", "submission", "follow_up", "escalation"]
    if dispute > 0.5:
        sequence = [
            "evidence_package",
            "legal_precheck",
            "submission",
            "escalation",
            "executive_path",
        ]

    return {
        "payer_specific_optimal_sequences": sequence,
        "expected_time_savings_days": 4 if dispute <= 0.5 else 7,
        "expected_recovery_uplift_pct": 0.08 if dispute <= 0.5 else 0.14,
        "recommended_evidence_order": [
            "contract_basis",
            "line_item_shortfall",
            "integrity_manifest",
            "supporting_statements",
        ],
        "base_playbook": base_playbook,
    }
