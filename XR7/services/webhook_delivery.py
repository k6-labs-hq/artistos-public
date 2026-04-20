"""Outbound webhook delivery service.

Manages webhook event queue and delivery for notifying external systems
about events (e.g., payment received, claim status changed).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class OutboundWebhookService:
    """Service for queuing and managing outbound webhook events.
    
    Usage::
    
        service = OutboundWebhookService(db)
        
        event = service.queue_event(
            event_type="claim.status_changed",
            payload={
                "claim_id": "clm_abc123",
                "artist_id": "art_xyz789",
                "status": "FILED",
            },
        )
        
        # Trigger async delivery
        deliver_webhook_event.delay(event.id)
    """
    
    def __init__(self, db: Session) -> None:
        """Initialize webhook service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def queue_event(
        self,
        event_type: str,
        payload: dict,
        artist_id: str | None = None,
    ) -> WebhookEvent:
        """Queue a webhook event for delivery.
        
        Creates a WebhookEvent record in PENDING status. The event will be
        picked up by the deliver_webhook_event Celery task for async delivery.
        
        Args:
            event_type: Event type (e.g., "claim.status_changed", "payment.received")
            payload: Event payload data (must be JSON-serializable)
            artist_id: Optional artist ID (extracted from payload if not provided)
        
        Returns:
            Created WebhookEvent instance
        
        Example::
        
            event = service.queue_event(
                event_type="payment.received",
                payload={
                    "payment_id": "pmt_xyz",
                    "artist_id": "art_abc",
                    "amount": 150.00,
                    "currency": "USD",
                }
            )
        """
        # Extract artist_id from payload if not provided
        if artist_id is None:
            artist_id = payload.get("artist_id")
        
        # Create webhook event record
        event = WebhookEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            payload=payload,
            artist_id=artist_id,
            status=WebhookEventStatus.PENDING,
            created_at=datetime.utcnow(),
            processing_error=None,
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        logger.info(
            "webhook_event_queued",
            extra={
                "event_id": event.id,
                "event_type": event_type,
                "artist_id": artist_id,
            },
        )
        
        return event
    
    def get_event(self, event_id: str) -> WebhookEvent | None:
        """Get webhook event by ID.
        
        Args:
            event_id: Webhook event ID
        
        Returns:
            WebhookEvent or None if not found
        """
        return (
            self.db.query(WebhookEvent)
            .filter(WebhookEvent.id == event_id)
            .first()
        )
    
    def list_events(
        self,
        artist_id: str | None = None,
        status: WebhookEventStatus | None = None,
        limit: int = 100,
    ) -> list[WebhookEvent]:
        """List webhook events with optional filtering.
        
        Args:
            artist_id: Filter by artist ID
            status: Filter by event status
            limit: Maximum number of events to return
        
        Returns:
            List of WebhookEvent instances
        """
        query = self.db.query(WebhookEvent)
        
        if artist_id:
            query = query.filter(WebhookEvent.artist_id == artist_id)
        
        if status:
            query = query.filter(WebhookEvent.status == status)
        
        return query.order_by(WebhookEvent.created_at.desc()).limit(limit).all()
    
    def retry_failed_event(self, event_id: str) -> WebhookEvent | None:
        """Reset a failed event to PENDING for retry.
        
        Args:
            event_id: Webhook event ID to retry
        
        Returns:
            Updated WebhookEvent or None if not found
        """
        event = self.get_event(event_id)
        
        if not event:
            logger.warning("retry_failed_event_not_found", extra={"event_id": event_id})
            return None
        
        if event.status != WebhookEventStatus.FAILED:
            logger.warning(
                "retry_event_wrong_status",
                extra={"event_id": event_id, "status": event.status},
            )
            return event
        
        event.status = WebhookEventStatus.PENDING
        event.processing_error = None
        self.db.commit()
        self.db.refresh(event)
        
        logger.info("webhook_event_retry_queued", extra={"event_id": event_id})
        
        return event
