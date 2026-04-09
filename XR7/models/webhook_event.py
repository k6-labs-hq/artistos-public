"""Webhook Event Inbox — stores inbound webhook payloads for replay.

A signed payload is written here on receipt.  If processing fails the
row stays in status=FAILED and can be replayed via the admin endpoint.
"""
from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class WebhookEventStatus(str):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    REPLAYING = "REPLAYING"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    raw_payload: Mapped[str] = mapped_column(Text, nullable=False)
    # HMAC-SHA256 of raw_payload with the webhook secret
    signature: Mapped[str | None] = mapped_column(String, nullable=True)
    signature_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=WebhookEventStatus.PENDING, index=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class WebhookEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    source: str
    event_type: str
    raw_payload: str
    signature: str | None
    signature_verified: bool
    status: str
    processing_error: str | None
    attempts: int
    processed_at: datetime | None
    created_at: datetime
    updated_at: datetime


def verify_webhook_signature(payload: str, secret: str, provided_sig: str) -> bool:
    """Constant-time HMAC-SHA256 comparison."""
    expected = hmac.new(
        secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, provided_sig)
