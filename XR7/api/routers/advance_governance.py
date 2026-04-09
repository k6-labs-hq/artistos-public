from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_auth_payload, require_analyst, require_artist_access, require_executive, require_legal
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.api.deps import get_artist_or_404
from XR7.services.analyst_gated_advance import (
    add_failed_packet_signature,
    analyst_decision,
    artist_accept_offer,
    complete_failed_packet,
    executive_decision,
    generate_failed_advance_recovery_packet,
    list_analyst_queue,
    list_executive_queue,
    list_visible_artist_offers,
    publish_artist_offer,
    run_nightly_advance_opportunity_scan,
)
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["advance-governance"])


class ApprovalRequest(BaseModel):
    approved: bool
    notes: str | None = None


class FailedPacketRequest(BaseModel):
    failure_reason: str


class PacketSignRequest(BaseModel):
    note: str | None = None


@router.post("/admin/advances/run-nightly-eval")
def run_nightly_eval(
    db: Session = Depends(get_db),
    auth: dict = Depends(require_analyst),
) -> dict:
    result = run_nightly_advance_opportunity_scan(db)
    return {
        "triggered_by": auth.get("sub"),
        **result,
    }


@router.get("/admin/advances/queue/analyst")
def analyst_queue(
    db: Session = Depends(get_db),
    _: dict = Depends(require_analyst),
) -> dict:
    rows = list_analyst_queue(db)
    return {
        "count": len(rows),
        "items": [
            {
                "opportunity_id": r.id,
                "artist_id": r.artist_id,
                "anomaly_id": r.anomaly_id,
                "claim_id": r.claim_id,
                "model_score": r.model_score,
                "predicted_recovery_amount": r.predicted_recovery_amount,
                "max_advance_amount": r.max_advance_amount,
                "proposed_advance_fee_percent": r.proposed_advance_fee_percent,
                "currency": r.currency,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.post("/admin/advances/opportunities/{opportunity_id}/analyst-decision")
def approve_analyst(
    opportunity_id: str,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_analyst),
) -> dict:
    try:
        row = analyst_decision(
            db,
            opportunity_id=opportunity_id,
            approved=payload.approved,
            notes=payload.notes,
            actor_subject=str(auth.get("sub") or "unknown"),
            actor_role=str(auth.get("role") or "analyst"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "opportunity_id": row.id,
        "status": row.status,
        "analyst_notes": row.analyst_notes,
    }


@router.get("/admin/advances/queue/executive")
def executive_queue(
    db: Session = Depends(get_db),
    _: dict = Depends(require_executive),
) -> dict:
    rows = list_executive_queue(db)
    return {
        "count": len(rows),
        "items": [
            {
                "opportunity_id": r.id,
                "artist_id": r.artist_id,
                "anomaly_id": r.anomaly_id,
                "claim_id": r.claim_id,
                "model_score": r.model_score,
                "predicted_recovery_amount": r.predicted_recovery_amount,
                "max_advance_amount": r.max_advance_amount,
                "proposed_advance_fee_percent": r.proposed_advance_fee_percent,
                "currency": r.currency,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.post("/admin/advances/opportunities/{opportunity_id}/executive-decision")
def approve_executive(
    opportunity_id: str,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_executive),
) -> dict:
    try:
        row = executive_decision(
            db,
            opportunity_id=opportunity_id,
            approved=payload.approved,
            notes=payload.notes,
            actor_subject=str(auth.get("sub") or "unknown"),
            actor_role=str(auth.get("role") or "executive"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "opportunity_id": row.id,
        "status": row.status,
        "executive_notes": row.executive_notes,
    }


@router.post("/admin/advances/opportunities/{opportunity_id}/publish-offer")
def publish_offer(
    opportunity_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_executive),
) -> dict:
    try:
        offer = publish_artist_offer(db, opportunity_id=opportunity_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "offer_id": offer.id,
        "opportunity_id": offer.opportunity_id,
        "artist_id": offer.artist_id,
        "offered_amount": offer.offered_amount,
        "currency": offer.currency,
        "advance_fee_percent": offer.advance_fee_percent,
        "effective_total_fee_cap_percent": offer.effective_total_fee_cap_percent,
        "status": offer.status,
        "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
    }


@router.post("/admin/advances/offers/{offer_id}/failed-recovery-packet")
def create_failed_packet(
    offer_id: str,
    payload: FailedPacketRequest,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_executive),
) -> dict:
    try:
        packet = generate_failed_advance_recovery_packet(
            db,
            offer_id=offer_id,
            failure_reason=payload.failure_reason,
            actor_subject=str(auth.get("sub") or "unknown"),
            actor_role=str(auth.get("role") or "executive"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "packet_id": packet.id,
        "offer_id": packet.offer_id,
        "artist_id": packet.artist_id,
        "status": packet.status,
        "immutable_ledger_hash": packet.immutable_ledger_hash,
        "required_signers": packet.required_signers,
        "collected_signatures": packet.collected_signatures,
    }


@router.post("/admin/advances/packets/{packet_id}/sign")
def sign_failed_packet(
    packet_id: str,
    payload: PacketSignRequest,
    db: Session = Depends(get_db),
    auth: dict = Depends(get_auth_payload),
) -> dict:
    role = str(auth.get("role") or "").strip().lower()
    if role not in {"analyst", "exec", "executive", "legal", "counsel", "general_counsel", "admin"}:
        raise HTTPException(status_code=403, detail="Internal signer role required")
    try:
        packet = add_failed_packet_signature(
            db,
            packet_id=packet_id,
            actor_subject=str(auth.get("sub") or "unknown"),
            actor_role=str(auth.get("role") or "unknown"),
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "packet_id": packet.id,
        "status": packet.status,
        "collected_signatures": packet.collected_signatures,
        "required_signers": packet.required_signers,
    }


@router.post("/admin/advances/packets/{packet_id}/complete")
def complete_packet(
    packet_id: str,
    db: Session = Depends(get_db),
    auth: dict = Depends(require_legal),
) -> dict:
    try:
        packet = complete_failed_packet(
            db,
            packet_id=packet_id,
            actor_subject=str(auth.get("sub") or "unknown"),
            actor_role=str(auth.get("role") or "legal"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "packet_id": packet.id,
        "status": packet.status,
        "immutable_ledger_hash": packet.immutable_ledger_hash,
        "collected_signatures": packet.collected_signatures,
        "required_signers": packet.required_signers,
    }


@router.get("/artists/{artist_id}/advance/offers")
def list_artist_offers(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    artist = get_artist_or_404(artist_id, db)

    offers = list_visible_artist_offers(db, artist_id=artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "count": len(offers),
            "offers": [
                {
                    "offer_id": o.id,
                    "opportunity_id": o.opportunity_id,
                    "offered_amount": o.offered_amount,
                    "currency": o.currency,
                    "advance_fee_percent": o.advance_fee_percent,
                    "effective_total_fee_cap_percent": o.effective_total_fee_cap_percent,
                    "status": o.status,
                    "expires_at": o.expires_at.isoformat() if o.expires_at else None,
                }
                for o in offers
            ],
        },
    )


@router.post("/artists/{artist_id}/advance/offers/{offer_id}/accept")
def accept_artist_offer(
    artist_id: str,
    offer_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    try:
        offer = artist_accept_offer(db, artist_id=artist_id, offer_id=offer_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "offer_id": offer.id,
            "status": offer.status,
            "message": "Advance offer accepted. Disbursement has been queued.",
        },
    )
