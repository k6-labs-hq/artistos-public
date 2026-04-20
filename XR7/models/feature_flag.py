"""Feature flag model for runtime configuration and gradual rollouts.

Feature flags enable/disable features dynamically without deployments.
Supports percentage-based rollouts, user targeting, and conditional activation.
"""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class FeatureFlag(Base):
    """Feature flag for runtime feature toggling.

    Enables gradual rollouts, A/B testing, and kill switches without deployments.
    """

    __tablename__ = "feature_flags"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    # Configuration
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Gradual rollout (0-100)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Targeting
    target_user_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    conditions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<FeatureFlag(key={self.key}, enabled={self.enabled}, "
            f"rollout={self.rollout_percentage}%)>"
        )


class FeatureFlagSchema(BaseModel):
    """Pydantic schema for FeatureFlag serialization."""

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
