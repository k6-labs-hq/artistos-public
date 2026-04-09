"""Pillar 5 — Rights scan and auto-registration service.

Detects missing ISRC/ISWC/UPC/PRO/foreign registrations per work and
generates submission packets for PRS, GEMA, SACEM, ASCAP, BMI etc.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.rights_scan import RightsScanResult
from XR7.models.work import Work
from xr7_common.logging import get_logger

logger = get_logger(__name__)

_FOREIGN_SOCIETIES = ["PRS", "GEMA", "SACEM", "SOCAN", "APRA", "JASRAC", "BUMA"]

_REQUIRED_IDENTIFIERS = {
    "isrc": "International Standard Recording Code — required for digital distribution royalties.",
    "iswc": "International Standard Musical Work Code — required for publishing/PRO royalties.",
    "upc": "Universal Product Code — required for physical/bundle royalties.",
    "pro_registration": "PRO (ASCAP/BMI/SESAC) registration — required for performance royalties.",
}


def scan_rights_gaps(db: Session, artist_id: str) -> list[dict[str, Any]]:
    """Scan all works for this artist and detect registration gaps."""
    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    gaps: list[dict[str, Any]] = []

    for work in works:
        work_meta: dict[str, Any] = {}
        try:
            work_meta = dict(work.metadata_json or {})
        except Exception:  # noqa: BLE001
            pass

        for identifier, description in _REQUIRED_IDENTIFIERS.items():
            if not work_meta.get(identifier):
                gaps.append(
                    {
                        "work_id": work.id,
                        "work_title": getattr(work, "title", None),
                        "gap_type": f"missing_{identifier}",
                        "description": description,
                        "territory": "global",
                    }
                )

        # Foreign society registrations
        registered_societies: list[str] = list(work_meta.get("registered_societies") or [])
        for society in _FOREIGN_SOCIETIES:
            if society not in registered_societies:
                gaps.append(
                    {
                        "work_id": work.id,
                        "work_title": getattr(work, "title", None),
                        "gap_type": "unregistered_foreign",
                        "description": f"Not registered with {society}.",
                        "territory": society,
                    }
                )

    return gaps


def persist_and_generate_packets(
    db: Session,
    artist_id: str,
    gaps: list[dict[str, Any]],
) -> list[RightsScanResult]:
    """Persist gaps and generate registration packets for each."""
    results: list[RightsScanResult] = []
    for gap in gaps:
        packet = _build_registration_packet(artist_id=artist_id, gap=gap)
        row = RightsScanResult(
            artist_id=artist_id,
            work_id=gap.get("work_id"),
            gap_type=gap["gap_type"],
            territory=gap.get("territory"),
            registration_packet=packet,
            notes=gap.get("description"),
        )
        db.add(row)
        results.append(row)
    if results:
        db.commit()
    return results


def _build_registration_packet(artist_id: str, gap: dict[str, Any]) -> dict[str, Any]:
    """Build an auto-generated registration submission packet."""
    return {
        "artist_id": artist_id,
        "work_id": gap.get("work_id"),
        "work_title": gap.get("work_title"),
        "gap_type": gap["gap_type"],
        "territory": gap.get("territory"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "submission_instructions": _submission_instructions(gap["gap_type"], gap.get("territory")),
        "status": "pending_review",
    }


def _submission_instructions(gap_type: str, territory: str | None) -> str:
    if gap_type == "missing_isrc":
        return "Apply for ISRC via your distributor (DistroKid / CD Baby / TuneCore) or IFPI."
    if gap_type == "missing_iswc":
        return "Register with your PRO (ASCAP/BMI/SESAC/PRS) to obtain ISWC."
    if gap_type == "missing_upc":
        return "Request UPC from your distributor or GS1 directly."
    if gap_type == "missing_pro_registration":
        return "Register this work with your PRO membership portal immediately."
    if gap_type == "unregistered_foreign" and territory:
        return (
            f"Submit affiliation/work registration claim to {territory}. "
            "XR7 can generate a pre-filled packet. Confirm to proceed."
        )
    return "Manual review required."
