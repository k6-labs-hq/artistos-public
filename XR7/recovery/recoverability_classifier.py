from __future__ import annotations

from typing import Any

from shared.utils.numbers import safe_float as _safe_float
from XR7.recovery.black_box_expiration import evaluate_black_box_expiration_for_anomaly

RECOVERABLE = "Recoverable"
POTENTIALLY_CONTRACT = "Potentially Recoverable (Contract-Based)"
EXPIRED_REDIS = "Expired (Black-Box Redistributed)"
COPYRIGHT_DAMAGES = "Recoverable via Copyright Damages"
FUTURE_PREVENTION = "Future Leakage Prevention Only"


_ALLOWED_FOR_CLAIMS = {RECOVERABLE, POTENTIALLY_CONTRACT, COPYRIGHT_DAMAGES}


_JURISDICTION_RULES: dict[str, dict[str, Any]] = {
    "US": {"audit_window_years": 3, "copyright_discovery_rule": True},
    "UK": {"audit_window_years": 6, "copyright_discovery_rule": True},
    "EU": {"audit_window_years": 5, "copyright_discovery_rule": True},
    "APAC": {"audit_window_years": 4, "copyright_discovery_rule": True},
}


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(t in text for t in terms)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class ContractRecoverabilityScorer:
    """Clause-aware contract recoverability scoring with jurisdiction and litigation adjustments."""

    _BASE_RANGES: dict[str, tuple[float, float]] = {
        "audit_rights": (0.90, 0.95),
        "mfn": (0.75, 0.90),
        "backend_participation": (0.50, 0.75),
        "reversion": (0.60, 0.85),
        "expired_audit_no_copyright": (0.05, 0.20),
    }

    def _resolve_clause(self, contract_data: dict[str, Any]) -> str:
        text = str(contract_data.get("governing_clause") or contract_data.get("clause_type") or "").lower()
        if "audit" in text:
            return "audit_rights"
        if "mfn" in text or "most-favored" in text or "most favored" in text:
            return "mfn"
        if "backend" in text or "participation" in text:
            return "backend_participation"
        if "reversion" in text:
            return "reversion"
        if bool(contract_data.get("audit_rights_expired")):
            return "expired_audit_no_copyright"
        return "backend_participation"

    def score(
        self,
        *,
        anomaly_like: dict[str, Any],
        contract_data: dict[str, Any] | None,
        jurisdiction: str | None,
        litigation_flags: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        contract = contract_data or {}
        clause = self._resolve_clause(contract)
        base_low, base_high = self._BASE_RANGES.get(clause, (0.40, 0.70))
        score = (base_low + base_high) / 2.0

        comparator_required = clause == "mfn"
        comparator_present = bool(contract.get("comparator_present") or contract.get("mfn_comparator"))
        if comparator_required and not comparator_present:
            score -= 0.12

        if clause == "reversion" and not bool(contract.get("notice_delivery_proof")):
            score -= 0.10

        if clause == "audit_rights" and bool(contract.get("audit_rights_expired")):
            clause = "expired_audit_no_copyright"
            base_low, base_high = self._BASE_RANGES[clause]
            score = (base_low + base_high) / 2.0

        litigation = litigation_flags or {}
        adversarial = float(litigation.get("counterparty_dispute_intensity") or 0.0)
        cooperative = float(litigation.get("counterparty_settlement_rate") or 0.0)
        score -= min(0.15, adversarial * 0.15)
        score += min(0.08, cooperative * 0.08)

        region = str(jurisdiction or contract.get("jurisdiction") or "US").upper()
        if region not in _JURISDICTION_RULES:
            region = "US"
        rules = _JURISDICTION_RULES[region]

        audit_window_years = int(contract.get("audit_window_years") or rules["audit_window_years"])
        event_year = int(str(anomaly_like.get("event_date") or anomaly_like.get("time_window_end") or "")[:4] or 0)
        current_year = int(str(anomaly_like.get("as_of_year") or 2026))
        within_window = bool(event_year and current_year - event_year <= audit_window_years)
        audit_window_status = "within_window" if within_window else "outside_window"

        if not within_window and clause == "audit_rights":
            score -= 0.25

        recommended = "File audit demand with clause-cited exhibits"
        if clause == "mfn":
            recommended = "Obtain comparator deal terms then assert MFN variance claim"
        elif clause == "backend_participation":
            recommended = "Request backend participation accounting and waterfall disclosures"
        elif clause == "reversion":
            recommended = "Serve reversion notice and preserve delivery proof"
        elif clause == "expired_audit_no_copyright":
            recommended = "Pursue only if copyright-discovery pathway exists"

        final_score = _clamp(score)
        return {
            "contract_recoverability_score": round(final_score, 6),
            "governing_clause": clause,
            "jurisdiction": region,
            "audit_window_status": audit_window_status,
            "comparator_required": comparator_required,
            "recommended_legal_strategy": recommended,
            "score_range": {"low": base_low, "high": base_high},
        }


def recoverability_explainer_line(
    *,
    classification: dict[str, Any],
    contract_score: dict[str, Any] | None = None,
) -> str:
    c = classification.get("recoverability_class") or "Unclassified"
    legal = classification.get("legal_basis") or "Legal basis unavailable"
    if contract_score:
        clause = contract_score.get("governing_clause") or "contract clause"
        strategy = contract_score.get("recommended_legal_strategy") or "review contract"
        return f"{c}: {legal}. Governing clause: {clause}. Recommended strategy: {strategy}."
    return f"{c}: {legal}."


def classify_recoverability(
    anomaly_like: dict[str, Any],
    *,
    black_box_result: dict[str, Any] | None = None,
    contract_metadata: dict[str, Any] | None = None,
    metadata_repair_confidence: float | None = None,
    jurisdiction: str | None = None,
    litigation_flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    black_box = black_box_result or evaluate_black_box_expiration_for_anomaly(anomaly_like)

    subtype = str(anomaly_like.get("subtype") or "").upper()
    description = str(anomaly_like.get("description") or "").upper()
    text = f"{subtype} {description}"
    confidence = _safe_float(anomaly_like.get("confidence_score"), 0.75)
    estimated = _safe_float(anomaly_like.get("estimated_recoverable"), 0.0)

    contract = contract_metadata or {}
    has_contract_enforcement = bool(contract.get("enforceable") or contract.get("backend_clause") or contract.get("rate_card"))
    contract_score_payload = ContractRecoverabilityScorer().score(
        anomaly_like=anomaly_like,
        contract_data=contract,
        jurisdiction=jurisdiction,
        litigation_flags=litigation_flags,
    ) if contract else None

    if _contains_any(text, ("IDENTIFIER", "METADATA", "CATALOG", "CROSSWALK", "ISRC", "ISWC")) and estimated <= 0:
        return {
            "recoverability_class": FUTURE_PREVENTION,
            "rationale": "Issue is primarily metadata/catalog integrity with no retroactive monetary delta.",
            "legal_basis": "Operational prevention and rights administration",
            "recommended_action": "Run metadata repair, identifier normalization, and cross-system linking.",
            "confidence_score": round(max(confidence, metadata_repair_confidence or 0.8), 4),
            "contract_recoverability": contract_score_payload,
        }

    if _contains_any(text, ("MISREPORTED", "MISATTRIBUTED", "DSP", "UNDERREPORT", "MISROUTING", "METADATA DRIFT")):
        return {
            "recoverability_class": COPYRIGHT_DAMAGES,
            "rationale": "Underpayment or misattribution discovered now supports discovery-rule damages posture.",
            "legal_basis": "Copyright damages + discovery rule",
            "recommended_action": "Draft damages-oriented claim narrative with usage logs and attribution evidence.",
            "confidence_score": round(min(0.98, max(confidence, 0.82)), 4),
            "contract_recoverability": contract_score_payload,
        }

    if _contains_any(text, ("UNDERPAY", "RATE", "MISCALCULATION", "BACKEND", "SYNC", "REUSE")) or has_contract_enforcement:
        return {
            "recoverability_class": POTENTIALLY_CONTRACT,
            "rationale": "Dispute appears contract-governed (rate, formula, or participation obligations).",
            "legal_basis": "Contract enforcement and accounting rights",
            "recommended_action": "Draft contract-based claim with clause mapping and calculation audit exhibits.",
            "confidence_score": round(min(0.97, max(confidence, 0.8, _safe_float((contract_score_payload or {}).get("contract_recoverability_score"), 0.0))), 4),
            "contract_recoverability": contract_score_payload,
        }

    if bool(black_box.get("is_expired")):
        return {
            "recoverability_class": EXPIRED_REDIS,
            "rationale": "Unmatched funds appear past redistribution window based on payer/society rules.",
            "legal_basis": "Black-box redistribution policy",
            "recommended_action": "Use anomaly for metadata repair and future leakage prevention scoring.",
            "confidence_score": round(min(0.95, max(confidence, 0.78)), 4),
            "contract_recoverability": contract_score_payload,
        }

    return {
        "recoverability_class": RECOVERABLE,
        "rationale": "Anomaly is within active claim window and not yet black-box redistributed.",
        "legal_basis": "Within payer/society claim window",
        "recommended_action": "Draft and file recovery claim with evidence packet immediately.",
        "confidence_score": round(min(0.99, max(confidence, 0.85)), 4),
        "contract_recoverability": contract_score_payload,
    }


def build_recoverability_payload(
    anomaly_like: dict[str, Any],
    *,
    contract_metadata: dict[str, Any] | None = None,
    metadata_repair_confidence: float | None = None,
    jurisdiction: str | None = None,
    litigation_flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    black_box = evaluate_black_box_expiration_for_anomaly(anomaly_like)
    classification = classify_recoverability(
        anomaly_like,
        black_box_result=black_box,
        contract_metadata=contract_metadata,
        metadata_repair_confidence=metadata_repair_confidence,
        jurisdiction=jurisdiction,
        litigation_flags=litigation_flags,
    )
    contract_recoverability = classification.get("contract_recoverability")
    return {
        "black_box_expiration": black_box,
        "recoverability": classification,
        "legal_basis": classification.get("legal_basis"),
        "contract_recoverability": contract_recoverability,
        "recoverability_explainer_line": recoverability_explainer_line(
            classification=classification,
            contract_score=contract_recoverability,
        ),
        "claim_draft_allowed": classification.get("recoverability_class") in _ALLOWED_FOR_CLAIMS,
    }


def claim_draft_allowed_for_class(recoverability_class: str | None) -> bool:
    return str(recoverability_class or "") in _ALLOWED_FOR_CLAIMS
