from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class OAuthSessionStatus(str, enum.Enum):
    PENDING = "pending"
    EXCHANGED = "exchanged"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ConnectorAccountStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"


class OAuthConnectorSession(Base):
    __tablename__ = "oauth_connector_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    redirect_uri: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    requested_scopes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    status: Mapped[str] = mapped_column(
        Enum(OAuthSessionStatus), nullable=False, default=OAuthSessionStatus.PENDING
    )
    created_by_email: Mapped[str | None] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class ConnectorAccountLink(Base):
    __tablename__ = "connector_account_links"
    __table_args__ = (
        UniqueConstraint(
            "artist_id",
            "provider",
            "tenant_id",
            "external_account_id",
            name="uq_connector_account_artist_provider_tenant_external",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    external_account_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    granted_scopes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_type: Mapped[str] = mapped_column(String, nullable=False, default="Bearer")
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_refreshed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ConnectorAccountStatus), nullable=False, default=ConnectorAccountStatus.ACTIVE
    )
    created_by_email: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class OAuthConnectorSessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    provider: str
    redirect_uri: str
    state: str
    requested_scopes: str
    tenant_id: str
    status: OAuthSessionStatus
    created_by_email: str | None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class ConnectorAccountLinkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    provider: str
    tenant_id: str
    external_account_id: str
    display_name: str | None
    profile_metadata_json: str
    granted_scopes: str
    token_type: str
    token_expires_at: datetime | None
    last_refreshed_at: datetime | None
    status: ConnectorAccountStatus
    created_by_email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OAuthSessionCreateRequest(BaseModel):
    provider: str
    redirect_uri: str
    scopes: list[str] = Field(default_factory=list)
    tenant_id: str = "default"


class OAuthTokenExchangeRequest(BaseModel):
    state: str
    code: str
    external_account_id: str
    tenant_id: str = "default"
    granted_scopes: list[str] | None = None
    allow_partial_scope_grant: bool = False
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in_seconds: int | None = 3600
    display_name: str | None = None
    profile_metadata: dict[str, str] | None = None


class OAuthTokenRefreshRequest(BaseModel):
    rotate_refresh_token: bool = False
    expires_in_seconds: int = 3600
    force: bool = False
