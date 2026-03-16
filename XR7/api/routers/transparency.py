from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.transparency.immutable_ledger_viewer import ImmutableLedgerViewer

router = APIRouter(tags=["transparency"])


@router.get("/artists/{artist_id}/ledger/full")
def full_ledger(artist_id: str, include_raw_statements: bool = True, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    payload = ImmutableLedgerViewer(db).get_full_ledger(artist_id, include_raw_statements=include_raw_statements)
    return inject_branding_metadata(db, payload)


@router.get("/artists/{artist_id}/anomalies/{anomaly_id}/explain")
async def explain_anomaly(artist_id: str, anomaly_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    payload = await ImmutableLedgerViewer(db).explain_anomaly(anomaly_id)
    return inject_branding_metadata(db, {"artist_id": artist_id, **payload})
