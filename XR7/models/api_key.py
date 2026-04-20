"""
Partner API Key model for API ecosystem lifecycle management.

Enables partners to generate scoped API keys with tiered rate limits,
rotation support, usage tracking, and revocation.

Tiers:
- **sandbox**: 100 requests/hour for development/testing
- **production**: 10,000 requests/hour for live integrations

Closes: XR7-404
Domain: api-ecosystem
Scale-target: Partner-facing API ecosystem with full lifecycle governance
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

import bcrypt
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class PartnerAPIKey(Base):
    """Partner API key for secure third-party integrations."""

    __tablename__ = "partner_api_keys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String, nullable=False)
    key_prefix: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )  # xr7_live_abc...
    name: Mapped[str] = mapped_column(String, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tier: Mapped[str] = mapped_column(String, nullable=False, default="sandbox")
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    usage_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    @property
    def is_active(self) -> bool:
        """Check if API key is currently active."""
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at < datetime.now(timezone.utc):
            return False
        return True


class PartnerAPIKeySchema(BaseModel):
    """Pydantic schema for API key (without exposing hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    partner_id: str
    key_prefix: str
    name: str
    scopes: list[str]
    tier: str
    rate_limit_per_hour: int
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None
    revoked_at: datetime | None
    revoked_reason: str | None
    usage_count: int
    is_active: bool


def generate_api_key(tier: str = "sandbox") -> tuple[str, str, str]:
    """Generate a secure API key with prefix and hash.

    Args:
        tier: API key tier (sandbox or production)

    Returns:
        Tuple of (full_key, key_prefix, key_hash)
            - full_key: The actual key to give to partner (show once)
            - key_prefix: Identifier for the key (xr7_{tier}_{prefix})
            - key_hash: bcrypt hash to store in database

    Example:
        >>> full_key, prefix, hash = generate_api_key("production")
        >>> # full_key = "xr7_live_abc123_xyz789pqr456..."
        >>> # prefix = "xr7_live_abc123"
        >>> # hash = "$2b$12$..."
    """
    # Generate 32-byte random key
    key_secret = secrets.token_urlsafe(32)

    # Create prefix based on tier
    tier_prefix = "test" if tier == "sandbox" else "live"
    random_prefix = secrets.token_urlsafe(6)[:8]
    key_prefix = f"xr7_{tier_prefix}_{random_prefix}"

    # Full key format: {prefix}_{secret}
    full_key = f"{key_prefix}_{key_secret}"

    # Hash the full key for storage
    key_hash = bcrypt.hashpw(full_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    return full_key, key_prefix, key_hash


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Verify API key against stored hash.

    Args:
        provided_key: The API key provided by the partner
        stored_hash: The bcrypt hash stored in the database

    Returns:
        True if key matches hash, False otherwise
    """
    try:
        return bcrypt.checkpw(provided_key.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        return False
