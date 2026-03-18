from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.identity_match import (
    ArtistIdentityMatch,
    ArtistIdentityMatchAudit,
    ArtistIdentityMatchAuditSchema,
    ArtistIdentityMatchSchema,
    IdentityDecisionStatus,
)
from XR7.models.statement import Statement
from XR7.services.identity_matching import apply_identity_decision, persist_identity_match

router = APIRouter(tags=["identity"])


class IdentityDecisionRequest(BaseModel):
    decision: IdentityDecisionStatus
    actor: str = Field(min_length=3, max_length=120)
    reason: str = Field(min_length=3, max_length=400)


class IdentityMatchRequest(BaseModel):
    statement_id: str | None = None
    statement_signals: dict


def _artist_or_404(db: Session, artist_id: str) -> Artist:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.post("/artists/{artist_id}/identity/auto-match", response_model=ArtistIdentityMatchSchema)
def auto_match_identity(
    artist_id: str,
    payload: IdentityMatchRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> ArtistIdentityMatchSchema:
    artist = _artist_or_404(db, artist_id)

    statement = None
    if payload.statement_id:
        statement = (
            db.query(Statement)
            .filter(Statement.id == payload.statement_id, Statement.artist_id == artist_id)
            .first()
        )
        if not statement:
            raise HTTPException(status_code=404, detail="Statement not found for artist")

    record = persist_identity_match(db, artist, statement, payload.statement_signals)
    return ArtistIdentityMatchSchema.model_validate(record)


@router.get("/artists/{artist_id}/identity/matches")
def list_identity_matches(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    _artist_or_404(db, artist_id)
    rows = (
        db.query(ArtistIdentityMatch)
        .filter(ArtistIdentityMatch.artist_id == artist_id)
        .order_by(ArtistIdentityMatch.created_at.desc())
        .all()
    )
    return {
        "artist_id": artist_id,
        "count": len(rows),
        "matches": [ArtistIdentityMatchSchema.model_validate(r).model_dump(mode="json") for r in rows],
    }


@router.get("/artists/{artist_id}/identity/matches/{match_id}/audit")
def get_identity_match_audit(
    artist_id: str,
    match_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    _artist_or_404(db, artist_id)
    match = (
        db.query(ArtistIdentityMatch)
        .filter(ArtistIdentityMatch.id == match_id, ArtistIdentityMatch.artist_id == artist_id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Identity match not found")

    audits = (
        db.query(ArtistIdentityMatchAudit)
        .filter(ArtistIdentityMatchAudit.match_id == match_id)
        .order_by(ArtistIdentityMatchAudit.created_at.asc())
        .all()
    )
    return {
        "artist_id": artist_id,
        "match_id": match_id,
        "chain_head": match.chain_hash,
        "audit": [ArtistIdentityMatchAuditSchema.model_validate(a).model_dump(mode="json") for a in audits],
    }


@router.post("/artists/{artist_id}/identity/matches/{match_id}/decision", response_model=ArtistIdentityMatchSchema)
def decide_identity_match(
    artist_id: str,
    match_id: str,
    payload: IdentityDecisionRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> ArtistIdentityMatchSchema:
    _artist_or_404(db, artist_id)
    match = (
        db.query(ArtistIdentityMatch)
        .filter(ArtistIdentityMatch.id == match_id, ArtistIdentityMatch.artist_id == artist_id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Identity match not found")

    if payload.decision in {
        IdentityDecisionStatus.AUTO_ACCEPTED,
        IdentityDecisionStatus.PENDING_SOFT_CONFIRM,
        IdentityDecisionStatus.PENDING_EXPLICIT_CONFIRM,
    }:
        raise HTTPException(status_code=422, detail="Only CONFIRMED or REJECTED are accepted decisions")

    try:
        updated = apply_identity_decision(
            db,
            match,
            decision=payload.decision,
            actor=payload.actor,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ArtistIdentityMatchSchema.model_validate(updated)
