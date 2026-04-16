"""
Recovery Credit Score — API endpoints.

GET  /artists/{artist_id}/recovery-score
GET  /artists/{artist_id}/recovery-score/history
GET  /artists/{artist_id}/recovery-score/actions
POST /admin/advances/recovery-score/{artist_id}
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.authz import require_admin
from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.base import get_db
from XR7.modules.recovery_credit_score import RecoveryCreditScore
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["recovery_credit_score"])


@router.get("/artists/{artist_id}/recovery-score")
def get_recovery_score(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Current recovery credit score, tier, delta, and component breakdown."""
    get_artist_or_404(artist_id, db)
    scorer = RecoveryCreditScore(db)
    result = scorer.calculate(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/recovery-score/history")
def get_recovery_score_history(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Historical recovery credit score timeline."""
    get_artist_or_404(artist_id, db)
    from XR7.recovery.immutable_ledger import ImmutableLedgerService

    ledger = ImmutableLedgerService(db)
    entries = ledger.list_entries(artist_id)
    history = [
        {
            "entry_hash": e.entry_hash,
            "calculated_at": e.created_at.isoformat() if e.created_at else None,
            "payload": e.payload_json,
        }
        for e in entries
        if e.entry_type == "recovery_credit_score_calculated"
    ]
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "history": history,
            "count": len(history),
        },
    )


@router.get("/artists/{artist_id}/recovery-score/actions")
def get_recovery_score_actions(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Ranked list of improvement actions with estimated score impact."""
    get_artist_or_404(artist_id, db)
    scorer = RecoveryCreditScore(db)
    result = scorer.calculate(artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "actions": result.get("actions", []),
            "current_score": result.get("score"),
            "current_tier": result.get("tier"),
        },
    )


class AdvanceQualificationRequest(BaseModel):
    requested_advance_amount: float | None = None
    notes: str | None = None


@router.post("/admin/advances/recovery-score/{artist_id}")
def advance_qualification(
    artist_id: str,
    body: AdvanceQualificationRequest,
    _admin: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Internal endpoint: qualify and size a recovery advance using the score."""
    get_artist_or_404(artist_id, db)
    scorer = RecoveryCreditScore(db)
    result = scorer.calculate(artist_id)
    score = result["score"]
    tier = result["tier"]

    # Simple qualification logic
    qualified = score >= 450
    max_advance = 0.0
    if tier == "EXCEPTIONAL":
        max_advance = 50000.0
    elif tier == "STRONG":
        max_advance = 25000.0
    elif tier == "GOOD":
        max_advance = 10000.0
    elif tier == "FAIR":
        max_advance = 5000.0
    elif tier == "DEVELOPING":
        max_advance = 2000.0

    return {
        "artist_id": artist_id,
        "recovery_score": score,
        "tier": tier,
        "qualified_for_advance": qualified,
        "max_advance_amount": max_advance,
        "requested_amount": body.requested_advance_amount,
        "approved_amount": (
            min(body.requested_advance_amount, max_advance)
            if body.requested_advance_amount and qualified
            else 0.0
        ),
        "notes": body.notes,
        "component_breakdown": result["components"],
    }
