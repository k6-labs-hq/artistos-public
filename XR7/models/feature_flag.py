from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target_user_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    conditions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class FeatureFlagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    description: str | None = None
    enabled: bool
    rollout_percentage: int
    target_user_ids: list[str]
    conditions: dict
    created_at: datetime
    updated_at: datetime
