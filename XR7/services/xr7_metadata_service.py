from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.xr7_royalty import XR7AIDecisionAuditLog, XR7Track, XR7UnmatchedWork


def _now() -> datetime:
    return datetime.now(timezone.utc)


def suggest_metadata_repairs(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    scope: str = "catalog",
    max_items: int = 50,
) -> dict[str, object]:
    suggestions: list[dict[str, object]] = []

    if scope in {"catalog", "all"}:
        tracks = (
            db.query(XR7Track)
            .filter(XR7Track.tenant_id == tenant_id, XR7Track.artist_id == artist_id)
            .limit(max_items)
            .all()
        )
        for track in tracks:
            proposal: dict[str, object] | None = None
            if track.title != track.title.strip():
                proposal = {
                    "entity": "recording",
                    "entity_id": track.id,
                    "field": "title",
                    "current_value": track.title,
                    "proposed_value": track.title.strip(),
                    "confidence": 0.92,
                    "reason": "trim_whitespace",
                }
            elif track.metadata_quality_score < 0.6:
                proposal = {
                    "entity": "recording",
                    "entity_id": track.id,
                    "field": "metadata_quality_score",
                    "current_value": track.metadata_quality_score,
                    "proposed_value": min(1.0, track.metadata_quality_score + 0.2),
                    "confidence": 0.8,
                    "reason": "quality_boost_from_complete_fields",
                }
            if proposal:
                suggestions.append(proposal)

    if scope in {"unmatched", "all"} and len(suggestions) < max_items:
        unmatched = (
            db.query(XR7UnmatchedWork)
            .filter(
                XR7UnmatchedWork.tenant_id == tenant_id,
                XR7UnmatchedWork.artist_id == artist_id,
                XR7UnmatchedWork.status == "open",
            )
            .limit(max_items - len(suggestions))
            .all()
        )
        for row in unmatched:
            suggestions.append(
                {
                    "entity": "unmatched_work",
                    "entity_id": row.id,
                    "field": "status",
                    "current_value": row.status,
                    "proposed_value": "manual_review",
                    "confidence": 0.74,
                    "reason": "open_item_needs_resolution_path",
                }
            )

    quality_before = 0.0
    quality_after = 0.0
    tracks_all = (
        db.query(XR7Track)
        .filter(XR7Track.tenant_id == tenant_id, XR7Track.artist_id == artist_id)
        .all()
    )
    if tracks_all:
        quality_before = sum(t.metadata_quality_score for t in tracks_all) / len(tracks_all)
        quality_after = min(1.0, quality_before + min(0.25, 0.02 * len(suggestions)))

    return {
        "suggestions": suggestions[:max_items],
        "quality_score_before": round(quality_before, 4),
        "projected_quality_score_after": round(quality_after, 4),
    }


def apply_metadata_repairs(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    suggestion_ids: list[str],
    dry_run: bool,
) -> dict[str, object]:
    applied_count = 0
    skipped_count = 0
    audit_refs: list[str] = []

    for suggestion_id in suggestion_ids:
        parts = suggestion_id.split(":")
        if len(parts) != 2:
            skipped_count += 1
            continue
        entity, entity_id = parts
        if entity not in ("recording", "track"):
            skipped_count += 1
            continue

        track = (
            db.query(XR7Track)
            .filter(
                XR7Track.id == entity_id,
                XR7Track.tenant_id == tenant_id,
                XR7Track.artist_id == artist_id,
            )
            .first()
        )
        if not track:
            skipped_count += 1
            continue

        if not dry_run:
            track.title = track.title.strip()
            track.ai_repair_status = "applied"
            track.metadata_quality_score = min(1.0, float(track.metadata_quality_score) + 0.1)
            track.updated_at = _now()

        prompt_hash = hashlib.sha256(f"apply:{suggestion_id}:{dry_run}".encode("utf-8")).hexdigest()
        audit = XR7AIDecisionAuditLog(
            tenant_id=tenant_id,
            artist_id=artist_id,
            decision_type="metadata_repair_apply",
            model_provider="xr7_rule_engine",
            model_version="v1",
            prompt_hash=prompt_hash,
            input_ref=suggestion_id,
            output_ref=json.dumps({"dry_run": dry_run}, sort_keys=True),
            reviewer_id=None,
            override_flag=False,
        )
        db.add(audit)
        db.flush()
        audit_refs.append(audit.id)
        applied_count += 1

    db.commit()
    return {
        "applied_count": applied_count,
        "skipped_count": skipped_count,
        "audit_refs": audit_refs,
    }
