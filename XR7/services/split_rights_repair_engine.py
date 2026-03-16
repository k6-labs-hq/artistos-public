from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from XR7.recovery.split_verification import verify_splits


@dataclass
class SplitRepairResult:
    artist_id: str
    mismatch_count: int
    corrections_applied: int
    low_confidence_flags: int
    registration_packets: list[dict[str, Any]]
    corrections: list[dict[str, Any]]


class SplitRightsRepairEngine:
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold

    def analyze(
        self,
        artist_id: str,
        rights_rows: list[dict[str, Any]],
        payout_rows: list[dict[str, Any]],
        metadata_repairs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        verification = verify_splits(
            artist_id,
            rights_rows,
            payout_rows,
            metadata_repairs=metadata_repairs,
            mismatch_threshold=0.03,
        )

        unregistered = [
            {
                "work_id": str(r.get("work_id") or ""),
                "issue": "UNREGISTERED_WORK",
                "details": "No PRO registration present in rights row",
            }
            for r in rights_rows
            if not r.get("pro_registered", True)
        ]

        missing_contributors = [
            {
                "work_id": str(r.get("work_id") or ""),
                "issue": "MISSING_CONTRIBUTOR",
                "details": "Contributor list is empty or incomplete",
            }
            for r in rights_rows
            if not (r.get("contributors") or [])
        ]

        pro_publisher_mismatches = []
        conflicting_societies = []
        for r in rights_rows:
            work_id = str(r.get("work_id") or "")
            pro = str(r.get("pro") or "").strip().upper()
            pub = str(r.get("publisher") or "").strip().upper()
            societies = sorted({str(s).strip().upper() for s in (r.get("societies") or []) if str(s).strip()})
            if pro and pub and pro not in {"ASCAP", "BMI", "SESAC", "PRS", "GEMA", "SACEM", "SOCAN", "APRA", "JASRAC"}:
                pro_publisher_mismatches.append(
                    {
                        "work_id": work_id,
                        "issue": "PRO_PUBLISHER_MISMATCH",
                        "details": f"Unrecognized PRO '{pro}' for publisher '{pub}'",
                    }
                )
            if len(societies) > 1:
                conflicting_societies.append(
                    {
                        "work_id": work_id,
                        "issue": "CONFLICTING_SOCIETY_REGISTRATIONS",
                        "details": f"Multiple societies declared: {', '.join(societies)}",
                    }
                )

        verification["rights_integrity_findings"] = {
            "missing_contributors": missing_contributors,
            "pro_publisher_mismatches": pro_publisher_mismatches,
            "unregistered_works": unregistered,
            "conflicting_societies": conflicting_societies,
        }
        return verification

    def apply_high_confidence_repairs(
        self,
        artist_id: str,
        rights_rows: list[dict[str, Any]],
        payout_rows: list[dict[str, Any]],
        metadata_repairs: list[dict[str, Any]] | None = None,
    ) -> SplitRepairResult:
        analysis = self.analyze(artist_id, rights_rows, payout_rows, metadata_repairs=metadata_repairs)
        mismatches = list(analysis.get("mismatches") or [])

        corrections: list[dict[str, Any]] = []
        registration_packets: list[dict[str, Any]] = []
        low_confidence_flags = 0

        for row in mismatches:
            expected = float(row.get("expected_split") or 0.0)
            actual = float(row.get("actual_split") or 0.0)
            delta = abs(expected - actual)
            confidence = max(0.0, min(1.0, 1.0 - delta))
            proposed = expected
            correction = {
                "work_id": row.get("work_id"),
                "territory": row.get("territory"),
                "platform": row.get("platform"),
                "before_split": actual,
                "after_split": proposed,
                "confidence": round(confidence, 4),
                "rationale": "Expected split from rights registry exceeds paid split.",
            }
            corrections.append(correction)
            if confidence < self.confidence_threshold:
                low_confidence_flags += 1
                continue
            registration_packets.append(
                {
                    "work_id": row.get("work_id"),
                    "packet_type": "SPLIT_CORRECTION_REGISTRATION",
                    "proposed_split": proposed,
                    "territory": row.get("territory"),
                    "platform": row.get("platform"),
                    "contributors": [],
                    "status": "READY_TO_FILE",
                }
            )

        return SplitRepairResult(
            artist_id=artist_id,
            mismatch_count=len(mismatches),
            corrections_applied=len(registration_packets),
            low_confidence_flags=low_confidence_flags,
            registration_packets=registration_packets,
            corrections=corrections,
        )
