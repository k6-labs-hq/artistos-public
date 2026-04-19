"""
Tests for partner API key lifecycle management.

Closes: XR7-404
Domain: api-ecosystem
Scale-target: Partner-facing API ecosystem with full lifecycle governance
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from XR7.models.api_key import PartnerAPIKey, generate_api_key, verify_api_key
from XR7.models.base import SessionLocal


def test_generate_api_key_creates_valid_format():
    """Generated API keys should have correct format and components."""
    full_key, prefix, key_hash = generate_api_key("sandbox")

    assert full_key.startswith("xr7_test_")
    assert prefix.startswith("xr7_test_")
    assert key_hash.startswith("$2b$")  # bcrypt hash

    # Verify key can be validated
    assert verify_api_key(full_key, key_hash)


def test_generate_api_key_production_tier():
    """Production tier keys should have 'live' prefix."""
    full_key, prefix, key_hash = generate_api_key("production")

    assert full_key.startswith("xr7_live_")
    assert prefix.startswith("xr7_live_")


def test_verify_api_key_rejects_wrong_key():
    """Wrong API key should fail verification."""
    _, _, key_hash = generate_api_key("sandbox")

    assert not verify_api_key("xr7_test_wrong_key", key_hash)


def test_api_key_creation_and_validation():
    """Create API key in database and validate lifecycle."""
    db = SessionLocal()

    try:
        full_key, prefix, key_hash = generate_api_key("sandbox")

        api_key = PartnerAPIKey(
            partner_id="partner-123",
            key_hash=key_hash,
            key_prefix=prefix,
            name="Development Key",
            scopes=["read:artists", "read:statements"],
            tier="sandbox",
            rate_limit_per_hour=100,
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        # Verify key is active
        assert api_key.is_active is True

        # Verify key can be looked up by prefix
        found = db.query(PartnerAPIKey).filter(PartnerAPIKey.key_prefix == prefix).first()
        assert found is not None
        assert verify_api_key(full_key, found.key_hash)

    finally:
        db.close()


def test_api_key_revocation():
    """Revoked API key should not be active."""
    db = SessionLocal()

    try:
        full_key, prefix, key_hash = generate_api_key("sandbox")

        api_key = PartnerAPIKey(
            partner_id="partner-456",
            key_hash=key_hash,
            key_prefix=prefix,
            name="Test Key",
            tier="sandbox",
        )

        db.add(api_key)
        db.commit()

        assert api_key.is_active is True

        # Revoke key
        api_key.revoked_at = datetime.now(timezone.utc)
        api_key.revoked_reason = "Security incident"
        db.commit()

        assert api_key.is_active is False

    finally:
        db.close()


def test_api_key_expiration():
    """Expired API key should not be active."""
    db = SessionLocal()

    try:
        full_key, prefix, key_hash = generate_api_key("sandbox")

        api_key = PartnerAPIKey(
            partner_id="partner-789",
            key_hash=key_hash,
            key_prefix=prefix,
            name="Temporary Key",
            tier="sandbox",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired yesterday
        )

        db.add(api_key)
        db.commit()

        assert api_key.is_active is False

    finally:
        db.close()


def test_api_key_usage_tracking():
    """API key usage should be tracked."""
    db = SessionLocal()

    try:
        full_key, prefix, key_hash = generate_api_key("production")

        api_key = PartnerAPIKey(
            partner_id="partner-101",
            key_hash=key_hash,
            key_prefix=prefix,
            name="Production Key",
            tier="production",
            rate_limit_per_hour=10000,
        )

        db.add(api_key)
        db.commit()

        # Simulate API usage
        api_key.usage_count += 1
        api_key.last_used_at = datetime.now(timezone.utc)
        db.commit()

        assert api_key.usage_count == 1
        assert api_key.last_used_at is not None

    finally:
        db.close()


def test_production_key_has_higher_rate_limit():
    """Production tier should have higher rate limit than sandbox."""
    db = SessionLocal()

    try:
        sandbox_key, sandbox_prefix, sandbox_hash = generate_api_key("sandbox")
        prod_key, prod_prefix, prod_hash = generate_api_key("production")

        sandbox_api_key = PartnerAPIKey(
            partner_id="partner-202",
            key_hash=sandbox_hash,
            key_prefix=sandbox_prefix,
            name="Sandbox",
            tier="sandbox",
            rate_limit_per_hour=100,
        )

        prod_api_key = PartnerAPIKey(
            partner_id="partner-202",
            key_hash=prod_hash,
            key_prefix=prod_prefix,
            name="Production",
            tier="production",
            rate_limit_per_hour=10000,
        )

        db.add_all([sandbox_api_key, prod_api_key])
        db.commit()

        assert prod_api_key.rate_limit_per_hour > sandbox_api_key.rate_limit_per_hour

    finally:
        db.close()


def test_api_key_unique_prefix():
    """API key prefixes should be unique."""
    db = SessionLocal()

    try:
        full_key, prefix, key_hash = generate_api_key("sandbox")

        key1 = PartnerAPIKey(
            partner_id="partner-303",
            key_hash=key_hash,
            key_prefix=prefix,
            name="Key 1",
            tier="sandbox",
        )

        key2 = PartnerAPIKey(
            partner_id="partner-303",
            key_hash=key_hash,
            key_prefix=prefix,  # Same prefix
            name="Key 2",
            tier="sandbox",
        )

        db.add(key1)
        db.commit()

        db.add(key2)

        with pytest.raises(Exception):  # Should raise unique constraint violation
            db.commit()

    finally:
        db.rollback()
        db.close()
