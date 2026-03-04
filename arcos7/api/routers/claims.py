from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from arcos7.models.base import get_db
from arcos7.models.claim import Claim, ClaimSchema
from arcos7.recovery.orchestrator import ClaimsOrchestrator

router = APIRouter(tags=["claims"])


@router.get("/artists/{artist_id}/claims")
def list_claims(artist_id: str, db: Session = Depends(get_db)):
    return db.query(Claim).filter(Claim.artist_id == artist_id).all()


@router.get("/claims/{claim_id}", response_model=ClaimSchema)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/claims/{claim_id}/advance", response_model=ClaimSchema)
def advance_claim(claim_id: str, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        return orchestrator.advance_claim(claim_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claims/{claim_id}/evidence")
def generate_evidence(claim_id: str, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        return orchestrator.generate_evidence_packet(claim_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class ReconcileRequest(BaseModel):
    recovered_amount: float
    currency: str


@router.post("/claims/{claim_id}/reconcile", response_model=ClaimSchema)
def reconcile_claim(claim_id: str, body: ReconcileRequest, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        return orchestrator.reconcile_recovered_amount(claim_id, body.recovered_amount, body.currency)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
