from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)

    notify_anomaly_detected: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_urgent_sol: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_deposit_received: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_claim_advanced: Mapped[bool] = mapped_column(Boolean, default=True)

    quiet_hours_start: Mapped[str | None] = mapped_column(String, nullable=True)
    quiet_hours_end: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class NotificationPreferenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    email: str | None = None
    phone: str | None = None
    notify_anomaly_detected: bool
    notify_urgent_sol: bool
    notify_deposit_received: bool
    notify_claim_advanced: bool
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    created_at: datetime
    updated_at: datetime


class NotificationPreferenceUpsert(BaseModel):
    email: str | None = None
    phone: str | None = None
    notify_anomaly_detected: bool = True
    notify_urgent_sol: bool = True
    notify_deposit_received: bool = True
    notify_claim_advanced: bool = True
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
