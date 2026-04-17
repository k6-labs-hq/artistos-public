from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session

from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus

_DEFAULT_SECRET = os.getenv("XR7_OUTBOUND_WEBHOOK_SECRET", "")
_DEFAULT_ENDPOINT = os.getenv("XR7_OUTBOUND_WEBHOOK_URL", "")


class OutboundWebhookService:
    """Publishes outbound webhook events with HMAC signing and retry metadata."""

    def __init__(self, db: Session, *, secret: str | None = None, endpoint: str | None = None) -> None:
        self.db = db
        self.secret = (secret if secret is not None else _DEFAULT_SECRET).strip()
        self.endpoint = (endpoint if endpoint is not None else _DEFAULT_ENDPOINT).strip()

    def _sign(self, payload: str) -> str:
        return hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def queue_event(self, *, event_type: str, payload: dict[str, Any], source: str = "xr7") -> WebhookEvent:
        raw_payload = json.dumps(payload, default=str, sort_keys=True)
        signature = self._sign(raw_payload) if self.secret else None
        row = WebhookEvent(
            source=source,
            event_type=event_type,
            raw_payload=raw_payload,
            signature=signature,
            signature_verified=bool(signature),
            status=WebhookEventStatus.PENDING,
            attempts=0,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def deliver_event(self, row: WebhookEvent) -> bool:
        if not self.endpoint:
            row.status = WebhookEventStatus.FAILED
            row.processing_error = "XR7_OUTBOUND_WEBHOOK_URL is not configured"
            row.attempts += 1
            self.db.commit()
            return False

        headers = {"Content-Type": "application/json"}
        if row.signature:
            headers["X-XR7-Signature"] = row.signature
            headers["X-XR7-Event-Type"] = row.event_type

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.endpoint, content=row.raw_payload.encode("utf-8"), headers=headers)
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            row.status = WebhookEventStatus.FAILED
            row.processing_error = str(exc)
            row.attempts += 1
            self.db.commit()
            return False

        row.status = WebhookEventStatus.PROCESSED
        row.processing_error = None
        row.attempts += 1
        row.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
