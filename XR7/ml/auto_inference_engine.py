from __future__ import annotations

from typing import Any


def infer_catalog_relationships(catalog_rows: list[dict[str, Any]]) -> dict[str, Any]:
    inferred = []
    for row in catalog_rows:
        work_id = row.get("work_id") or row.get("id")
        streams = float(row.get("streams") or 0.0)
        contributors = row.get("contributors") or []
        likely_split = round(1.0 / max(1, len(contributors)), 4)
        likely_owner = row.get("owner") or (contributors[0] if contributors else "artist")
        likely_publisher = row.get("publisher") or "unknown_publisher"
        likely_admin = row.get("admin") or "self_administered"

        hints = []
        if not row.get("registration_id") and streams > 0:
            hints.append("missing_registration_likely")

        inferred.append(
            {
                "work_id": work_id,
                "likely_split": likely_split,
                "likely_owner": likely_owner,
                "likely_publisher": likely_publisher,
                "likely_admin": likely_admin,
                "hints": hints,
            }
        )

    return {"count": len(inferred), "inferences": inferred}
