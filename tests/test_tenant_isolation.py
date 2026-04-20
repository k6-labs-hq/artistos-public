"""
Tests for multi-tenant write operation isolation enforcement.

Verifies that write operations (INSERT/UPDATE/DELETE) cannot cross tenant
boundaries, preventing data corruption and compliance violations.

Closes: XR7-403
Domain: security
Scale-target: 10x tenant count with strict data plane isolation
Compliance: SOC 2 CC6.7 — Logical access controls (tenant isolation)
GDPR: Art. 32 — Security of processing (organizational measures)
"""

from __future__ import annotations

import pytest

from XR7.exceptions import TenantIsolationViolation
from XR7.models.base import SessionLocal
from XR7.models.oauth_connector import OAuthConnectorAccount
from XR7.services.tenant_context import reset_tenant_context, set_tenant_context


@pytest.fixture
def db_session():
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def tenant_a_context():
    """Set tenant context to tenant-a."""
    tokens = set_tenant_context("tenant-a", "user-alice")
    yield
    reset_tenant_context(tokens)


@pytest.fixture
def tenant_b_context():
    """Set tenant context to tenant-b."""
    tokens = set_tenant_context("tenant-b", "user-bob")
    yield
    reset_tenant_context(tokens)


@pytest.fixture
def no_tenant_context():
    """Clear tenant context (e.g., system operations)."""
    tokens = set_tenant_context("", "")
    yield
    reset_tenant_context(tokens)


def test_insert_auto_injects_tenant_id(db_session, tenant_a_context):
    """INSERT should auto-inject tenant_id from context."""
    account = OAuthConnectorAccount(
        id="test-account-1",
        provider="google",
        external_account_id="alice@example.com",
        artist_id="artist-1",
        # tenant_id intentionally omitted
    )

    db_session.add(account)
    db_session.flush()

    # Verify tenant_id was auto-injected
    assert account.tenant_id == "tenant-a"


def test_insert_with_wrong_tenant_id_raises(db_session, tenant_a_context):
    """INSERT with explicit wrong tenant_id should raise exception."""
    account = OAuthConnectorAccount(
        id="test-account-2",
        provider="google",
        external_account_id="bob@example.com",
        artist_id="artist-2",
        tenant_id="tenant-b",  # Wrong tenant!
    )

    db_session.add(account)

    with pytest.raises(TenantIsolationViolation) as exc_info:
        db_session.flush()

    assert exc_info.value.current_tenant == "tenant-a"
    assert exc_info.value.target_tenant == "tenant-b"
    assert exc_info.value.operation == "INSERT"
    assert "OAuthConnectorAccount" in exc_info.value.model


def test_update_cross_tenant_record_raises(db_session, tenant_a_context, tenant_b_context):
    """UPDATE on record from another tenant should raise exception."""
    # Create record as tenant-a
    account = OAuthConnectorAccount(
        id="test-account-3",
        provider="google",
        external_account_id="alice@example.com",
        artist_id="artist-3",
    )
    db_session.add(account)
    db_session.flush()
    db_session.commit()

    # Switch to tenant-b and try to update
    reset_tenant_context((None, None))
    tokens_b = set_tenant_context("tenant-b", "user-bob")

    try:
        # Query will auto-filter by tenant, so manually attach object
        account_to_update = db_session.get(OAuthConnectorAccount, "test-account-3")

        if account_to_update is None:
            # Expected: query filtered it out due to tenant mismatch
            # Try to force-load and update anyway
            account_to_update = OAuthConnectorAccount(
                id="test-account-3",
                provider="google",
                external_account_id="alice@example.com",
                artist_id="artist-3",
                tenant_id="tenant-a",
            )
            db_session.merge(account_to_update)
            account_to_update.external_account_id = "hacked@example.com"

            with pytest.raises(TenantIsolationViolation) as exc_info:
                db_session.flush()

            assert exc_info.value.current_tenant == "tenant-b"
            assert exc_info.value.target_tenant == "tenant-a"
            assert exc_info.value.operation == "UPDATE"

    finally:
        reset_tenant_context(tokens_b)


def test_delete_cross_tenant_record_raises(db_session, tenant_a_context, tenant_b_context):
    """DELETE on record from another tenant should raise exception."""
    # Create record as tenant-a
    account = OAuthConnectorAccount(
        id="test-account-4",
        provider="google",
        external_account_id="alice@example.com",
        artist_id="artist-4",
    )
    db_session.add(account)
    db_session.flush()
    db_session.commit()

    # Switch to tenant-b and try to delete
    reset_tenant_context((None, None))
    tokens_b = set_tenant_context("tenant-b", "user-bob")

    try:
        # Try to force-load and delete
        account_to_delete = OAuthConnectorAccount(
            id="test-account-4",
            provider="google",
            external_account_id="alice@example.com",
            artist_id="artist-4",
            tenant_id="tenant-a",
        )
        account_to_delete = db_session.merge(account_to_delete)
        db_session.delete(account_to_delete)

        with pytest.raises(TenantIsolationViolation) as exc_info:
            db_session.flush()

        assert exc_info.value.current_tenant == "tenant-b"
        assert exc_info.value.target_tenant == "tenant-a"
        assert exc_info.value.operation == "DELETE"

    finally:
        reset_tenant_context(tokens_b)


