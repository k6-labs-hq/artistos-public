"""Concierge Inbox: in-app messaging between artists and XR7 analysts.

Endpoints:
  GET  /artists/{artist_id}/concierge/messages  – list inbox messages
  POST /concierge/send                          – send a concierge message
  POST /artists/{artist_id}/concierge/read      – mark messages as read
  POST /artists/{artist_id}/concierge/escalate  – request human analyst
  POST /artists/{artist_id}/persona/enrich      – trigger persona enrichment job
  GET  /artists/{artist_id}/persona             – get persona profile
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.vip import (
    ConciergeMessageSchema,
    ConciergeMessageSender,
    EnrichPersonaRequest,
    PersonaProfileSchema,
    SendConciergeMessageRequest,
)
from XR7.services.vip_service import VipService

router = APIRouter(tags=["concierge"])


# ---------------------------------------------------------------------------
# Guard helper
# ---------------------------------------------------------------------------

def _require_vip(artist_id: str, svc: VipService) -> None:
    if not svc.is_vip(artist_id):
        raise HTTPException(
            status_code=403,
            detail="Founders Circle / VIP membership required to access concierge features.",
        )


# ---------------------------------------------------------------------------
# Concierge inbox
# ---------------------------------------------------------------------------

@router.get(
    "/artists/{artist_id}/concierge/messages",
    response_model=list[ConciergeMessageSchema],
    summary="List concierge inbox messages for an artist",
)
def list_concierge_messages(
    artist_id: str,
    limit: int = Query(50, ge=1, le=200),
    thread_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> list[ConciergeMessageSchema]:
    svc = VipService(db)
    _require_vip(artist_id, svc)
    messages = svc.get_messages(artist_id, limit=limit, thread_id=thread_id)
    return [ConciergeMessageSchema.model_validate(m) for m in messages]


@router.post(
    "/concierge/send",
    response_model=ConciergeMessageSchema,
    summary="Send a concierge message (artist → analyst or system)",
)
def send_concierge_message(
    body: SendConciergeMessageRequest,
    db: Session = Depends(get_db),
) -> ConciergeMessageSchema:
    svc = VipService(db)
    _require_vip(body.artist_id, svc)

    # Determine sender name
    membership = svc.get_membership(body.artist_id)
    artist_name = "You"
    if membership:
        from XR7.models.artist import Artist
        art = db.query(Artist).filter(Artist.id == body.artist_id).first()
        if art:
            artist_name = art.name

    msg = svc.send_message(
        body.artist_id,
        sender_type=ConciergeMessageSender.ARTIST,
        sender_name=artist_name,
        message_body=body.message_body,
        attachments=body.attachments,
        request_human_analyst=body.request_human_analyst,
        thread_id=body.thread_id or str(uuid.uuid4()),
    )
    return ConciergeMessageSchema.model_validate(msg)


class MarkReadRequest(BaseModel):
    message_ids: list[str]


class MarkReadResponse(BaseModel):
    marked: int


@router.post(
    "/artists/{artist_id}/concierge/read",
    response_model=MarkReadResponse,
    summary="Mark concierge messages as read",
)
def mark_messages_read(
    artist_id: str,
    body: MarkReadRequest,
    db: Session = Depends(get_db),
) -> MarkReadResponse:
    svc = VipService(db)
    _require_vip(artist_id, svc)
    count = svc.mark_messages_read(artist_id, body.message_ids)
    return MarkReadResponse(marked=count)


class EscalateResponse(BaseModel):
    success: bool
    message: str
    escalation_id: str


@router.post(
    "/artists/{artist_id}/concierge/escalate",
    response_model=EscalateResponse,
    summary="One-click escalation: request a named human analyst",
)
def request_human_analyst(
    artist_id: str,
    db: Session = Depends(get_db),
) -> EscalateResponse:
    svc = VipService(db)
    _require_vip(artist_id, svc)
    membership = svc.get_membership(artist_id)
    analyst_name = (membership.concierge_analyst_name if membership else None) or "XR7 Strategy Team"
    escalation_id = str(uuid.uuid4())
    svc.send_message(
        artist_id,
        sender_type=ConciergeMessageSender.SYSTEM,
        sender_name="XR7 Concierge",
        message_body=(
            f"Your request for a human analyst session has been received. "
            f"{analyst_name} will reach out within 24 hours. "
            f"Reference: {escalation_id[:8].upper()}"
        ),
        thread_id=escalation_id,
        request_human_analyst=True,
    )
    return EscalateResponse(
        success=True,
        message=f"Escalated to {analyst_name}. You'll hear back within 24 hours.",
        escalation_id=escalation_id,
    )


# ---------------------------------------------------------------------------
# Persona enrichment
# ---------------------------------------------------------------------------

class EnrichPersonaResponse(BaseModel):
    job_id: str
    status: str
    message: str


@router.post(
    "/artists/{artist_id}/persona/enrich",
    response_model=EnrichPersonaResponse,
    summary="Trigger background persona enrichment from public sources",
)
def enrich_persona(
    artist_id: str,
    body: EnrichPersonaRequest,
    db: Session = Depends(get_db),
) -> EnrichPersonaResponse:
    svc = VipService(db)
    _require_vip(artist_id, svc)

    # Dispatch Celery task
    from XR7.tasks.vip_tasks import enrich_artist_persona
    task = enrich_artist_persona.delay(artist_id, force=body.force)
    job_id = task.id

    svc.mark_enrichment_in_progress(artist_id, job_id)

    return EnrichPersonaResponse(
        job_id=job_id,
        status="in_progress",
        message="Persona enrichment started. Check back in a few minutes.",
    )


@router.get(
    "/artists/{artist_id}/persona",
    response_model=PersonaProfileSchema,
    summary="Get enriched persona profile",
)
def get_persona(
    artist_id: str,
    db: Session = Depends(get_db),
) -> PersonaProfileSchema:
    svc = VipService(db)
    _require_vip(artist_id, svc)
    profile = svc.get_or_create_persona(artist_id)
    return PersonaProfileSchema.model_validate(profile)
