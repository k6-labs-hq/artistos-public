from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.earnings.dashboard import DashboardEngine
from XR7.models.base import get_db
from XR7.models.notification_delivery_log import (
    NotificationDeliveryLog,
    NotificationDeliveryLogSchema,
)
from XR7.models.notification_preference import NotificationPreference, NotificationPreferenceSchema
from XR7.notifications.push_voice import register_push_token, voice_balance_query
from XR7.services.branding import (
    apply_brand_placeholders,
    branding_metadata,
    communication_templates,
    get_branding_for_artist,
    inject_branding_metadata,
)

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
    get_artist_or_404(artist_id, db)
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
    get_artist_or_404(artist_id, db)
    brand = get_branding_for_artist(db, artist_id)
    templates = communication_templates()
    return {
        "artist_id": artist_id,
        "channels": ["twilio_sms", "smtp_email"],
        "status": "queued",
        "branding": branding_metadata(brand),
        "templates": templates,
        "rendered_templates": apply_brand_placeholders(templates, brand),
    }


@router.post("/artists/{artist_id}/notifications/push-register")
def push_register(artist_id: str, token: str, platform: str = "firebase", db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    out = register_push_token(artist_id, token, platform)
    brand = get_branding_for_artist(db, artist_id)
    return {
        **out,
        "push_sender_name": brand.get("display_name"),
        "branding": branding_metadata(brand),
    }


@router.post("/artists/{artist_id}/notifications/voice-query")
def voice_query(artist_id: str, question: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    dashboard = DashboardEngine(db).compute(artist_id)
    result = voice_balance_query(artist_id, question, dashboard)
    if isinstance(result, dict):
        return inject_branding_metadata(db, {"artist_id": artist_id, **result})
    return inject_branding_metadata(db, {"artist_id": artist_id, "response": result})


@router.get(
    "/artists/{artist_id}/notifications/delivery-log",
    response_model=List[NotificationDeliveryLogSchema],
    summary="List notification delivery log for an artist",
)
def get_delivery_log(
    artist_id: str,
    event_key: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return persisted delivery log rows for audit and debugging."""
    q = db.query(NotificationDeliveryLog).filter(
        NotificationDeliveryLog.artist_id == artist_id
    )
    if event_key:
        q = q.filter(NotificationDeliveryLog.event_key == event_key)
    return (
        q.order_by(NotificationDeliveryLog.created_at.desc()).limit(limit).all()
    )
