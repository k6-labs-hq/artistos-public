from __future__ import annotations

from typing import Any


def assess_catalog_integrity(works: list[dict[str, Any]], contracts: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate metadata integrity and registration drift across catalog assets."""
    missing_isrc = [w.get("id") for w in works if not w.get("isrc")]
    missing_iswc = [w.get("id") for w in works if not w.get("iswc")]

    inferred_splits = []
    collaborator_mismatches = []
    drift = []

    expected_split = 1.0
    for c in contracts:
        terms = c.get("terms") or {}
        if "artist_split" in terms:
            expected_split = float(terms.get("artist_split") or expected_split)
            break

    for w in works:
        inferred_splits.append({"work_id": w.get("id"), "inferred_artist_split": expected_split})

    for e in events:
        qty = float(e.get("quantity") or 0.0)
        val = float(e.get("unit_value") or 0.0)
        if qty > 0 and val <= 0.0:
            collaborator_mismatches.append({
                "work_id": e.get("work_id"),
                "platform": e.get("platform"),
                "issue": "non_positive_unit_value",
            })

    for w in works:
        if str(w.get("title") or "").strip().lower().endswith("(live)") and not w.get("isrc"):
            drift.append({"work_id": w.get("id"), "issue": "metadata_drift_live_version_unregistered"})

    return {
        "isrc_iswc_reconciliation": {
            "missing_isrc_count": len(missing_isrc),
            "missing_iswc_count": len(missing_iswc),
            "missing_isrc_work_ids": missing_isrc,
            "missing_iswc_work_ids": missing_iswc,
        },
        "split_sheet_inference": inferred_splits,
        "collaborator_mismatch_detection": collaborator_mismatches,
        "missing_registration_prediction": {
            "predicted_missing_registrations": len(missing_isrc) + len(missing_iswc),
            "high_risk_work_ids": list(dict.fromkeys(missing_isrc + missing_iswc))[:25],
        },
        "metadata_drift_detection": drift,
    }
