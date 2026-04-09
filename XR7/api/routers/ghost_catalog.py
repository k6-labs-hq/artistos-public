"""
Ghost Catalog Detector — API endpoints.

POST /artists/{artist_id}/catalog/ghost-scan
GET  /artists/{artist_id}/catalog/ghosts
GET  /artists/{artist_id}/catalog/ghosts/{work_id}
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.api.deps import get_artist_or_404
from XR7.modules.ghost_catalog_detector import GhostCatalogDetector
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["ghost_catalog_detector"])


@router.post("/artists/{artist_id}/catalog/ghost-scan")
def trigger_ghost_scan(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Trigger Ghost Catalog Detector scan for this artist."""
    artist = get_artist_or_404(artist_id, db)
    detector = GhostCatalogDetector(db)
    result = detector.scan(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/catalog/ghosts")
def list_ghost_works(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Retrieve detected ghost works for this artist."""
    artist = get_artist_or_404(artist_id, db)
    detector = GhostCatalogDetector(db)
    result = detector.scan(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/catalog/ghosts/{work_id}")
def get_ghost_work(
    artist_id: str,
    work_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Detail for a specific ghost work."""
    artist = get_artist_or_404(artist_id, db)
    detector = GhostCatalogDetector(db)
    result = detector.scan(artist_id)
    for ghost in result.get("ghost_works", []):
        if ghost["work_id"] == work_id:
            return inject_branding_metadata(db, ghost)
    raise HTTPException(status_code=404, detail="Ghost work not found")
