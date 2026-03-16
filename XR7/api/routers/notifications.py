from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.notification_preference import NotificationPreference, NotificationPreferenceSchema
from XR7.notifications.push_voice import register_push_token, voice_balance_query
from XR7.earnings.dashboard import DashboardEngine

router = APIRouter(tags=["notifications"])


class NotificationPreferenceRequest(BaseModel):
    email: str | None = None
    phone: str | None = None
    notify_anomaly_detected: bool = True
    notify_urgent_sol: bool = True
    notify_deposit_received: bool = True
    notify_claim_advanced: bool = True
    quiet_hours_start: int = 22
    quiet_hours_end: int = 7


@router.post("/artists/{artist_id}/notifications/preferences", response_model=NotificationPreferenceSchema)
def set_notification_preferences(artist_id: str, payload: NotificationPreferenceRequest, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    row = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()
    if not row:
        row = NotificationPreference(artist_id=artist_id)
        db.add(row)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


@router.post("/artists/{artist_id}/notifications/dispatch")
def dispatch_notifications(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return {
        "artist_id": artist_id,
        "channels": ["twilio_sms", "smtp_email"],
        "status": "queued",
    }


@router.post("/artists/{artist_id}/notifications/push-register")
def push_register(artist_id: str, token: str, platform: str = "firebase", db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return register_push_token(artist_id, token, platform)


@router.post("/artists/{artist_id}/notifications/voice-query")
def voice_query(artist_id: str, question: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    dashboard = DashboardEngine(db).compute(artist_id)
    return voice_balance_query(artist_id, question, dashboard)
