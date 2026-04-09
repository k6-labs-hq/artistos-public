"""
Catalog Value Appraiser — API endpoints.

POST /artists/{artist_id}/catalog/value-appraisal
GET  /artists/{artist_id}/catalog/value-appraisal/result
GET  /artists/{artist_id}/catalog/value-appraisal/history
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.api.deps import get_artist_or_404
from XR7.modules.catalog_value_appraiser import CatalogValueAppraiser
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["catalog_value_appraiser"])


class AppraisalRequest(BaseModel):
    catalog_health_score: float = 0.75
    concentration_score: float = 0.3
    territory_coverage_ratio: float = 0.7
    trajectory: str = "STABLE"


@router.post("/artists/{artist_id}/catalog/value-appraisal")
def trigger_appraisal(
    artist_id: str,
    body: AppraisalRequest,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Trigger catalog value appraisal for this artist."""
    artist = get_artist_or_404(artist_id, db)
    appraiser = CatalogValueAppraiser(db)
    result = appraiser.appraise(
        artist_id=artist_id,
        catalog_health_score=body.catalog_health_score,
        concentration_score=body.concentration_score,
        territory_coverage_ratio=body.territory_coverage_ratio,
        trajectory=body.trajectory,
    )
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/catalog/value-appraisal/result")
def get_appraisal_result(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Retrieve the latest catalog value appraisal."""
    artist = get_artist_or_404(artist_id, db)
    appraiser = CatalogValueAppraiser(db)
    result = appraiser.appraise(artist_id=artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/catalog/value-appraisal/history")
def get_appraisal_history(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Historical appraisals over time (tracks catalog value growth)."""
    artist = get_artist_or_404(artist_id, db)
    # Historical appraisals stored in the immutable ledger
    from XR7.recovery.immutable_ledger import ImmutableLedgerService
    ledger = ImmutableLedgerService(db)
    entries = ledger.list_entries(artist_id)
    history = [
        {
            "entry_hash": e.entry_hash,
            "appraised_at": e.created_at.isoformat() if e.created_at else None,
            "payload": e.payload_json,
        }
        for e in entries
        if e.entry_type == "catalog_value_appraisal"
    ]
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "history": history,
        "count": len(history),
    })
