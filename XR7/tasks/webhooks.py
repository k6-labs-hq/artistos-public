from __future__ import annotations

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus
from XR7.services.webhook_delivery import OutboundWebhookService


@celery_app.task(
    name="xr7.webhooks.deliver",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def deliver_webhook_event(self, webhook_event_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        row = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_event_id).first()
        if not row:
            raise ValueError("webhook event not found")
        service = OutboundWebhookService(db)
        ok = service.deliver_event(row)
        return {"webhook_event_id": webhook_event_id, "status": row.status, "delivered": ok}
    finally:
        db.close()


@celery_app.task(name="xr7.webhooks.redeliver_failed")
def redeliver_failed_webhooks() -> dict:
    db = SessionLocal()
    try:
        rows = (
            db.query(WebhookEvent)
            .filter(WebhookEvent.status == WebhookEventStatus.FAILED)
            .order_by(WebhookEvent.created_at.asc())
            .limit(100)
            .all()
        )
        count = 0
        for row in rows:
            deliver_webhook_event.delay(row.id)
            count += 1
        return {"queued": count}
    finally:
        db.close()
