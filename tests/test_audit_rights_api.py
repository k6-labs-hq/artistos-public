"""Integration tests for audit rights workflow API.

Tests audit rights automation endpoints (Feature #16):
- Create audit workflow
- List workflows
- Generate demand letter
- Update workflow status
- Stats endpoint
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from XR7.services.audit_rights_service import AuditRightsWorkflow, AuditWorkflowStatus

client = TestClient(app)


@pytest.fixture
def db():
    """Use the shared test database session from conftest.py."""
    from tests.conftest import TestSession

    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_artist(db):
    """Create a test artist for audit workflow tests."""
    artist = Artist(id="test-artist-audit", name="Test Artist")
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@pytest.fixture
def test_audit_workflow(db, test_artist):
    """Create a test audit workflow."""
    workflow = AuditRightsWorkflow(
        id="test-workflow-123",
        artist_id=test_artist.id,
        contract_id="contract-123",
        counterparty_name="Universal Music Group",
        counterparty_address="2220 Colorado Avenue, Santa Monica, CA 90404",
        counterparty_contact="Legal Department",
        status=AuditWorkflowStatus.IDENTIFIED,
        audit_period_start=datetime(2023, 1, 1, tzinfo=timezone.utc),
        audit_period_end=datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def test_create_audit_workflow(db, test_artist):
    """Test creating a new audit rights workflow."""

    response = client.post(
        f"/artists/{test_artist.id}/audit-workflows",
        json={
            "artist_id": test_artist.id,
            "contract_id": "contract-123",
            "counterparty_name": "Universal Music Group",
            "counterparty_address": "2220 Colorado Avenue, Santa Monica, CA 90404",
            "counterparty_contact": "Legal Department",
            "audit_period_start": "2023-01-01T00:00:00Z",
            "audit_period_end": "2025-12-31T23:59:59Z",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["artist_id"] == test_artist.id
    assert data["contract_id"] == "contract-123"
    assert data["counterparty_name"] == "Universal Music Group"
    assert data["status"] == "IDENTIFIED"
    assert "id" in data
    assert "created_at" in data


def test_list_audit_workflows(db, test_artist, test_audit_workflow):
    """Test listing audit workflows for an artist."""

    response = client.get(f"/artists/{test_artist.id}/audit-workflows")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(w["id"] == test_audit_workflow.id for w in data)


def test_list_audit_workflows_filtered_by_status(db, test_artist, test_audit_workflow):
    """Test filtering workflows by status."""

    response = client.get(
        f"/artists/{test_artist.id}/audit-workflows",
        params={"status": "IDENTIFIED"},
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert all(w["status"] == "IDENTIFIED" for w in data)


def test_get_audit_workflow_detail(db, test_artist, test_audit_workflow):
    """Test getting audit workflow details."""

    response = client.get(f"/artists/{test_artist.id}/audit-workflows/{test_audit_workflow.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_audit_workflow.id
    assert data["artist_id"] == test_artist.id
    assert data["counterparty_name"] == test_audit_workflow.counterparty_name


def test_get_audit_workflow_not_found(db, test_artist):
    """Test 404 when workflow doesn't exist."""

    response = client.get(f"/artists/{test_artist.id}/audit-workflows/nonexistent-workflow-id")

    assert response.status_code == 404


