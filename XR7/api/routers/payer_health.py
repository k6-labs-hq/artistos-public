"""
Payer Health Score — API endpoints.

GET /artists/{artist_id}/payers/health
GET /artists/{artist_id}/payers/{payer_id}/health
GET /payers/health/global
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.base import get_db
from XR7.modules.payer_health_score import PayerHealthScorer, global_aggregate_scores
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["payer_health_score"])


@router.get("/artists/{artist_id}/payers/health")
def get_all_payer_scores(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """All payer health scores for this artist."""
    get_artist_or_404(artist_id, db)
    scorer = PayerHealthScorer(db)
    result = scorer.score_all(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/payers/{payer_id}/health")
def get_single_payer_score(
    artist_id: str,
    payer_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Health score for a specific payer."""
    get_artist_or_404(artist_id, db)
    scorer = PayerHealthScorer(db)
    result = scorer.score_single(artist_id, payer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Payer not found for this artist")
    return inject_branding_metadata(db, result)


@router.get("/payers/health/global")
def get_global_payer_health(
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Platform-wide aggregate payer health scores (anonymised)."""
    return global_aggregate_scores(db)
