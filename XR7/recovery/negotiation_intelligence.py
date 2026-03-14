from __future__ import annotations

from statistics import mean
from typing import Any

from XR7.models.claim import Claim


def _claim_variance(claim: Claim) -> float:
    evidence = claim.evidence or {}
    if isinstance(evidence, dict):
        reconciliation = evidence.get("reconciliation") or {}
        return abs(float(reconciliation.get("discrepancy_amount") or 0.0))
    return 0.0


def _payer(claim: Claim) -> str:
    evidence = claim.evidence or {}
    if isinstance(evidence, dict):
        contracts = ((evidence.get("legal_support") or {}).get("contract_basis") or [])
        if contracts and isinstance(contracts, list):
            return str((contracts[0] or {}).get("counterparty") or "Unknown")
    return "Unknown"


def build_negotiation_intel(target_claim: Claim, historical_claims: list[Claim]) -> dict[str, Any]:
    """Return settlement range and strategy using payer/type/variance cohort heuristics."""
    payer = _payer(target_claim)
    claim_type = str(target_claim.claim_type or "UNKNOWN")

    cohort = [
        row
        for row in historical_claims
        if str(row.claim_type or "") == claim_type and _payer(row) == payer
    ]
    if not cohort:
        cohort = [row for row in historical_claims if str(row.claim_type or "") == claim_type]

    recovered_values = [float(row.recovered_amount or 0.0) for row in cohort if float(row.recovered_amount or 0.0) > 0.0]
    avg_recovered = mean(recovered_values) if recovered_values else float(target_claim.recovered_amount or 0.0 or 500.0)
    variance_values = [_claim_variance(row) for row in cohort]
    variance_avg = mean(variance_values) if variance_values else _claim_variance(target_claim)

    ask = max(100.0, avg_recovered * (1.15 if variance_avg < 250 else 1.05))
    midpoint = ask * 0.86
    floor = ask * 0.72

    strategy = "value_first_then_timeline_pressure"
    if variance_avg > 500:
        strategy = "documentation_first_then_split_offer"

    fallback_terms = [
        "Escrow agreement for disputed balance while reconciliation finalizes",
        "Interim partial payment with 30-day true-up window",
        "Joint independent audit with cost-sharing cap",
    ]

    return {
        "claim_id": target_claim.id,
        "cluster": {
            "payer": payer,
            "claim_type": claim_type,
            "cohort_size": len(cohort),
            "avg_variance": round(float(variance_avg), 2),
        },
        "settlement_ranges": {
            "ask": round(float(ask), 2),
            "midpoint": round(float(midpoint), 2),
            "floor": round(float(floor), 2),
        },
        "recommended_strategy": strategy,
        "fallback_terms": fallback_terms,
    }
