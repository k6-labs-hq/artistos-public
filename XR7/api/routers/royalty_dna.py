"""
Royalty DNA Profile — API endpoints.

POST /artists/{artist_id}/profile/dna
GET  /artists/{artist_id}/profile/dna/result
GET  /artists/{artist_id}/profile/dna/insights
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.base import get_db
from XR7.modules.royalty_dna_profile import RoyaltyDNAProfile
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["royalty_dna_profile"])


@router.post("/artists/{artist_id}/profile/dna")
def trigger_dna_profile(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Trigger Royalty DNA Profile generation for this artist."""
    get_artist_or_404(artist_id, db)
    profiler = RoyaltyDNAProfile(db)
    result = profiler.generate(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/profile/dna/result")
def get_dna_result(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Retrieve the Royalty DNA Profile result."""
    get_artist_or_404(artist_id, db)
    profiler = RoyaltyDNAProfile(db)
    result = profiler.generate(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/profile/dna/insights")
def get_dna_insights(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Plain-language insights only from the Royalty DNA Profile."""
    get_artist_or_404(artist_id, db)
    profiler = RoyaltyDNAProfile(db)
    result = profiler.generate(artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "insights": result.get("insights", []),
            "territory_gaps": result.get("territory_gaps", []),
            "chain_of_custody_hash": result.get("chain_of_custody_hash"),
        },
    )
