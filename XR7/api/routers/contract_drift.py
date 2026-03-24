"""
Contract Drift Monitor — API endpoints.

GET  /artists/{artist_id}/contracts/drift
GET  /artists/{artist_id}/contracts/{contract_id}/drift
POST /artists/{artist_id}/contracts/{contract_id}/drift/dispute
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.modules.contract_drift_monitor import ContractDriftMonitor
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["contract_drift_monitor"])


@router.get("/artists/{artist_id}/contracts/drift")
def get_all_contract_drift(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """All contract drift data for this artist."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    monitor = ContractDriftMonitor(db)
    result = monitor.analyze_all(artist_id)
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/contracts/{contract_id}/drift")
def get_contract_drift(
    artist_id: str,
    contract_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Drift timeline for a specific contract."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    monitor = ContractDriftMonitor(db)
    result = monitor.analyze_contract(artist_id, contract_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return inject_branding_metadata(db, result)


class DriftDisputeRequest(BaseModel):
    reason: str | None = None


@router.post("/artists/{artist_id}/contracts/{contract_id}/drift/dispute")
def initiate_drift_dispute(
    artist_id: str,
    contract_id: str,
    body: DriftDisputeRequest,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Initiate a dispute workflow from a contract drift finding."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    monitor = ContractDriftMonitor(db)
    drift = monitor.analyze_contract(artist_id, contract_id)
    if drift is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    # Hand off to claims orchestration — return dispute initiation record
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "contract_id": contract_id,
        "dispute_initiated": True,
        "drift_classification": drift.get("latest_classification"),
        "cumulative_drift_cost": drift.get("cumulative_drift_cost"),
        "reason": body.reason,
        "action": "Review by analyst team. Claims workflow will be triggered.",
    })
