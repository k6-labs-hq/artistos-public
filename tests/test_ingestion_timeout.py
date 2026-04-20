"""
Tests for statement parsing timeout enforcement.

Ensures that malformed or maliciously crafted large statement files do not
hang the ingestion worker indefinitely.

Closes: XR7-402
Domain: ingestion
Scale-target: 10x ingestion volume with DoS protection
Compliance: SOC 2 CC6.1 — Data integrity and availability controls
"""

from __future__ import annotations

import io
import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TEST_ARTIST_ID, create_test_artist, create_test_terms
from XR7.api.app import app
from XR7.ingestion.parse_timeout import (
    StatementParseTimeoutError,
    TimeoutConfig,
    parse_with_timeout,
)
from XR7.models.base import SessionLocal


def slow_parse_fn(content: bytes, artist_id: str, filename: str = "test.csv", **kwargs):
    """Mock parsing function that takes 5 seconds."""
    time.sleep(5)
    return {
        "format_detected": "test",
        "row_count": 10,
        "events": [],
        "payments": [],
        "errors": [],
    }


def test_parse_timeout_enforces_timeout():
    """Parsing function that exceeds timeout should raise TimeoutError."""
    timeout_config = TimeoutConfig(timeout_seconds=2, enabled=True)

    with pytest.raises(StatementParseTimeoutError) as exc_info:
        parse_with_timeout(
            slow_parse_fn,
            b"test content",
            "artist-123",
            "slow_file.csv",
            timeout_config=timeout_config,
        )

    assert exc_info.value.timeout_seconds == 2
    assert "slow_file.csv" in str(exc_info.value)


def test_parse_timeout_allows_fast_parsing():
    """Parsing function that completes quickly should succeed."""
    timeout_config = TimeoutConfig(timeout_seconds=10, enabled=True)

    def fast_parse_fn(content: bytes, artist_id: str, filename: str = "test.csv", **kwargs):
        return {
            "format_detected": "test",
            "row_count": 5,
            "events": [],
            "payments": [],
            "errors": [],
        }

    result = parse_with_timeout(
        fast_parse_fn,
        b"test content",
        "artist-123",
        "fast_file.csv",
        timeout_config=timeout_config,
    )

    assert result["format_detected"] == "test"
    assert result["row_count"] == 5


def test_parse_timeout_logs_warning_for_slow_parsing(caplog):
    """Parsing that approaches timeout should log warning."""
    timeout_config = TimeoutConfig(timeout_seconds=10, log_threshold_seconds=1, enabled=True)

    def medium_parse_fn(content: bytes, artist_id: str, filename: str = "test.csv", **kwargs):
        time.sleep(2)  # Exceeds log_threshold but not timeout
        return {
            "format_detected": "test",
            "row_count": 5,
            "events": [],
            "payments": [],
            "errors": [],
        }

    result = parse_with_timeout(
        medium_parse_fn,
        b"test content",
        "artist-123",
        "medium_file.csv",
        timeout_config=timeout_config,
    )

    assert result["format_detected"] == "test"
    assert any("Statement parsing slow" in record.message for record in caplog.records)


def test_parse_timeout_can_be_disabled():
    """Timeout enforcement can be disabled for testing."""
    timeout_config = TimeoutConfig(timeout_seconds=1, enabled=False)

    # This would timeout if enabled, but should succeed when disabled
    result = parse_with_timeout(
        slow_parse_fn,  # Takes 5 seconds
        b"test content",
        "artist-123",
        "file.csv",
        timeout_config=timeout_config,
    )

    assert result["format_detected"] == "test"


