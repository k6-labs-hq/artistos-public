from __future__ import annotations

from typing import Any


def clause_action_map(contract_terms: list[dict[str, Any]]) -> dict[str, Any]:
    """Map contract clauses to required actions, escalations, and evidence needs."""
    actions = []
    for term in contract_terms:
        key = str(term.get("term_key") or "unknown")
        row = {
            "clause": key,
            "required_action": "review",
            "escalation_mapping": "standard",
            "evidence_requirement": "supporting_contract_excerpt",
        }
        if "audit" in key:
            row["required_action"] = "prepare_audit_notice"
            row["escalation_mapping"] = "legal_if_denied"
            row["evidence_requirement"] = "audit_rights_clause"
        elif "recoup" in key:
            row["required_action"] = "validate_recoupment_schedule"
            row["escalation_mapping"] = "finance_and_legal"
            row["evidence_requirement"] = "recoupment_ledger"
        elif "rate" in key:
            row["required_action"] = "benchmark_rate_and_compute_shortfall"
            row["escalation_mapping"] = "payer_ops_then_legal"
            row["evidence_requirement"] = "rate_calc_appendix"
        actions.append(row)

    return {"contract_action_map": actions}