def test_generate_audit_demand_letter(db, test_artist, test_audit_workflow):
    """Test generating audit demand letter."""

    proposed_date = datetime.now(timezone.utc) + timedelta(days=45)

    response = client.post(
        f"/artists/{test_artist.id}/audit-workflows/{test_audit_workflow.id}/generate-letter",
        json={
            "artist_name": "Test Artist Legal Name",
            "contract_name": "Recording Agreement",
            "contract_date": "January 15, 2020",
            "audit_clause_reference": "Section 12.3",
            "proposed_audit_date": proposed_date.isoformat(),
            "attorney_name": "Jane Doe, Esq.",
            "auditor_name": "Smith & Associates CPA",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"

    letter_text = response.text

    # Verify key elements in letter
    assert "Test Artist Legal Name" in letter_text
    assert "Section 12.3" in letter_text
    assert "Jane Doe, Esq." in letter_text
    assert "Smith & Associates CPA" in letter_text
    assert "Universal Music Group" in letter_text
    assert "thirty (30) days" in letter_text

    # Verify workflow status updated to LETTER_DRAFTED
    db.refresh(test_audit_workflow)
    assert test_audit_workflow.status == AuditWorkflowStatus.LETTER_DRAFTED
    assert test_audit_workflow.letter_generated_at is not None
    assert test_audit_workflow.letter_template_version == "v1.0"


def test_update_workflow_status(db, test_artist, test_audit_workflow):
    """Test updating workflow status."""

    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{test_audit_workflow.id}",
        json={
            "status": "LETTER_SENT",
            "notes": "Sent via certified mail",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "LETTER_SENT"
    assert data["letter_sent_at"] is not None  # Auto-populated

    # Verify database was updated
    db.refresh(test_audit_workflow)
    assert test_audit_workflow.status == AuditWorkflowStatus.LETTER_SENT
    assert test_audit_workflow.letter_sent_at is not None


def test_update_workflow_status_not_found(db, test_artist):
    """Test 404 when updating nonexistent workflow."""

    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/nonexistent-id",
        json={"status": "LETTER_SENT"},
    )

    assert response.status_code == 404


def test_audit_workflow_stats(db, test_audit_workflow):
    """Test system-wide audit workflow statistics."""

    response = client.get("/audit-workflows/stats")

    assert response.status_code == 200
    data = response.json()

    assert "by_status" in data
    assert "total_workflows" in data
    assert isinstance(data["by_status"], dict)
    assert isinstance(data["total_workflows"], int)
    assert data["total_workflows"] > 0


def test_create_workflow_artist_id_mismatch(db, test_artist):
    """Test validation error when artist_id in path doesn't match body."""

    response = client.post(
        f"/artists/{test_artist.id}/audit-workflows",
        json={
            "artist_id": "different-artist-id",
            "counterparty_name": "Test Label",
        },
    )

    assert response.status_code == 400
    assert "mismatch" in response.json()["detail"].lower()


def test_workflow_progression_through_states(db, test_artist, test_audit_workflow):
    """Test complete workflow progression from IDENTIFIED to CLOSED."""

    workflow_id = test_audit_workflow.id

    # Step 1: Generate letter (IDENTIFIED → LETTER_DRAFTED)
    proposed_date = datetime.now(timezone.utc) + timedelta(days=45)
    response = client.post(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}/generate-letter",
        json={
            "artist_name": "Test Artist",
            "contract_name": "Recording Agreement",
            "contract_date": "January 1, 2020",
            "audit_clause_reference": "Section 12",
            "proposed_audit_date": proposed_date.isoformat(),
            "attorney_name": "Attorney Name",
        },
    )
    assert response.status_code == 200
    db.refresh(test_audit_workflow)
    assert test_audit_workflow.status == AuditWorkflowStatus.LETTER_DRAFTED

    # Step 2: Mark letter as sent
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "LETTER_SENT"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "LETTER_SENT"

    # Step 3: Mark response received
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "RESPONSE_RECEIVED"},
    )
    assert response.status_code == 200

    # Step 4: Schedule audit
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "AUDIT_SCHEDULED"},
    )
    assert response.status_code == 200

    # Step 5: Complete audit
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "AUDIT_COMPLETED"},
    )
    assert response.status_code == 200

    # Step 6: Negotiate settlement
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "SETTLEMENT_NEGOTIATED"},
    )
    assert response.status_code == 200

    # Step 7: Close workflow
    response = client.patch(
        f"/artists/{test_artist.id}/audit-workflows/{workflow_id}",
        json={"status": "CLOSED"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CLOSED"

    # Verify final state
    db.refresh(test_audit_workflow)
    assert test_audit_workflow.status == AuditWorkflowStatus.CLOSED
