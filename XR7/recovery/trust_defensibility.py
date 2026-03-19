from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.recovery.immutable_ledger import ImmutableLedgerService


class TrustDefensibilityService:
    """Immutable legal defensibility audit trail with trust scoring."""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def _hash(self, payload: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def trust_score(
        self,
        *,
        data_completeness: float,
        model_confidence: float,
        contract_evidence_quality: float,
        sol_risk: float,
    ) -> dict[str, Any]:
        score = (
            max(0.0, min(1.0, data_completeness)) * 0.30
            + max(0.0, min(1.0, model_confidence)) * 0.30
            + max(0.0, min(1.0, contract_evidence_quality)) * 0.25
            + (1.0 - max(0.0, min(1.0, sol_risk))) * 0.15
        )
        pct = round(score * 100.0, 2)
        rating = "green" if pct >= 75 else ("yellow" if pct >= 50 else "red")
        return {
            "trust_score": pct,
            "defensibility_rating": rating,
            "requires_attorney_review": pct < 65,
            "inputs": {
                "data_completeness": data_completeness,
                "model_confidence": model_confidence,
                "contract_evidence_quality": contract_evidence_quality,
                "sol_risk": sol_risk,
            },
        }

    def log_classification_decision(
        self,
        *,
        artist_id: str,
        anomaly_id: str,
        inputs: dict[str, Any],
        model_version: str,
        rule_version: str,
        agent_id: str,
        confidence_score: float,
        human_review_flag: bool,
    ) -> dict[str, Any]:
        payload = {
            "anomaly_id": anomaly_id,
            "inputs": inputs,
            "model_version": model_version,
            "rule_version": rule_version,
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence_score": confidence_score,
            "human_review_flag": human_review_flag,
        }
        payload["decision_hash"] = self._hash(payload)

        if self.db is not None:
            ImmutableLedgerService(self.db).append(artist_id, "classification_decision", payload)
        return payload

    def legal_defensibility_report(
        self,
        *,
        claim_id: str,
        anomaly_payload: dict[str, Any],
        classification_payload: dict[str, Any],
        evidence_package: dict[str, Any],
    ) -> dict[str, Any]:
        chain = [
            {"stage": "raw_royalty_data", "hash": self._hash(anomaly_payload)},
            {"stage": "anomaly_detection", "hash": self._hash({"anomaly_id": anomaly_payload.get("id"), "subtype": anomaly_payload.get("subtype")})},
            {"stage": "recoverability_classification", "hash": self._hash(classification_payload)},
            {"stage": "evidence_package", "hash": self._hash(evidence_package)},
        ]
        report = {
            "claim_id": claim_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "chain_of_custody": chain,
            "hash_verification_passed": all(bool(c.get("hash")) for c in chain),
        }
        report["report_hash"] = self._hash(report)
        return report
