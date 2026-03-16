from __future__ import annotations

from typing import Any

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus


def verify_splits(
    artist_id: str,
    rights_rows: list[dict[str, Any]],
    payout_rows: list[dict[str, Any]],
    metadata_repairs: list[dict[str, Any]] | None = None,
    mismatch_threshold: float = 0.1,
) -> dict[str, Any]:
    """Compare expected rights splits against observed payout distribution."""
    repair_map: dict[str, str] = {}
    for row in metadata_repairs or []:
        if str(row.get("issue_type") or "") != "DUPLICATE_WORK_REGISTRATION":
            continue
        before = row.get("before") or {}
        after = row.get("after") or {}
        canonical = str(after.get("canonical") or "")
        for dup in before.get("duplicates") or []:
            if canonical and dup:
                repair_map[str(dup)] = canonical

    def _canonical_work_id(raw: Any) -> str:
        key = str(raw or "")
        return repair_map.get(key, key)

    payout_index = {
        (_canonical_work_id(r.get("work_id")), str(r.get("territory") or "GLOBAL"), str(r.get("platform") or "ALL")): float(r.get("actual_split") or 0.0)
        for r in payout_rows
    }

    mismatches: list[dict[str, Any]] = []
    missing_contributors: list[dict[str, Any]] = []
    incorrect_percentages: list[dict[str, Any]] = []
    pro_publisher_mismatches: list[dict[str, Any]] = []
    unregistered_works: list[dict[str, Any]] = []
    conflicting_registrations: list[dict[str, Any]] = []
    for row in rights_rows:
        key = (_canonical_work_id(row.get("work_id")), str(row.get("territory") or "GLOBAL"), str(row.get("platform") or "ALL"))
        expected = float(row.get("expected_split") or 0.0)
        actual = float(payout_index.get(key, expected))
        delta = abs(expected - actual)
        contributors = list(row.get("contributors") or [])
        if not contributors:
            missing_contributors.append(
                {
                    "work_id": key[0],
                    "issue": "MISSING_CONTRIBUTORS",
                }
            )
        if expected > 1.0 or expected < 0.0:
            incorrect_percentages.append(
                {
                    "work_id": key[0],
                    "issue": "INCORRECT_PERCENTAGES",
                    "expected_split": expected,
                }
            )
        if not bool(row.get("pro_registered", True)):
            unregistered_works.append(
                {
                    "work_id": key[0],
                    "issue": "UNREGISTERED_WORK",
                }
            )
        pro = str(row.get("pro") or "").upper().strip()
        publisher = str(row.get("publisher") or "").upper().strip()
        if pro and publisher and pro not in {"ASCAP", "BMI", "SESAC", "PRS", "GEMA", "SACEM", "SOCAN", "APRA", "JASRAC"}:
            pro_publisher_mismatches.append(
                {
                    "work_id": key[0],
                    "issue": "PRO_PUBLISHER_MISMATCH",
                    "pro": pro,
                    "publisher": publisher,
                }
            )
        societies = sorted({str(s).upper().strip() for s in (row.get("societies") or []) if str(s).strip()})
        if len(societies) > 1:
            conflicting_registrations.append(
                {
                    "work_id": key[0],
                    "issue": "CONFLICTING_REGISTRATIONS_ACROSS_SOCIETIES",
                    "societies": societies,
                }
            )
        if delta >= mismatch_threshold:
            estimated_value = float(row.get("estimated_value") or 0.0)
            mismatches.append(
                {
                    "work_id": key[0],
                    "territory": key[1],
                    "platform": key[2],
                    "expected_split": expected,
                    "actual_split": actual,
                    "split_delta": round(delta, 6),
                    "estimated_recoverable": round(estimated_value * delta, 2),
                }
            )

    total_recoverable = sum(float(m.get("estimated_recoverable") or 0.0) for m in mismatches)
    return {
        "artist_id": artist_id,
        "mismatch_count": len(mismatches),
        "estimated_total_recoverable": round(total_recoverable, 2),
        "metadata_repair_links_applied": len(repair_map),
        "mismatches": mismatches,
        "missing_contributors": missing_contributors,
        "incorrect_percentages": incorrect_percentages,
        "pro_publisher_mismatches": pro_publisher_mismatches,
        "unregistered_works": unregistered_works,
        "conflicting_registrations_across_societies": conflicting_registrations,
    }


def upsert_split_conflict_anomalies(artist_id: str, verification: dict[str, Any], existing_anomalies: list[Anomaly]) -> list[Anomaly]:
    """Create split-conflict anomaly rows for unresolved mismatches."""
    existing_keys = {
        (str(a.subtype), str(a.description or ""))
        for a in existing_anomalies
        if str(a.subtype).lower() == "split_conflict"
    }

    created: list[Anomaly] = []
    for mismatch in verification.get("mismatches", []):
        description = (
            f"Split mismatch for work {mismatch.get('work_id')} "
            f"({mismatch.get('territory')}/{mismatch.get('platform')}): "
            f"expected {mismatch.get('expected_split')}, actual {mismatch.get('actual_split')}"
        )
        key = ("split_conflict", description)
        if key in existing_keys:
            continue
        created.append(
            Anomaly(
                artist_id=artist_id,
                category=AnomalyCategory.ROYALTY,
                subtype="split_conflict",
                severity=AnomalySeverity.HIGH,
                estimated_recoverable=float(mismatch.get("estimated_recoverable") or 0.0),
                confidence_score=0.85,
                status=AnomalyStatus.OPEN,
                description=description,
                territory=mismatch.get("territory"),
            )
        )
    return created
