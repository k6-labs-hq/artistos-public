from __future__ import annotations

from typing import Any


def classify_blockers(claim: dict[str, Any], evidence_strength: float, metadata_ok: bool, contract_terms_ok: bool) -> dict[str, Any]:
    """Detect blockers preventing claim acceleration and resolution."""
    blockers = []
    if not metadata_ok:
        blockers.append({"type": "missing_metadata", "severity": "high"})
    if not contract_terms_ok:
        blockers.append({"type": "missing_contract_terms", "severity": "high"})
    if evidence_strength < 40.0:
        blockers.append({"type": "missing_evidence", "severity": "critical"})

    status = str(claim.get("status") or "IDENTIFIED")
    if status in {"SUBMITTED", "FILED", "IN_REVIEW"}:
        blockers.append({"type": "payer_non_response", "severity": "medium"})
    if "ownership" in str(claim.get("claim_type") or "").lower():
        blockers.append({"type": "ambiguous_ownership", "severity": "high"})

    return {"claim_id": claim.get("id"), "blockers": blockers}
