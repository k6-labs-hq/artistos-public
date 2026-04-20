"""Tests for review queue status enum validation."""

import uuid

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.artist import Artist
from XR7.models.base import Base, engine, get_db
from XR7.models.review_queue import ReviewItem, ReviewItemStatus

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Setup test database with analyst API key."""
    monkeypatch.setenv("ANALYST_API_KEY", "test-analyst-key")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def analyst_headers():
    """Headers for analyst authentication."""
    return {
        "X-Analyst-Key": "test-analyst-key",
        "X-Analyst-Email": "analyst@test.com",
    }


@pytest.fixture
def test_review_item():
    """Create a test review item."""
    db = next(get_db())
    try:
        # Create artist
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Test Artist",
            email="artist@test.com",
        )
        db.add(artist)
        db.commit()

        # Create review item
        item = ReviewItem(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            source_type="ANOMALY",
            source_id=str(uuid.uuid4()),
            reason="Test review item",
            priority_score=1.0,
            status=ReviewItemStatus.OPEN.value,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


def test_list_review_items_with_valid_status(analyst_headers, test_review_item):
    """Test listing review items with valid status enum value."""
    response = client.get(
        "/review-queue/items?status=OPEN",
        headers=analyst_headers,
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert all(item["status"] == "OPEN" for item in items)


def test_list_review_items_with_invalid_status_returns_422(analyst_headers, test_review_item):
    """Test listing review items with invalid status returns validation error."""
    response = client.get(
        "/review-queue/items?status=INVALID_STATUS",
        headers=analyst_headers,
    )
    assert response.status_code == 422
    error = response.json()
    assert "detail" in error
    # FastAPI returns validation error for invalid enum value
    assert any("status" in str(e).lower() for e in error["detail"])


def test_list_review_items_all_valid_statuses(analyst_headers, test_review_item):
    """Test that all valid ReviewItemStatus values work."""
    valid_statuses = ["OPEN", "IN_REVIEW", "RESOLVED", "DISMISSED"]

    for status in valid_statuses:
        response = client.get(
            f"/review-queue/items?status={status}",
            headers=analyst_headers,
        )
        assert response.status_code == 200, f"Status {status} should be valid"


def test_list_review_items_without_status_filter(analyst_headers, test_review_item):
    """Test listing review items without status filter returns all items."""
    response = client.get(
        "/review-queue/items",
        headers=analyst_headers,
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1


def test_list_review_items_case_sensitive_validation(analyst_headers, test_review_item):
    """Test that status enum is case-sensitive."""
    # Lowercase should fail
    response = client.get(
        "/review-queue/items?status=open",
        headers=analyst_headers,
    )
    assert response.status_code == 422

    # Mixed case should fail
    response = client.get(
        "/review-queue/items?status=Open",
        headers=analyst_headers,
    )
    assert response.status_code == 422
