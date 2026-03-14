from __future__ import annotations

from typing import Any

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus


def verify_splits(
    artist_id: str,
    rights_rows: list[dict[str, Any]],
    payout_rows: list[dict[str, Any]],
    mismatch_threshold: float = 0.1,
) -> dict[str, Any]:
    """Compare expected rights splits against observed payout distribution."""
    payout_index = {
        (str(r.get("work_id")), str(r.get("territory") or "GLOBAL"), str(r.get("platform") or "ALL")): float(r.get("actual_split") or 0.0)
        for r in payout_rows
    }

    mismatches: list[dict[str, Any]] = []
    for row in rights_rows:
        key = (str(row.get("work_id")), str(row.get("territory") or "GLOBAL"), str(row.get("platform") or "ALL"))
        expected = float(row.get("expected_split") or 0.0)
        actual = float(payout_index.get(key, expected))
        delta = abs(expected - actual)
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
        "mismatches": mismatches,
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
