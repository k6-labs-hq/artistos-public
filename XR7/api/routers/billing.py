from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.billing.engine import BillingEngine
from XR7.models.base import get_db
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus

router = APIRouter(tags=["billing"])


@router.get("/artists/{artist_id}/billing")
def get_billing_summary(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = BillingEngine(db)
    return engine.get_artist_billing_summary(artist_id)


@router.get("/artists/{artist_id}/invoices")
def list_invoices(artist_id: str, db: Session = Depends(get_db)):
    claims = (
        db.query(Claim)
        .filter(Claim.artist_id == artist_id, Claim.contingency_fee.is_not(None))
        .all()
    )
    invoices = []
    for c in claims:
        invoices.append({
            "claim_id": c.id,
            "recovered_amount": c.recovered_amount,
            "contingency_fee": c.contingency_fee,
            "currency": c.currency,
            "claim_status": c.status,
        })
    return invoices
