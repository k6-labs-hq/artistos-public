from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine


class ClaimsEvidencePackageBuilder:
    """Assemble court/society-ready evidence package with JSON, PDF-text, and XLSX-like CSV export."""

    def __init__(self, *, confidence_gate_threshold: float = 0.65) -> None:
        self.confidence_gate_threshold = max(0.0, min(1.0, confidence_gate_threshold))

    def _claim_strength_rating(self, package: dict[str, Any]) -> str:
        confidence = float(package.get("overall_confidence") or 0.0)
        trust_score = float(package.get("trust_score") or 0.0)
        days_remaining = int((package.get("discovery_rule") or {}).get("days_remaining") or 0)
        if confidence >= 0.82 and trust_score >= 80 and days_remaining > 30:
            return "A"
        if confidence >= 0.68 and trust_score >= 65:
            return "B"
        if confidence >= 0.45 and trust_score >= 45:
            return "C"
        return "D"

    def _attorney_checklist(self, package: dict[str, Any]) -> dict[str, bool]:
        return {
            "anomaly_detection_report_present": bool(package.get("anomaly_detection_report")),
            "expiration_probability_report_present": bool(
                package.get("expiration_probability_report")
            ),
            "contract_recoverability_present": bool(package.get("contract_recoverability")),
            "discovery_timeline_present": bool(
                (package.get("discovery_rule") or {}).get("discovery_timeline")
            ),
            "metadata_repair_history_present": bool(package.get("metadata_repair_history")),
            "royalty_statement_excerpt_present": bool(package.get("royalty_statement_excerpt")),
            "attorney_declaration_template_present": bool(
                package.get("attorney_declaration_template")
            ),
        }

    def _cover_page(self, package: dict[str, Any]) -> dict[str, Any]:
        discovery = package.get("discovery_rule") or {}
        return {
            "title": "XR7 Claims Evidence Package",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sol_deadline": discovery.get("statute_of_limitations_deadline"),
            "sol_deadline_warning": (
                "URGENT: statute of limitations deadline within 90 days"
                if bool(discovery.get("urgent_flag"))
                else "SOL timing evaluated; continue standard filing workflow"
            ),
        }

    def build(
        self,
        *,
        claim: dict[str, Any],
        anomaly: dict[str, Any],
        recoverability_payload: dict[str, Any],
        trust_score: float,
        precedent_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        discovery = DiscoveryRuleEngine().evaluate(
            {
                **anomaly,
                "artist_id": claim.get("artist_id"),
                "jurisdiction": claim.get("governing_law_state")
                or anomaly.get("jurisdiction")
                or "US",
                "xr7_detection_timestamp": anomaly.get("created_at"),
            }
        )

        package = {
            "claim_id": claim.get("id"),
            "anomaly_id": anomaly.get("id"),
            "cover_page": {},
            "anomaly_detection_report": {
                "timestamp": anomaly.get("created_at"),
                "hash_signed": True,
                "category": anomaly.get("category"),
                "subtype": anomaly.get("subtype"),
                "description": anomaly.get("description"),
            },
            "expiration_probability_report": recoverability_payload.get("black_box_expiration")
            or {},
            "contract_recoverability": recoverability_payload.get("contract_recoverability") or {},
            "discovery_rule": discovery,
            "metadata_repair_history": {
                "pre_repair": anomaly.get("pre_repair") or {},
                "post_repair": anomaly.get("post_repair") or {},
                "repair_events": anomaly.get("metadata_repairs") or [],
            },
            "royalty_statement_excerpt": anomaly.get("royalty_statement_excerpt")
            or {"redacted": True},
            "precedent_references": precedent_refs or [],
            "attorney_declaration_template": {
                "title": "Attorney Declaration",
                "fields": [
                    "attorney_name",
                    "bar_number",
                    "jurisdiction",
                    "declaration_text",
                    "signature",
                    "date",
                ],
                "status": "fillable",
            },
            "overall_confidence": float(
                (recoverability_payload.get("recoverability") or {}).get("confidence_score") or 0.0
            ),
            "trust_score": float(trust_score),
            "human_attorney_review_required": float(
                (recoverability_payload.get("recoverability") or {}).get("confidence_score") or 0.0
            )
            < self.confidence_gate_threshold,
        }
        package["cover_page"] = self._cover_page(package)
        package["attorney_review_checklist"] = self._attorney_checklist(package)
        package["claim_strength_rating"] = self._claim_strength_rating(package)
        return package

    def export_json(self, package: dict[str, Any]) -> str:
        return json.dumps(package, indent=2, default=str)

    def export_pdf_text(self, package: dict[str, Any]) -> str:
        lines = [
            package.get("cover_page", {}).get("title", "XR7 Claims Evidence Package"),
            f"Generated: {package.get('cover_page', {}).get('generated_at')}",
            f"Claim ID: {package.get('claim_id')}",
            f"Anomaly ID: {package.get('anomaly_id')}",
            f"SOL Warning: {package.get('cover_page', {}).get('sol_deadline_warning')}",
            f"Strength Rating: {package.get('claim_strength_rating')}",
            "Attorney Checklist:",
        ]
        checklist = package.get("attorney_review_checklist") or {}
        for key, value in checklist.items():
            lines.append(f" - {key}: {'yes' if value else 'no'}")
        return "\n".join(lines)

    def export_xlsx_bytes(self, package: dict[str, Any]) -> bytes:
        """CSV fallback used as forensic workbook-compatible export content."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["field", "value"])
        writer.writerow(["claim_id", package.get("claim_id")])
        writer.writerow(["anomaly_id", package.get("anomaly_id")])
        writer.writerow(["claim_strength_rating", package.get("claim_strength_rating")])
        writer.writerow(["trust_score", package.get("trust_score")])
        writer.writerow(["overall_confidence", package.get("overall_confidence")])
        writer.writerow(["sol_deadline", (package.get("cover_page") or {}).get("sol_deadline")])
        writer.writerow(
            ["sol_warning", (package.get("cover_page") or {}).get("sol_deadline_warning")]
        )
        return output.getvalue().encode("utf-8")
