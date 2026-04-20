"""Platform OAuth credential model for semi-automated data ingestion.

Feature #7: Semi-automated pull fallbacks

Stores OAuth credentials with encryption for secure platform API access.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class PlatformOAuthStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


class PlatformOAuthCredential(Base):
    """OAuth credentials for platform API access with token rotation."""
    
    __tablename__ = "platform_oauth_credentials"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)  # spotify, youtube, soundcloud
    
    # OAuth tokens (encrypted at rest in production)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Scope and metadata
    scopes: Mapped[list] = mapped_column(String, nullable=False, default="[]")  # JSON array
    status: Mapped[str] = mapped_column(
        Enum(PlatformOAuthStatus),
        nullable=False,
        default=PlatformOAuthStatus.ACTIVE,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PlatformOAuthCredentialSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    artist_id: str
    platform: str
    expires_at: datetime | None
    scopes: str  # JSON string
    status: PlatformOAuthStatus
    created_at: datetime
