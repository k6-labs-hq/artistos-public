"""Notification Delivery Log — persisted row per send attempt.

Every call to send_event_notification that reaches the dispatch stage writes
a row here, regardless of outcome.  This satisfies the backlog acceptance
signal: "Delivery events persisted for auditability."
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    event_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String, nullable=False)  # "sms" | "email"
    recipient: Mapped[str | None] = mapped_column(String, nullable=True)
    sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # skip_reason is set when sent=False (e.g. "quiet_hours", "event_disabled")
    skip_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    rendered_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    rendered_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    org_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class NotificationDeliveryLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str | None
    event_key: str
    channel: str
    recipient: str | None
    sent: bool
    skip_reason: str | None
    rendered_title: str | None
    rendered_body: str | None
    org_id: str | None
    created_at: datetime
