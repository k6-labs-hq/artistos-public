"""Collaborator Share — viral invite loop triggered after analysis completion.

After a creator's analysis finishes, this endpoint:
  1. Accepts a list of collaborators (co-writers, producers, publishers, etc.)
  2. Creates an Invite record for each collaborator
  3. Logs each collaborator in HubSpot CRM as a lead
  4. Returns a ready-to-copy share message containing the creator's personal
     invite link so they can forward it to their collaborators.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.collaborator_share_lead import CollaboratorRole, CollaboratorShareLead
from XR7.models.invite import InviteChannel, InviteRole
from XR7.services.branding import inject_branding_metadata
from XR7.services.hubspot_client import HubSpotClient
from XR7.services.invite_service import get_invite_service

router = APIRouter(tags=["collaborator_share"])

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

_ROLE_TO_INVITE_ROLE: dict[str, InviteRole] = {
    CollaboratorRole.CO_WRITER.value: InviteRole.WRITER,
    CollaboratorRole.PRODUCER.value: InviteRole.ARTIST,
    CollaboratorRole.PUBLISHER.value: InviteRole.DISTRIBUTOR,
    CollaboratorRole.MANAGER.value: InviteRole.MANAGER,
    CollaboratorRole.LABEL.value: InviteRole.DISTRIBUTOR,
    CollaboratorRole.OTHER.value: InviteRole.ARTIST,
}

_ROLE_LABEL: dict[str, str] = {
    CollaboratorRole.CO_WRITER.value: "co-writer",
    CollaboratorRole.PRODUCER.value: "producer",
    CollaboratorRole.PUBLISHER.value: "publisher",
    CollaboratorRole.MANAGER.value: "manager",
    CollaboratorRole.LABEL.value: "label",
    CollaboratorRole.OTHER.value: "collaborator",
}


class CollaboratorInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    role: CollaboratorRole = CollaboratorRole.CO_WRITER


class CollaboratorShareRequest(BaseModel):
    collaborators: list[CollaboratorInput] = Field(..., min_length=1, max_length=50)


class CollaboratorShareResult(BaseModel):
    collaborator_name: str
    role: str
    invite_link: str
    invite_token: str
    lead_id: str
    hubspot_logged: bool


class CollaboratorShareResponse(BaseModel):
    share_message: str
    collaborators: list[CollaboratorShareResult]
    total_logged: int


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/collaborator-share",
    response_model=CollaboratorShareResponse,
)
def generate_collaborator_share(
    artist_id: str,
    req: CollaboratorShareRequest,
    db: Session = Depends(get_db),
    _auth: dict = Depends(require_artist_access),
) -> dict:
    """Generate a shareable invite message for co-writers, producers, and publishers.

    For each collaborator supplied:
    - An Invite record is created so they can onboard directly.
    - A CRM lead is upserted in HubSpot so the growth team can follow up.
    - The endpoint returns a personalised copy-paste message the creator can
      send via text, email, or DM.

    The invite link encodes the creator as the referral source, closing the
    viral loop — every collaborator who signs up is attributed back to the
    artist who referred them.
    """
    artist: Artist | None = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    invite_svc = get_invite_service(db)
    hs = HubSpotClient()

    results: list[CollaboratorShareResult] = []

    # Use the first generated invite link as the primary share link
    primary_invite_link: str | None = None

    for collab in req.collaborators:
        invite_role = _ROLE_TO_INVITE_ROLE.get(collab.role.value, InviteRole.ARTIST)
        role_label = _ROLE_LABEL.get(collab.role.value, "collaborator")

        # Build invite
        invite, raw_token = invite_svc.create_invite(
            recipient_name=collab.name,
            recipient_email=collab.email,
            channel=InviteChannel.MANUAL,
            role=invite_role,
            campaign="collaborator_share_panel",
            referring_agent_id=artist_id,
            custom_message=(
                f"Invited by {artist.name} after their XR7 royalty analysis. "
                f"Role: {role_label}."
            ),
        )
        db.flush()

        # Build invite URL (frontend handles the /invite/:token route)
        invite_link = f"/invite/{raw_token}"
        if primary_invite_link is None:
            primary_invite_link = invite_link

        # Log to HubSpot CRM — fire-and-forget; failure is non-blocking
        hs_result = hs.log_collaborator_lead(
            name=collab.name,
            email=collab.email,
            role=collab.role.value,
            source_artist_id=artist_id,
            source_artist_name=artist.name,
        )
        hs_contact_id: str | None = hs_result.get("object_id")
        hubspot_logged = bool(hs_result.get("ok") and hs_contact_id)

        # Persist lead record
        lead = CollaboratorShareLead(
            source_artist_id=artist_id,
            collaborator_name=collab.name,
            collaborator_email=collab.email,
            collaborator_role=collab.role.value,
            invite_id=invite.id,
            hubspot_contact_id=hs_contact_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(lead)
        db.flush()

        results.append(
            CollaboratorShareResult(
                collaborator_name=collab.name,
                role=collab.role.value,
                invite_link=invite_link,
                invite_token=raw_token,
                lead_id=lead.id,
                hubspot_logged=hubspot_logged,
            )
        )

    # Compose the share message using the first collaborator's invite link as the
    # primary call-to-action. Each collaborator receives their own unique token
    # in the results array for individual forwarding.
    collab_names = _format_name_list([c.collaborator_name for c in results])
    share_message = _compose_share_message(
        artist_name=artist.name,
        collab_names=collab_names,
        invite_link=primary_invite_link or "/invite",
    )

    # Back-fill the share message text onto each lead for audit trail
    for lead_result in results:
        db.query(CollaboratorShareLead).filter(
            CollaboratorShareLead.id == lead_result.lead_id
        ).update({"share_message_text": share_message})

    db.commit()

    return inject_branding_metadata(
        db,
        CollaboratorShareResponse(
            share_message=share_message,
            collaborators=results,
            total_logged=len(results),
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_name_list(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _compose_share_message(
    artist_name: str,
    collab_names: str,
    invite_link: str,
) -> str:
    return (
        f"Hey {collab_names},\n\n"
        f"I just ran an XR7 royalty analysis on my catalog and found real money sitting in "
        f"unpaid royalties. Since we've worked together, there's a good chance some of these "
        f"recoveries include splits tied to your name too.\n\n"
        f"XR7 audits streaming platforms, PROs, and distributors — it's completely free to "
        f"start and they only collect a small percentage if they actually recover something "
        f"for you.\n\n"
        f"Use my personal link to get early access:\n"
        f"{invite_link}\n\n"
        f"— {artist_name}"
    )
