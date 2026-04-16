from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_admin, require_artist_access
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.work import Work
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["governance"])


def _log_admin_action(
    db: Session,
    *,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: dict | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


@router.post("/artists/{artist_id}/privacy/export")
def export_artist_data(
    artist_id: str,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(require_artist_access),
) -> dict:
    artist = get_artist_or_404(artist_id, db)

    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

    _log_admin_action(
        db,
        actor=str(auth_payload.get("sub") or "artist"),
        action="privacy_export_requested",
        resource_type="artist",
        resource_id=artist_id,
        details={"work_count": len(works), "claim_count": len(claims)},
    )

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "export": {
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "artist": {
                    "id": artist.id,
                    "name": artist.name,
                    "email": artist.email,
                    "status": artist.status,
                    "created_at": artist.created_at.isoformat() if artist.created_at else None,
                },
                "works": [
                    {
                        "id": w.id,
                        "title": w.title,
                        "isrc": w.isrc,
                        "iswc": w.iswc,
                        "work_type": str(w.work_type),
                    }
                    for w in works
                ],
                "claims": [
                    {
                        "id": c.id,
                        "status": str(c.status),
                        "claim_type": c.claim_type,
                        "recovered_amount": c.recovered_amount,
                        "currency": c.currency,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in claims
                ],
            },
        },
    )


@router.post("/artists/{artist_id}/privacy/erase")
def erase_artist_data(
    artist_id: str,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(require_artist_access),
) -> dict:
    artist = get_artist_or_404(artist_id, db)

    artist.name = f"ERASED-{artist.id[:8]}"
    artist.email = None
    db.add(
        AdminAuditLog(
            actor=str(auth_payload.get("sub") or "artist"),
            action="privacy_erasure_applied",
            resource_type="artist",
            resource_id=artist_id,
            details={"mode": "anonymize_identity_fields"},
        )
    )
    db.commit()

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "status": "anonymized",
            "message": "Artist profile identity fields have been anonymized.",
        },
    )


@router.get("/admin/audit/events")
def list_admin_audit_events(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(require_admin),
) -> dict:
    rows = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "actor": r.actor,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "details": r.details,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        "requested_by": str(auth_payload.get("sub") or "admin"),
    }
