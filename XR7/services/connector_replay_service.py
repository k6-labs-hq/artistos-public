"""Connector replay service — HMAC verification + event replay."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from XR7.models.connector_sync_cursor import ConnectorSyncCursor
from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus


def verify_hmac_signature(payload: str, secret: str, provided_sig: str) -> bool:
    """HMAC-SHA256 constant-time comparison.  Returns False when secret is empty."""
    if not secret:
        return False
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided_sig)


def ingest_webhook(
    *,
    source: str,
    event_type: str,
    raw_payload: str,
    signature: str | None,
    secret: str | None,
    db: Session,
) -> WebhookEvent:
    """Persist an inbound webhook and verify the HMAC (if secret is configured)."""
    verified = False
    if secret and signature:
        verified = verify_hmac_signature(raw_payload, secret, signature)

    event = WebhookEvent(
        source=source,
        event_type=event_type,
        raw_payload=raw_payload,
        signature=signature,
        signature_verified=verified,
        status=WebhookEventStatus.PENDING,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def mark_event_processed(event_id: str, db: Session) -> WebhookEvent:
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if not event:
        raise ValueError(f"WebhookEvent {event_id} not found")
    event.status = WebhookEventStatus.PROCESSED
    event.processed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return event


def mark_event_failed(event_id: str, error: str, db: Session) -> WebhookEvent:
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if not event:
        raise ValueError(f"WebhookEvent {event_id} not found")
    event.status = WebhookEventStatus.FAILED
    event.processing_error = error
    event.attempts += 1
    db.commit()
    db.refresh(event)
    return event


def replay_event(event_id: str, db: Session) -> WebhookEvent:
    """Reset a FAILED event to REPLAYING so downstream processors re-pick it up."""
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if not event:
        raise ValueError(f"WebhookEvent {event_id} not found")
    if event.status not in (WebhookEventStatus.FAILED, WebhookEventStatus.PROCESSED):
        raise ValueError(f"Cannot replay event in status {event.status}")
    event.status = WebhookEventStatus.REPLAYING
    event.processing_error = None
    event.attempts += 1
    db.commit()
    db.refresh(event)
    return event


def get_failed_events(source: str | None, db: Session, limit: int = 50) -> List[WebhookEvent]:
    q = db.query(WebhookEvent).filter(WebhookEvent.status == WebhookEventStatus.FAILED)
    if source:
        q = q.filter(WebhookEvent.source == source)
    return q.order_by(WebhookEvent.created_at.desc()).limit(limit).all()


def upsert_sync_cursor(
    *,
    artist_id: str,
    integration: str,
    cursor_value: str,
    db: Session,
) -> ConnectorSyncCursor:
    cursor = (
        db.query(ConnectorSyncCursor)
        .filter(
            ConnectorSyncCursor.artist_id == artist_id,
            ConnectorSyncCursor.integration == integration,
        )
        .first()
    )
    if cursor:
        cursor.cursor_value = cursor_value
        cursor.last_successful_fetch_at = datetime.now(timezone.utc)
        cursor.fetch_count = str(int(cursor.fetch_count or "0") + 1)
    else:
        cursor = ConnectorSyncCursor(
            artist_id=artist_id,
            integration=integration,
            cursor_value=cursor_value,
            last_successful_fetch_at=datetime.now(timezone.utc),
            fetch_count="1",
        )
        db.add(cursor)
    db.commit()
    db.refresh(cursor)
    return cursor
