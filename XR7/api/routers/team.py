from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from XR7.network.coop_recovery import CoopRecoveryNetwork

router = APIRouter(tags=["team"])


class InviteRequest(BaseModel):
    email: str


@router.post("/artists/{artist_id}/network/invite")
def network_invite(artist_id: str, payload: InviteRequest):
    return CoopRecoveryNetwork().invite_collaborator(artist_id, payload.email)
