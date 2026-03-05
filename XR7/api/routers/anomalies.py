from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.anomaly.engine import AnomalyEngine
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.models.anomaly import Anomaly, AnomalySchema, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import get_db

router = APIRouter(tags=["anomalies"])


@router.get("/artists/{artist_id}/anomalies")
def list_anomalies(artist_id: str, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if status:
        query = query.filter(Anomaly.status == status)
    return query.all()


@router.get("/anomalies/{anomaly_id}", response_model=AnomalySchema)
def get_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly


@router.post("/artists/{artist_id}/anomalies/detect")
def detect_anomalies(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    rg = RightsGraph()
    engine = AnomalyEngine(EarningsEngine(rg), rg)
    anomaly_dicts = engine.detect_all(artist_id, db)
    return {"artist_id": artist_id, "detected": anomaly_dicts}
