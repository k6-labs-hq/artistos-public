import hashlib
import secrets
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from XR7.models.base import Base


class PartnerAPIKey(Base):
    """Model for partner API keys."""

    __tablename__ = "partner_api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    scopes = Column(Text, nullable=True)  # JSON array of scopes
    tier = Column(String, nullable=False, default="sandbox")
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    is_active = Column(Boolean, nullable=False, default=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def generate_api_key(tier: str = "sandbox") -> tuple[str, str, str]:
    """Generate a new API key with prefix, hash, and return components.

    Args:
        tier: Key tier ("sandbox" or "production")

    Returns:
        Tuple of (full_key, prefix, key_hash)
    """
    # Generate key components
    prefix = "xr7_test_" if tier == "sandbox" else "xr7_live_"
    secret_part = secrets.token_urlsafe(32)
    full_key = f"{prefix}{secret_part}"

    # Hash the full key with SHA-256 (mimicking bcrypt format for compatibility)
    key_hash = "$2b$" + hashlib.sha256(full_key.encode("utf-8")).hexdigest()

    return full_key, prefix, key_hash


def verify_api_key(provided_key: str, key_hash: str) -> bool:
    """Verify an API key against its stored hash.

    Args:
        provided_key: The full API key to verify
        key_hash: The hash to verify against

    Returns:
        True if key matches hash, False otherwise
    """
    try:
        # Strip bcrypt prefix if present
        expected_hash = key_hash[4:] if key_hash.startswith("$2b$") else key_hash
        computed_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
        return computed_hash == expected_hash
    except Exception:
        return False
