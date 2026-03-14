from __future__ import annotations

from typing import Any


REQUIRED_PLATFORM_SET = {"spotify", "apple music", "youtube", "tiktok"}
REQUIRED_USAGE_SOURCES = {"distributor", "pro", "mlc", "platform"}


def detect_missing_data(
    *,
    connected_sources: list[str],
    catalog_rows: list[dict[str, Any]],
    registration_rows: list[dict[str, Any]],
    usage_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    lower_connected = {s.strip().lower() for s in connected_sources}
    missing_platforms = sorted(REQUIRED_PLATFORM_SET - lower_connected)

    registration_ids = [r.get("registration_id") for r in registration_rows]
    missing_pro_registrations = len([r for r in registration_ids if not r or r == "pending"])

    usage_sources = {str(u.get("source", "")).strip().lower() for u in usage_rows if u.get("source")}
    missing_usage_sources = sorted(REQUIRED_USAGE_SOURCES - usage_sources)

    missing_metadata_fields: dict[str, int] = {"isrc": 0, "work_title": 0, "publisher": 0}
    for row in catalog_rows:
        if not row.get("isrc"):
            missing_metadata_fields["isrc"] += 1
        if not row.get("work_title"):
            missing_metadata_fields["work_title"] += 1
        if not row.get("publisher"):
            missing_metadata_fields["publisher"] += 1

    prompts: list[str] = []
    if missing_platforms:
        prompts.append("Connect missing platforms for complete visibility")
    if missing_pro_registrations > 0:
        prompts.append("Add missing PRO registrations")
    if missing_usage_sources:
        prompts.append("Upload or connect missing usage data sources")
    if any(v > 0 for v in missing_metadata_fields.values()):
        prompts.append("Confirm missing catalog metadata fields")

    return {
        "missing_platforms": missing_platforms,
        "missing_pro_registrations": missing_pro_registrations,
        "missing_usage_sources": missing_usage_sources,
        "missing_metadata": missing_metadata_fields,
        "prompt_user": bool(prompts),
        "prompts": prompts,
    }
