from __future__ import annotations

from typing import Any

from XR7.recovery.black_box_expiration import evaluate_black_box_expiration_for_anomaly


RECOVERABLE = "Recoverable"
POTENTIALLY_CONTRACT = "Potentially Recoverable (Contract-Based)"
EXPIRED_REDIS = "Expired (Black-Box Redistributed)"
COPYRIGHT_DAMAGES = "Recoverable via Copyright Damages"
FUTURE_PREVENTION = "Future Leakage Prevention Only"


_ALLOWED_FOR_CLAIMS = {RECOVERABLE, POTENTIALLY_CONTRACT, COPYRIGHT_DAMAGES}


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(t in text for t in terms)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def classify_recoverability(
    anomaly_like: dict[str, Any],
    *,
    black_box_result: dict[str, Any] | None = None,
    contract_metadata: dict[str, Any] | None = None,
    metadata_repair_confidence: float | None = None,
) -> dict[str, Any]:
    black_box = black_box_result or evaluate_black_box_expiration_for_anomaly(anomaly_like)

    subtype = str(anomaly_like.get("subtype") or "").upper()
    description = str(anomaly_like.get("description") or "").upper()
    text = f"{subtype} {description}"
    confidence = _safe_float(anomaly_like.get("confidence_score"), 0.75)
    estimated = _safe_float(anomaly_like.get("estimated_recoverable"), 0.0)

    contract = contract_metadata or {}
    has_contract_enforcement = bool(contract.get("enforceable") or contract.get("backend_clause") or contract.get("rate_card"))

    if _contains_any(text, ("IDENTIFIER", "METADATA", "CATALOG", "CROSSWALK", "ISRC", "ISWC")) and estimated <= 0:
        return {
            "recoverability_class": FUTURE_PREVENTION,
            "rationale": "Issue is primarily metadata/catalog integrity with no retroactive monetary delta.",
            "legal_basis": "Operational prevention and rights administration",
            "recommended_action": "Run metadata repair, identifier normalization, and cross-system linking.",
            "confidence_score": round(max(confidence, metadata_repair_confidence or 0.8), 4),
        }

    if _contains_any(text, ("MISREPORTED", "MISATTRIBUTED", "DSP", "UNDERREPORT", "MISROUTING", "METADATA DRIFT")):
        return {
            "recoverability_class": COPYRIGHT_DAMAGES,
            "rationale": "Underpayment or misattribution discovered now supports discovery-rule damages posture.",
            "legal_basis": "Copyright damages + discovery rule",
            "recommended_action": "Draft damages-oriented claim narrative with usage logs and attribution evidence.",
            "confidence_score": round(min(0.98, max(confidence, 0.82)), 4),
        }

    if _contains_any(text, ("UNDERPAY", "RATE", "MISCALCULATION", "BACKEND", "SYNC", "REUSE")) or has_contract_enforcement:
        return {
            "recoverability_class": POTENTIALLY_CONTRACT,
            "rationale": "Dispute appears contract-governed (rate, formula, or participation obligations).",
            "legal_basis": "Contract enforcement and accounting rights",
            "recommended_action": "Draft contract-based claim with clause mapping and calculation audit exhibits.",
            "confidence_score": round(min(0.97, max(confidence, 0.8)), 4),
        }

    if bool(black_box.get("is_expired")):
        return {
            "recoverability_class": EXPIRED_REDIS,
            "rationale": "Unmatched funds appear past redistribution window based on payer/society rules.",
            "legal_basis": "Black-box redistribution policy",
            "recommended_action": "Use anomaly for metadata repair and future leakage prevention scoring.",
            "confidence_score": round(min(0.95, max(confidence, 0.78)), 4),
        }

    return {
        "recoverability_class": RECOVERABLE,
        "rationale": "Anomaly is within active claim window and not yet black-box redistributed.",
        "legal_basis": "Within payer/society claim window",
        "recommended_action": "Draft and file recovery claim with evidence packet immediately.",
        "confidence_score": round(min(0.99, max(confidence, 0.85)), 4),
    }


def build_recoverability_payload(
    anomaly_like: dict[str, Any],
    *,
    contract_metadata: dict[str, Any] | None = None,
    metadata_repair_confidence: float | None = None,
) -> dict[str, Any]:
    black_box = evaluate_black_box_expiration_for_anomaly(anomaly_like)
    classification = classify_recoverability(
        anomaly_like,
        black_box_result=black_box,
        contract_metadata=contract_metadata,
        metadata_repair_confidence=metadata_repair_confidence,
    )
    return {
        "black_box_expiration": black_box,
        "recoverability": classification,
        "legal_basis": classification.get("legal_basis"),
        "claim_draft_allowed": classification.get("recoverability_class") in _ALLOWED_FOR_CLAIMS,
    }


def claim_draft_allowed_for_class(recoverability_class: str | None) -> bool:
    return str(recoverability_class or "") in _ALLOWED_FOR_CLAIMS
