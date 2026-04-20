"""Webhook delivery Celery tasks.

Handles asynchronous webhook event delivery with retries and failure tracking.
"""

from sqlalchemy.orm import Session

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus
from xr7_common.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(Exception,),
)
def deliver_webhook_event(self, event_id: str) -> dict:
    """Deliver a webhook event to its registered endpoint.
    
    Args:
        event_id: WebhookEvent ID to deliver
    
    Returns:
        Status dict with delivery outcome
    
    Raises:
        Retries automatically on failure up to max_retries
    """
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        
        if not event:
            logger.error(f"Webhook event {event_id} not found")
            return {"status": "error", "message": "Event not found"}
        
        try:
            # TODO: Implement actual HTTP delivery when webhook infrastructure is ready
            # Current implementation: Stub mode for development
            
            # Production implementation would:
            # 1. Extract webhook URL from event.webhook_url or event.subscription
            # 2. Sign payload with HMAC-SHA256 secret
            # 3. POST event.payload to webhook URL with retry logic
            # 4. Validate response status (200-299 = success)
            # 5. Update event status and response metadata
            
            logger.info(
                "[STUB] Webhook delivery simulated",
                extra={
                    "event_id": event_id,
                    "event_type": event.event_type if hasattr(event, 'event_type') else None,
                    "status": event.status,
                }
            )
            
            # Mark as delivered in stub mode
            event.status = WebhookEventStatus.DELIVERED
            event.processing_error = None
            db.commit()
            
            return {
                "status": "delivered",
                "event_id": event_id,
                "delivery_mode": "stub",
            }
            
        except Exception as exc:
            # Log failure and update event status
            logger.error(
                f"Webhook delivery failed: {exc}",
                extra={"event_id": event_id, "error": str(exc)},
            )
            
            event.status = WebhookEventStatus.FAILED
            event.processing_error = str(exc)[:500]  # Truncate long errors
            db.commit()
            
            # Celery will retry automatically
            raise
    finally:
        db.close()


@celery_app.task
def deliver_webhook_batch(event_ids: list[str]) -> dict:
    """Deliver multiple webhook events in batch.
    
    Args:
        event_ids: List of WebhookEvent IDs
    
    Returns:
        Summary of delivery outcomes
    """
    results = {
        "total": len(event_ids),
        "delivered": 0,
        "failed": 0,
        "not_found": 0,
    }
    
    for event_id in event_ids:
        try:
            outcome = deliver_webhook_event.apply(args=[event_id])
            if outcome.get("status") == "delivered":
                results["delivered"] += 1
            elif outcome.get("status") == "error":
                results["not_found"] += 1
            else:
                results["failed"] += 1
        except Exception as exc:
            logger.error(f"Batch delivery failed for {event_id}: {exc}")
            results["failed"] += 1
    
    return results
