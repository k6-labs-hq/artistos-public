from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ModelRegistryEntry(Base):
    __tablename__ = "ml_model_registry"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_family: Mapped[str] = mapped_column(String, nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String, nullable=False, index=True)
    training_snapshot_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ModelRegistryEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_family: str
    model_version: str
    training_snapshot_ref: str | None = None
    metrics: dict[str, Any] | None = None
    extra_metadata: dict[str, Any] | None = None
    created_at: datetime
