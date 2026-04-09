from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.anomaly import Anomaly, AnomalyExplainWithRecoverabilitySchema, AnomalySchema
from XR7.models.base import get_db
from XR7.api.deps import get_artist_or_404
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.services.branding import inject_branding_metadata
from XR7.transparency.immutable_ledger_viewer import ImmutableLedgerViewer

router = APIRouter(tags=["transparency"])


@router.get("/artists/{artist_id}/ledger/full")
def full_ledger(artist_id: str, include_raw_statements: bool = True, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)
    payload = ImmutableLedgerViewer(db).get_full_ledger(artist_id, include_raw_statements=include_raw_statements)
    return inject_branding_metadata(db, payload)


@router.get("/artists/{artist_id}/anomalies/{anomaly_id}/explain", response_model=AnomalyExplainWithRecoverabilitySchema)
async def explain_anomaly(artist_id: str, anomaly_id: str, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)
    payload = await ImmutableLedgerViewer(db).explain_anomaly(anomaly_id)
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id, Anomaly.artist_id == artist_id).first()
    recoverability = {}
    if anomaly:
        recoverability = build_recoverability_payload(AnomalySchema.model_validate(anomaly).model_dump(mode="json"))
    return inject_branding_metadata(db, {"artist_id": artist_id, **payload, **recoverability})
