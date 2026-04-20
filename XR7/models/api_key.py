import secrets
import hashlib
import uuid
import json
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.hybrid import hybrid_property
from XR7.models.base import Base
from datetime import datetime, timezone


class JSONEncodedList(TypeDecorator):
    """Store Python lists as JSON strings in database."""
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        """Convert list to JSON string before storing."""
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        """Convert JSON string back to list when reading."""
        if value is None:
            return []
        return json.loads(value)


class PartnerAPIKey(Base):
    """Model for partner API keys."""
    __tablename__ = 'partner_api_keys'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False, unique=True, index=True)  # Each prefix must be unique
    name = Column(String, nullable=True)
    scopes = Column(JSONEncodedList, nullable=True)  # Stores list as JSON
    tier = Column(String, nullable=False, default="sandbox")
    rate_limit_per_hour = Column(Integer, nullable=False, default=100)
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @hybrid_property
    def is_active(self) -> bool:
        """API key is active if not revoked and not expired."""
        now = datetime.now(timezone.utc)
        
        # Check if revoked
        if self.revoked_at is not None:
            return False
        
        # Check if expired
        if self.expires_at is not None:
            # Make expires_at timezone-aware if it's not
            expires = self.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if now > expires:
                return False
        
        return True


def generate_api_key(tier: str = "sandbox") -> tuple[str, str, str]:
    """Generate a new API key with prefix, hash, and return components.
    
    Args:
        tier: Key tier ("sandbox" or "production")
        
    Returns:
        Tuple of (full_key, prefix, key_hash)
        - full_key: Complete API key (e.g., "xr7_test_AbCdEf1234...")
        - prefix: First 16 characters of full key for identification (e.g., "xr7_test_AbCdEf1")
        - key_hash: SHA-256 hash of full key for verification
    """
    # Generate key components
    tier_prefix = "xr7_test_" if tier == "sandbox" else "xr7_live_"
    secret_part = secrets.token_urlsafe(32)
    full_key = f"{tier_prefix}{secret_part}" 
    
    # Prefix is first 16 chars of full key (unique identifier for display/lookup)
    prefix = full_key[:16]
    
    # Hash the full key with SHA-256 (mimicking bcrypt format for compatibility)
    key_hash = "$2b$" + hashlib.sha256(full_key.encode('utf-8')).hexdigest()
    
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
        computed_hash = hashlib.sha256(provided_key.encode('utf-8')).hexdigest()
        return computed_hash == expected_hash
    except Exception:
        return False