def test_no_tenant_context_allows_all_operations(db_session, no_tenant_context):
    """System operations without tenant context should not be blocked."""
    # This simulates system migrations, background jobs, etc.
    account = OAuthConnectorAccount(
        id="test-account-5",
        provider="google",
        external_account_id="system@example.com",
        artist_id="artist-5",
        tenant_id="any-tenant",
    )

    # Should not raise exception
    db_session.add(account)
    db_session.flush()

    # Update should work
    account.external_account_id = "updated@example.com"
    db_session.flush()

    # Delete should work
    db_session.delete(account)
    db_session.flush()


def test_select_auto_filters_by_tenant(db_session, tenant_a_context, tenant_b_context):
    """SELECT queries should auto-filter by tenant_id."""
    # Create records for tenant-a
    for i in range(3):
        account = OAuthConnectorAccount(
            id=f"test-account-a-{i}",
            provider="google",
            external_account_id=f"alice{i}@example.com",
            artist_id=f"artist-a-{i}",
        )
        db_session.add(account)
    db_session.flush()
    db_session.commit()

    # Switch to tenant-b and create records
    reset_tenant_context((None, None))
    tokens_b = set_tenant_context("tenant-b", "user-bob")

    try:
        for i in range(2):
            account = OAuthConnectorAccount(
                id=f"test-account-b-{i}",
                provider="google",
                external_account_id=f"bob{i}@example.com",
                artist_id=f"artist-b-{i}",
            )
            db_session.add(account)
        db_session.flush()
        db_session.commit()

        # Query should only return tenant-b records
        accounts = db_session.query(OAuthConnectorAccount).all()
        assert len(accounts) == 2
        assert all(acc.tenant_id == "tenant-b" for acc in accounts)

    finally:
        reset_tenant_context(tokens_b)


def test_violation_logs_audit_trail(db_session, tenant_a_context, caplog):
    """Tenant violations should log audit trail for security monitoring."""
    account = OAuthConnectorAccount(
        id="test-account-6",
        provider="google",
        external_account_id="user@example.com",
        artist_id="artist-6",
        tenant_id="tenant-b",  # Wrong tenant
    )

    db_session.add(account)

    with pytest.raises(TenantIsolationViolation):
        db_session.flush()

    # Verify audit log
    assert any("tenant_isolation_violation_insert" in record.message for record in caplog.records)
    violation_logs = [r for r in caplog.records if "tenant_isolation_violation" in r.message]
    assert len(violation_logs) > 0

    log_extra = violation_logs[0].__dict__
    assert log_extra.get("current_tenant") == "tenant-a"
    assert log_extra.get("target_tenant") == "tenant-b"
    assert log_extra.get("actor") == "user-alice"


def test_bulk_insert_auto_injects_tenant_id(db_session, tenant_a_context):
    """Bulk INSERT should auto-inject tenant_id for all objects."""
    accounts = [
        OAuthConnectorAccount(
            id=f"test-bulk-{i}",
            provider="google",
            external_account_id=f"user{i}@example.com",
            artist_id=f"artist-{i}",
            # tenant_id omitted
        )
        for i in range(5)
    ]

    db_session.add_all(accounts)
    db_session.flush()

    # Verify all have tenant_id injected
    for account in accounts:
        assert account.tenant_id == "tenant-a"


def test_tenant_isolation_prevents_data_leakage():
    """End-to-end test: tenants cannot see each other's data."""
    session = SessionLocal()

    try:
        # Tenant A creates data
        tokens_a = set_tenant_context("tenant-a", "user-alice")
        account_a = OAuthConnectorAccount(
            id="secret-account-a",
            provider="google",
            external_account_id="alice@secret.com",
            artist_id="artist-a",
        )
        session.add(account_a)
        session.flush()
        session.commit()
        reset_tenant_context(tokens_a)

        # Tenant B tries to access tenant A's data
        tokens_b = set_tenant_context("tenant-b", "user-bob")
        leaked_accounts = (
            session.query(OAuthConnectorAccount)
            .filter(OAuthConnectorAccount.id == "secret-account-a")
            .all()
        )

        # Should return empty (auto-filtered)
        assert len(leaked_accounts) == 0

        # Tenant B tries to update tenant A's data directly
        account_to_hack = OAuthConnectorAccount(
            id="secret-account-a",
            provider="google",
            external_account_id="alice@secret.com",
            artist_id="artist-a",
            tenant_id="tenant-a",
        )
        session.merge(account_to_hack)
        account_to_hack.external_account_id = "hacked@evil.com"

        # Should raise violation
        with pytest.raises(TenantIsolationViolation):
            session.flush()

        reset_tenant_context(tokens_b)

    finally:
        session.close()
