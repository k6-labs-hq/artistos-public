from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.xr7_metadata_service import apply_metadata_repairs, suggest_metadata_repairs

router = APIRouter(tags=["xr7-metadata"])


class MetadataRepairSuggestRequest(BaseModel):
    tenant_id: str = "default"
    scope: str = "catalog"
    max_items: int = 50


class MetadataRepairApplyRequest(BaseModel):
    tenant_id: str = "default"
    suggestion_ids: list[str] = Field(default_factory=list)
    dry_run: bool = False


@router.post("/artists/{artist_id}/xr7/metadata/repair/suggest")
def suggest_repairs(artist_id: str, payload: MetadataRepairSuggestRequest, db: Session = Depends(get_db)):
    return suggest_metadata_repairs(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        scope=payload.scope,
        max_items=max(1, min(500, payload.max_items)),
    )


@router.post("/artists/{artist_id}/xr7/metadata/repair/apply")
def apply_repairs(artist_id: str, payload: MetadataRepairApplyRequest, db: Session = Depends(get_db)):
    return apply_metadata_repairs(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        suggestion_ids=payload.suggestion_ids,
        dry_run=payload.dry_run,
    )
