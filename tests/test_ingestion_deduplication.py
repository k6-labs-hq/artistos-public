"""
Tests for row-level event deduplication during statement ingestion.

Ensures that uploading overlapping statements (e.g., monthly statements that
include the same events) does not create duplicate event records in the database.

Closes: XR7-401
Domain: ingestion
Scale-target: 10x ingestion volume with correctness guarantees
SOC 2: CC6.1 — Data integrity controls
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func

from tests.conftest import TEST_ARTIST_ID, create_test_artist, create_test_terms
from XR7.api.app import app
from XR7.models.base import SessionLocal
from XR7.models.event import Event


@pytest.fixture
def test_csv_distrokid():
    """Sample DistroKid CSV with 3 unique events."""
    return """Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.004,0.40
2024-03,2024-03,Apple Music,Test Artist,Stream Track,50,Stream,0.007,0.35
2024-03,2024-03,YouTube Music,Test Artist,Stream Track,25,Stream,0.002,0.05"""


@pytest.fixture
def test_csv_distrokid_overlapping():
    """DistroKid CSV with same events plus 2 new ones (simulating re-upload)."""
    return """Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.004,0.40
2024-03,2024-03,Apple Music,Test Artist,Stream Track,50,Stream,0.007,0.35
2024-03,2024-03,YouTube Music,Test Artist,Stream Track,25,Stream,0.002,0.05
2024-04,2024-04,Spotify,Test Artist,Stream Track,200,Stream,0.004,0.80
2024-04,2024-04,Apple Music,Test Artist,Stream Track,100,Stream,0.007,0.70"""


def test_event_deduplication_same_file_rejected(test_csv_distrokid):
    """Uploading the exact same file twice should be rejected at file level."""
    db = SessionLocal()
    client = TestClient(app)

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)

        # Accept terms
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Upload first time
        file_content = test_csv_distrokid.encode("utf-8")
        response1 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("march_statement.csv", io.BytesIO(file_content), "text/csv")},
        )
        assert response1.status_code == 201
        statement1 = response1.json()
        assert statement1["events_created"] == 3

        # Upload same file again - should be rejected with 409
        response2 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("march_statement.csv", io.BytesIO(file_content), "text/csv")},
        )
        assert response2.status_code == 409
        assert "already been uploaded" in response2.json()["detail"]

        # Verify no duplicate events
        event_count = (
            db.query(func.count(Event.id)).filter(Event.artist_id == TEST_ARTIST_ID).scalar()
        )
        assert event_count == 3

    finally:
        db.close()


def test_event_deduplication_overlapping_statements(
    test_csv_distrokid, test_csv_distrokid_overlapping
):
    """Uploading overlapping statements should deduplicate at row level."""
    db = SessionLocal()
    client = TestClient(app)

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)

        # Accept terms
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Upload March statement (3 events)
        file1 = test_csv_distrokid.encode("utf-8")
        response1 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("march_statement.csv", io.BytesIO(file1), "text/csv")},
        )
        assert response1.status_code == 201
        assert response1.json()["events_created"] == 3

        # Verify 3 events created
        event_count = (
            db.query(func.count(Event.id)).filter(Event.artist_id == TEST_ARTIST_ID).scalar()
        )
        assert event_count == 3

        # Upload overlapping statement (3 old + 2 new events)
        file2 = test_csv_distrokid_overlapping.encode("utf-8")
        response2 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("march_april_statement.csv", io.BytesIO(file2), "text/csv")},
        )
        assert response2.status_code == 201
        statement2 = response2.json()

        # Should only insert 2 new events, skip 3 duplicates
        assert statement2["events_created"] == 2

        # Verify total events is 5 (not 8)
        event_count = (
            db.query(func.count(Event.id)).filter(Event.artist_id == TEST_ARTIST_ID).scalar()
        )
        assert event_count == 5, "Should have 3 original + 2 new = 5 events, not 8"

    finally:
        db.close()


def test_event_deduplication_metrics_logged(test_csv_distrokid_overlapping, caplog):
    """Deduplication should log metrics about skipped events."""
    db = SessionLocal()
    client = TestClient(app)

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Upload statement
        file = test_csv_distrokid_overlapping.encode("utf-8")
        response = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("statement.csv", io.BytesIO(file), "text/csv")},
        )
        assert response.status_code == 201

        # Upload same statement again (different filename to bypass file-level dedup)
        response2 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("statement_v2.csv", io.BytesIO(file), "text/csv")},
        )

        # Should not raise error, just skip duplicates
        assert response2.status_code == 201
        assert response2.json()["events_created"] == 0

        # Check logs for deduplication metrics
        assert any("Event ingestion complete" in record.message for record in caplog.records)
        assert any("skipped_duplicates" in str(record.__dict__) for record in caplog.records)

    finally:
        db.close()


def test_event_deduplication_preserves_legitimate_updates():
    """Events with different unit_value should be treated as distinct."""
    db = SessionLocal()
    client = TestClient(app)

    csv_v1 = """Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.004,0.40"""

    csv_v2_updated = """Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.005,0.50"""

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Upload original
        response1 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("v1.csv", io.BytesIO(csv_v1.encode()), "text/csv")},
        )
        assert response1.status_code == 201
        assert response1.json()["events_created"] == 1

        # Upload updated version (same event but different unit_value)
        response2 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("v2.csv", io.BytesIO(csv_v2_updated.encode()), "text/csv")},
        )
        assert response2.status_code == 201
        assert response2.json()["events_created"] == 1

        # Should have 2 events (original + update)
        event_count = (
            db.query(func.count(Event.id)).filter(Event.artist_id == TEST_ARTIST_ID).scalar()
        )
        assert event_count == 2

    finally:
        db.close()


def test_event_deduplication_across_artists():
    """Same event for different artists should NOT be deduplicated."""
    db = SessionLocal()
    client = TestClient(app)

    artist1_id = "test-artist-1"
    artist2_id = "test-artist-2"

    csv = """Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.004,0.40"""

    try:
        create_test_artist(db, artist1_id)
        create_test_artist(db, artist2_id)
        create_test_terms(db)

        client.post(f"/artists/{artist1_id}/terms/accept")
        client.post(f"/artists/{artist2_id}/terms/accept")

        # Upload for artist 1
        response1 = client.post(
            f"/artists/{artist1_id}/statements/upload",
            files={"file": ("statement.csv", io.BytesIO(csv.encode()), "text/csv")},
        )
        assert response1.status_code == 201
        assert response1.json()["events_created"] == 1

        # Upload same data for artist 2 - should create event
        response2 = client.post(
            f"/artists/{artist2_id}/statements/upload",
            files={"file": ("statement.csv", io.BytesIO(csv.encode()), "text/csv")},
        )
        assert response2.status_code == 201
        assert response2.json()["events_created"] == 1

        # Verify 2 total events (one per artist)
        total_events = db.query(func.count(Event.id)).scalar()
        assert total_events == 2

    finally:
        db.close()
