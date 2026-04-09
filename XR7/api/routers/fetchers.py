from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.ingestion.connectors.global_social_regional import GlobalSocialRegionalConnector
from XR7.models.base import get_db
from XR7.recovery.ugc_claim_generator import UGCClaimGenerator
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["fetchers"])


@router.post("/artists/{artist_id}/fetchers/global-social")
async def fetch_global_social(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    conn = GlobalSocialRegionalConnector()
    rows = await conn.scan_ugc_opportunities(artist_id)
    generator = UGCClaimGenerator(db)
    claim_ids: list[str] = []
    for r in rows:
        if float(r.get("estimated_recoverable") or 0.0) >= 3000:
            claim_ids.append(
                await generator.create_claim(artist_id, str(r.get("platform") or "generic"), r)
            )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "detected": rows,
            "auto_claim_eligible": [
                r for r in rows if float(r.get("estimated_recoverable") or 0.0) >= 3000
            ],
            "auto_claim_ids": claim_ids,
        },
    )
