from __future__ import annotations

from typing import Any


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def score_evidence_strength(
    claim_id: str,
    evidence_packet: dict[str, Any] | None,
    anchor_count: int,
) -> dict[str, Any]:
    """Compute evidence strength scoring dimensions for claim advancement and analyst review."""
    packet = evidence_packet or {}
    proof = (packet.get("proof") or {}) if isinstance(packet, dict) else {}
    legal_support = (packet.get("legal_support") or {}) if isinstance(packet, dict) else {}
    reconciliation = (packet.get("reconciliation") or {}) if isinstance(packet, dict) else {}
    integrity = (packet.get("integrity") or {}) if isinstance(packet, dict) else {}
    metadata = (packet.get("metadata") or {}) if isinstance(packet, dict) else {}

    ledger_rows = len((proof.get("ledger_evidence") or []))
    citations = len((legal_support.get("source_citations") or []))
    contract_basis = len((legal_support.get("contract_basis") or []))
    revision = int(metadata.get("revision") or 1)

    completeness = _clamp_score(
        35.0
        + min(30.0, ledger_rows * 2.0)
        + min(20.0, citations * 1.5)
        + min(15.0, contract_basis * 5.0)
    )

    discrepancy = float(reconciliation.get("discrepancy_amount") or 0.0)
    consistency = _clamp_score(100.0 - min(70.0, discrepancy * 10.0) - max(0, revision - 1) * 3.0)

    provenance = _clamp_score(30.0 + min(35.0, citations * 4.0) + min(35.0, anchor_count * 20.0))

    chain_fields = [
        integrity.get("packet_hash"),
        integrity.get("chain_hash"),
        integrity.get("signature"),
        integrity.get("signature_algorithm"),
    ]
    chain_present = sum(1 for item in chain_fields if item)
    chain_of_custody = _clamp_score((chain_present / len(chain_fields)) * 100.0)

    overall = _clamp_score(
        (completeness * 0.28)
        + (consistency * 0.24)
        + (provenance * 0.22)
        + (chain_of_custody * 0.26)
    )

    return {
        "claim_id": claim_id,
        "completeness_score": round(completeness, 2),
        "consistency_score": round(consistency, 2),
        "provenance_score": round(provenance, 2),
        "chain_of_custody_score": round(chain_of_custody, 2),
        "overall_strength_score": round(overall, 2),
    }