def test_ingestion_endpoint_timeout_returns_422():
    """Uploading a file that triggers parse timeout should return 422."""
    db = SessionLocal()
    client = TestClient(app)

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Mock parse_with_timeout to always raise timeout
        def mock_timeout(*args, **kwargs):
            raise StatementParseTimeoutError(60, "malformed.csv")

        with patch("XR7.api.routers.ingestion.parse_with_timeout", side_effect=mock_timeout):
            csv_content = b"""Date,Platform,Streams,Revenue
2024-03-01,Spotify,100,0.40"""

            response = client.post(
                f"/artists/{TEST_ARTIST_ID}/statements/upload",
                files={"file": ("malformed.csv", io.BytesIO(csv_content), "text/csv")},
            )

            assert response.status_code == 422
            assert "timed out" in response.json()["detail"].lower()
            assert "60 seconds" in response.json()["detail"]

    finally:
        db.close()


def test_ingestion_timeout_releases_worker():
    """Worker should remain healthy after parsing timeout."""
    db = SessionLocal()
    client = TestClient(app)

    try:
        create_test_artist(db, TEST_ARTIST_ID)
        create_test_terms(db)
        client.post(f"/artists/{TEST_ARTIST_ID}/terms/accept")

        # Mock timeout
        with patch(
            "XR7.api.routers.ingestion.parse_with_timeout",
            side_effect=StatementParseTimeoutError(60, "bad.csv"),
        ):
            response1 = client.post(
                f"/artists/{TEST_ARTIST_ID}/statements/upload",
                files={"file": ("bad.csv", io.BytesIO(b"test"), "text/csv")},
            )
            assert response1.status_code == 422

        # Subsequent request should work (worker not hung)
        valid_csv = b"""Reporting Month,Sale Month,Store,Artist Name,Title,Quantity,Song/Album,Customer Price,Earnings (USD)
2024-03,2024-03,Spotify,Test Artist,Stream Track,100,Stream,0.004,0.40"""

        response2 = client.post(
            f"/artists/{TEST_ARTIST_ID}/statements/upload",
            files={"file": ("valid.csv", io.BytesIO(valid_csv), "text/csv")},
        )
        assert response2.status_code == 201
        assert response2.json()["events_created"] == 1

    finally:
        db.close()


def test_batch_upload_timeout_continues_with_other_files():
    """Batch upload should continue processing other files if one times out."""
    # This test would require a batch upload endpoint to be implemented
    # Placeholder for future implementation
    pass


def test_timeout_metrics_logged(caplog):
    """Timeout events should be logged with sufficient context for alerting."""
    timeout_config = TimeoutConfig(timeout_seconds=1, enabled=True)

    with pytest.raises(StatementParseTimeoutError):
        parse_with_timeout(
            slow_parse_fn,
            b"test content" * 1000,  # Larger file
            "artist-123",
            "timeout_test.csv",
            timeout_config=timeout_config,
        )

    # Check that error log contains key fields for alerting
    timeout_logs = [r for r in caplog.records if "Statement parsing timeout" in r.message]
    assert len(timeout_logs) == 1

    log_extra = timeout_logs[0].__dict__
    assert log_extra.get("artist_id") == "artist-123"
    assert log_extra.get("filename") == "timeout_test.csv"
    assert log_extra.get("timeout_seconds") == 1
    assert "file_size_bytes" in log_extra


def test_timeout_config_from_env():
    """Timeout configuration should be loadable from environment."""
    import os

    from XR7.ingestion.parse_timeout import get_timeout_config_from_env

    original_timeout = os.environ.get("STATEMENT_PARSE_TIMEOUT_SECONDS")
    original_threshold = os.environ.get("STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD")

    try:
        os.environ["STATEMENT_PARSE_TIMEOUT_SECONDS"] = "120"
        os.environ["STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD"] = "60"

        config = get_timeout_config_from_env()

        assert config.timeout_seconds == 120
        assert config.log_threshold_seconds == 60
        assert config.enabled is True

    finally:
        # Restore original env vars
        if original_timeout:
            os.environ["STATEMENT_PARSE_TIMEOUT_SECONDS"] = original_timeout
        else:
            os.environ.pop("STATEMENT_PARSE_TIMEOUT_SECONDS", None)

        if original_threshold:
            os.environ["STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD"] = original_threshold
        else:
            os.environ.pop("STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD", None)
