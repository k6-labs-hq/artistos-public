from __future__ import annotations

from typing import Any


def suggest_unlocks(claim: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    """Recommend targeted fixes to clear blockers and unlock recovery progress."""
    fixes = []
    for blocker in blockers:
        btype = blocker.get("type")
        if btype == "missing_metadata":
            fixes.append("Complete ISRC/ISWC and rights-owner metadata on affected works")
        elif btype == "missing_contract_terms":
            fixes.append("Extract and attach missing contract clauses for rate/audit rights")
        elif btype == "missing_evidence":
            fixes.append("Add line-item payout variance table and source citations")
        elif btype == "payer_non_response":
            fixes.append("Trigger payer-specific escalation and legal notice sequence")
        elif btype == "ambiguous_ownership":
            fixes.append("Resolve ownership ambiguity with split sheet confirmation")

    return {
        "claim_id": claim.get("id"),
        "unlock_suggestions": fixes,
        "recommended_sequence": fixes[:3],
    }
