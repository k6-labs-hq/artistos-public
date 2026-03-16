from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.network.coop_recovery import CoopRecoveryNetwork
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["team"])


class InviteRequest(BaseModel):
    email: str


@router.post("/artists/{artist_id}/network/invite")
def network_invite(artist_id: str, payload: InviteRequest, db: Session = Depends(get_db)):
    out = CoopRecoveryNetwork().invite_collaborator(artist_id, payload.email)
    if isinstance(out, dict):
        return inject_branding_metadata(db, {"artist_id": artist_id, **out})
    return inject_branding_metadata(db, {"artist_id": artist_id, "result": out})
