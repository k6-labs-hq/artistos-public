from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.billing.engine import BillingEngine
from XR7.models.base import get_db
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.services.branding import inject_branding_metadata, branding_metadata, get_branding_for_artist

router = APIRouter(tags=["billing"])


@router.get("/artists/{artist_id}/billing")
def get_billing_summary(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = BillingEngine(db)
    summary = engine.get_artist_billing_summary(artist_id)
    fee_percent = float(artist.contingency_fee_percent or 0.0)
    summary["contingency_fee_percent"] = fee_percent
    summary["fee_display"] = (
        "Contingency fee: 12% (Founder rate - permanent)"
        if artist.is_founder
        else f"Contingency fee: {fee_percent:.2f}%"
    )
    return inject_branding_metadata(db, summary)


@router.get("/artists/{artist_id}/invoices")
def list_invoices(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    claims = (
        db.query(Claim)
        .filter(Claim.artist_id == artist_id, Claim.contingency_fee.is_not(None))
        .all()
    )
    brand = get_branding_for_artist(db, artist_id)
    invoices = []
    for c in claims:
        invoices.append({
            "artist_id": artist_id,
            "branding": branding_metadata(brand),
            "claim_id": c.id,
            "recovered_amount": c.recovered_amount,
            "contingency_fee": c.contingency_fee,
            "contingency_fee_percent": float(artist.contingency_fee_percent or 0.0),
            "fee_copy": (
                f"XR7 retains {float(artist.contingency_fee_percent or 0.0):.2f}% "
                f"(${float(c.contingency_fee or 0.0):,.2f}) You receive "
                f"${float((c.recovered_amount or 0.0) - (c.contingency_fee or 0.0)):,.2f}"
            ),
            "currency": c.currency,
            "claim_status": c.status,
        })
    return invoices
