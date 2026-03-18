from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.xr7_ugc_service import get_ugc_opportunities, ingest_ugc_signals

router = APIRouter(tags=["xr7-ugc"])


class UGCSignalIngestRequest(BaseModel):
    tenant_id: str = "default"
    platform: str
    signals: list[dict[str, object]] = Field(default_factory=list)


@router.post("/artists/{artist_id}/xr7/ugc/signals/ingest")
def ingest_signals(artist_id: str, payload: UGCSignalIngestRequest, db: Session = Depends(get_db)):
    return ingest_ugc_signals(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        platform=payload.platform,
        signals=payload.signals,
    )


@router.get("/artists/{artist_id}/xr7/ugc/opportunities")
def ugc_opportunities(
    artist_id: str,
    tenant_id: str = "default",
    min_confidence: float = 0.65,
    min_estimated_value: float = 0.0,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return {
        "opportunities": get_ugc_opportunities(
            db,
            tenant_id=tenant_id,
            artist_id=artist_id,
            min_confidence=min_confidence,
            min_estimated_value=min_estimated_value,
            status=status,
        )
    }
