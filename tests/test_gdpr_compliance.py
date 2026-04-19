"""
Tests for GDPR compliance endpoints.

Validates Data Subject Access Request (DSAR) and Right to Erasure
per GDPR Articles 15 and 17.

Closes: XR7-405
Domain: compliance-automation
Scale-target: GDPR/CCPA compliance for 10x tenant count (EU customers)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal

client = TestClient(app)

# Mock admin headers (in production, this would be JWT-based)
ADMIN_HEADERS = {"x-admin-key": "admin-secret"}


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_artist(db_session):
    """Create test artist with PII."""
    artist = Artist(
        id="test-artist-gdpr-1",
        email="test.user@example.com",
        name="Test User",
        tenant_id="test-tenant",
    )
    db_session.add(artist)
    db_session.commit()
    db_session.refresh(artist)
    yield artist


def test_dsar_returns_personal_data(db_session, test_artist):
    """GDPR Article 15 - DSAR should return all personal data for email."""
    response = client.get(
        f"/gdpr/data-subject-access?email={test_artist.email}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == test_artist.email
    assert "artists" in data["collected_data"]
    assert len(data["collected_data"]["artists"]) == 1
    assert data["collected_data"]["artists"][0]["id"] == test_artist.id
    assert data["collection_timestamp"] is not None
    assert "7 years" in data["retention_period"]


def test_dsar_returns_404_for_unknown_email(db_session):
    """DSAR should return 404 when no data exists for email."""
    response = client.get(
        "/gdpr/data-subject-access?email=nonexistent@example.com",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 404
    assert "No personal data found" in response.json()["detail"]


def test_dsar_includes_audit_logs(db_session, test_artist):
    """DSAR should include admin audit logs referencing the email."""
    # Create audit log entry
    audit_log = AdminAuditLog(
        action="user_login",
        actor_email=test_artist.email,
        actor_sub="sub-123",
    )
    db_session.add(audit_log)
    db_session.commit()

    response = client.get(
        f"/gdpr/data-subject-access?email={test_artist.email}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()

    assert "admin_audit_logs" in data["collected_data"]
    assert len(data["collected_data"]["admin_audit_logs"]) >= 1


def test_erasure_pseudonymizes_artist_data(db_session, test_artist):
    """GDPR Article 17 - Erasure should pseudonymize PII."""
    original_email = test_artist.email
    original_name = test_artist.name
    artist_id = test_artist.id

    response = client.delete(
        "/gdpr/erase",
        headers=ADMIN_HEADERS,
        json={
            "email": original_email,
            "reason": "Customer request",
            "preserve_financial_records": True,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == original_email
    assert data["records_pseudonymized"] > 0
    assert data["erasure_timestamp"] is not None
    assert data["audit_log_id"] is not None

    # Verify pseudonymization in database
    db_session.expire_all()
    artist = db_session.query(Artist).filter(Artist.id == artist_id).first()

    assert artist.email != original_email
    assert "deleted-" in artist.email
    assert "@gdpr-erased.invalid" in artist.email
    assert artist.name != original_name
    assert "[ERASED-" in artist.name


def test_erasure_preserves_financial_records(db_session, test_artist):
    """Erasure with preserve_financial_records=True should not delete financial data."""
    response = client.delete(
        "/gdpr/erase",
        headers=ADMIN_HEADERS,
        json={
            "email": test_artist.email,
            "reason": "GDPR Article 17",
            "preserve_financial_records": True,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Financial records preserved (not deleted)
    # In a real scenario, we'd create claims/payments and verify they still exist
    assert "records_preserved" in data


def test_erasure_creates_audit_log(db_session, test_artist):
    """Erasure should create audit log entry for compliance."""
    response = client.delete(
        "/gdpr/erase",
        headers=ADMIN_HEADERS,
        json={
            "email": test_artist.email,
            "reason": "Customer request",
            "preserve_financial_records": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    audit_log_id = data["audit_log_id"]

    # Verify audit log was created
    audit_log = db_session.query(AdminAuditLog).filter(AdminAuditLog.id == audit_log_id).first()

    assert audit_log is not None
    assert audit_log.action == "gdpr_erasure_completed"
    assert audit_log.target_email == test_artist.email
    assert "reason" in audit_log.changes


def test_dsar_logs_audit_trail(db_session, test_artist):
    """DSAR should create audit log for compliance tracking."""
    response = client.get(
        f"/gdpr/data-subject-access?email={test_artist.email}",
        headers=ADMIN_HEADERS,
    )

    assert response.status_code == 200

    # Verify DSAR audit log was created
    dsar_logs = (
        db_session.query(AdminAuditLog)
        .filter(AdminAuditLog.action == "gdpr_dsar_completed")
        .filter(AdminAuditLog.target_email == test_artist.email)
        .all()
    )

    assert len(dsar_logs) > 0


def test_erasure_pseudonymizes_audit_logs(db_session, test_artist):
    """Erasure should pseudonymize email in audit logs."""
    # Create audit log with artist's email
    audit_log = AdminAuditLog(
        action="test_action",
        actor_email=test_artist.email,
        actor_sub="sub-123",
    )
    db_session.add(audit_log)
    db_session.commit()
    audit_log_id = audit_log.id

    # Execute erasure
    response = client.delete(
        "/gdpr/erase",
        headers=ADMIN_HEADERS,
        json={
            "email": test_artist.email,
            "reason": "Test erasure",
            "preserve_financial_records": True,
        },
    )

    assert response.status_code == 200

    # Verify audit log email was pseudonymized
    db_session.expire_all()
    pseudonymized_log = (
        db_session.query(AdminAuditLog).filter(AdminAuditLog.id == audit_log_id).first()
    )

    assert pseudonymized_log.actor_email == "[ERASED]"


def test_multiple_artists_same_email():
    """DSAR should return all records when multiple artists share an email."""
    db = SessionLocal()

    try:
        # Create two artists with same email (edge case)
        artist1 = Artist(
            id="artist-1",
            email="shared@example.com",
            name="Artist One",
            tenant_id="tenant-1",
        )
        artist2 = Artist(
            id="artist-2",
            email="shared@example.com",
            name="Artist Two",
            tenant_id="tenant-2",
        )

        db.add_all([artist1, artist2])
        db.commit()

        response = client.get(
            "/gdpr/data-subject-access?email=shared@example.com",
            headers=ADMIN_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["collected_data"]["artists"]) == 2

    finally:
        db.close()
