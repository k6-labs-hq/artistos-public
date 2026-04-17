"""
Test upload rate limiting to prevent resource exhaustion.

CRITICAL SECURITY TESTS: These tests verify that file upload endpoints
have proper rate limiting to prevent abuse.

Without rate limiting:
- Malicious artists spam uploads 24/7
- Storage costs spike (S3/disk)
- ClamAV scan queue overwhelms
- Database write saturation
- Legitimate users blocked by resource exhaustion

With 10 uploads/hour/artist:
- Predictable infrastructure costs
- Fair resource distribution
- Attack surface minimized
- ClamAV scan capacity protected
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status

from XR7.services.rate_limiter import (
    UPLOAD_RATE_LIMIT_PER_ARTIST,
    UPLOAD_RATE_LIMIT_WINDOW,
    check_upload_rate_limit,
    get_remaining_uploads,
    increment_upload_count,
    reset_upload_rate_limit,
)


@pytest.fixture
def mock_redis():
    """Mock Redis client for rate limiting tests."""
    with patch("XR7.services.rate_limiter.get_redis_client") as mock:
        redis_mock = MagicMock()
        mock.return_value = redis_mock
        yield redis_mock


def test_first_upload_allowed(mock_redis):
    """
    Verify first upload is always allowed.

    When artist has no upload history, they should be allowed to upload
    and a new rate limit window should be created.
    """
    mock_redis.get.return_value = None  # No existing counter

    # Should not raise exception
    check_upload_rate_limit("artist_123")

    # Should create new counter with TTL
    mock_redis.setex.assert_called_once_with(
        "upload_rate_limit:artist_123", UPLOAD_RATE_LIMIT_WINDOW, 1
    )


def test_upload_within_limit_allowed(mock_redis):
    """
    Verify uploads within rate limit are allowed.

    Artist with 5 uploads should be allowed to upload more (limit is 10).
    """
    mock_redis.get.return_value = "5"  # 5 uploads so far

    # Should not raise exception
    check_upload_rate_limit("artist_123")

    # Should increment counter
    mock_redis.incr.assert_called_once_with("upload_rate_limit:artist_123")


def test_upload_at_limit_rejected(mock_redis):
    """
    Verify 11th upload is rejected with 429 status code.

    When artist has already uploaded 10 files (the limit), the next
    upload should be rejected with HTTP 429 Too Many Requests.
    """
    mock_redis.get.return_value = "10"  # Already at limit
    mock_redis.ttl.return_value = 1800  # 30 minutes remaining

    with pytest.raises(HTTPException) as exc_info:
        check_upload_rate_limit("artist_123")

    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Upload rate limit exceeded" in exc_info.value.detail
    assert "10 uploads per hour" in exc_info.value.detail
    assert exc_info.value.headers["Retry-After"] == "1800"


def test_upload_over_limit_rejected(mock_redis):
    """
    Verify uploads beyond limit are consistently rejected.

    Even if somehow the counter goes above 10, subsequent uploads
    should still be rejected.
    """
    mock_redis.get.return_value = "15"  # Way over limit
    mock_redis.ttl.return_value = 600  # 10 minutes remaining

    with pytest.raises(HTTPException) as exc_info:
        check_upload_rate_limit("artist_123")

    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exc_info.value.headers["Retry-After"] == "600"


def test_rate_limit_error_includes_retry_time(mock_redis):
    """
    Verify 429 response includes Retry-After header with seconds.

    This header tells clients when they can retry the request.
    """
    mock_redis.get.return_value = "10"
    mock_redis.ttl.return_value = 2400  # 40 minutes = 2400 seconds

    with pytest.raises(HTTPException) as exc_info:
        check_upload_rate_limit("artist_123")

    # Should include minutes in error message
    assert "41 minutes" in exc_info.value.detail  # 2400 // 60 + 1 = 41

    # Should include exact seconds in header
    assert exc_info.value.headers["Retry-After"] == "2400"


def test_get_remaining_uploads_no_history(mock_redis):
    """
    Verify remaining upload quota for new artist.

    Artist with no upload history should have full quota available.
    """
    mock_redis.get.return_value = None

    result = get_remaining_uploads("artist_123")

    assert result["remaining"] == 10
    assert result["limit"] == 10
    assert result["reset_in_seconds"] == 3600  # Full window


def test_get_remaining_uploads_partial_usage(mock_redis):
    """
    Verify remaining upload quota calculation.

    Artist with 3 uploads should have 7 remaining.
    """
    mock_redis.get.return_value = "3"
    mock_redis.ttl.return_value = 1200  # 20 minutes

    result = get_remaining_uploads("artist_123")

    assert result["remaining"] == 7  # 10 - 3
    assert result["limit"] == 10
    assert result["reset_in_seconds"] == 1200


def test_get_remaining_uploads_at_limit(mock_redis):
    """
    Verify remaining quota shows 0 when at limit.
    """
    mock_redis.get.return_value = "10"
    mock_redis.ttl.return_value = 900  # 15 minutes

    result = get_remaining_uploads("artist_123")

    assert result["remaining"] == 0
    assert result["limit"] == 10


def test_increment_upload_count_new_artist(mock_redis):
    """
    Verify incrementing counter for new artist.

    Should create new counter with TTL if one doesn't exist.
    """
    mock_redis.get.return_value = None

    increment_upload_count("artist_123")

    mock_redis.setex.assert_called_once_with(
        "upload_rate_limit:artist_123", UPLOAD_RATE_LIMIT_WINDOW, 1
    )


def test_increment_upload_count_existing_artist(mock_redis):
    """
    Verify incrementing counter for artist with upload history.

    Should increment existing counter, not create new one.
    """
    mock_redis.get.return_value = "5"

    increment_upload_count("artist_123")

    mock_redis.incr.assert_called_once_with("upload_rate_limit:artist_123")
    mock_redis.setex.assert_not_called()


def test_reset_upload_rate_limit(mock_redis):
    """
    Verify admin can reset rate limit for artist.

    Used for customer support escalations or testing.
    """
    reset_upload_rate_limit("artist_123")

    mock_redis.delete.assert_called_once_with("upload_rate_limit:artist_123")


def test_rate_limit_isolated_per_artist(mock_redis):
    """
    Verify rate limits are per-artist, not global.

    Artist A at limit should not affect Artist B.
    """
    # Artist A at limit
    mock_redis.get.return_value = "10"
    mock_redis.ttl.return_value = 1800

    with pytest.raises(HTTPException):
        check_upload_rate_limit("artist_A")

    # Artist B has separate counter
    mock_redis.get.return_value = "2"

    # Should not raise (different artist)
    check_upload_rate_limit("artist_B")

    # Both artists should have separate keys
    assert mock_redis.get.call_count == 2
    calls = [call[0][0] for call in mock_redis.get.call_args_list]
    assert "upload_rate_limit:artist_A" in calls
    assert "upload_rate_limit:artist_B" in calls


def test_rate_limit_configuration_values():
    """
    Verify rate limit configuration is set to expected values.

    10 uploads/hour is a reasonable limit that:
    - Prevents abuse (720 uploads/day would be malicious)
    - Allows legitimate usage (10 statements from various sources)
    - Protects ClamAV scan capacity
    - Keeps storage costs predictable
    """
    assert UPLOAD_RATE_LIMIT_PER_ARTIST == 10, (
        "Upload rate limit should be 10 per hour. "
        "This prevents resource exhaustion while allowing legitimate usage."
    )

    assert UPLOAD_RATE_LIMIT_WINDOW == 3600, (
        "Rate limit window should be 1 hour (3600 seconds). "
        "This provides reasonable interval for artists uploading multiple statements."
    )


def test_rate_limit_prevents_storage_exhaustion():
    """
    Scenario test: Rate limiting prevents storage cost attacks.

    Attack scenario (without rate limit):
    1. Attacker creates account
    2. Uploads 1000 x 50MB files = 50GB storage
    3. Repeats hourly = 1.2TB/day = $35/day in S3 costs
    4. 100 attackers = $3,500/day = $105,000/month

    Defense (with 10/hour limit):
    1. Attacker uploads 10 x 50MB files = 500MB
    2. Blocked for 1 hour
    3. Max 240 files/day = 12GB/day
    4. 100 attackers = 1.2TB/day = $35/day (manageable)

    10/hour limit reduces attack surface by 100x.
    """
    # Configuration prevents exponential storage growth
    max_uploads_per_hour = UPLOAD_RATE_LIMIT_PER_ARTIST
    max_file_size_mb = 50
    hours_per_day = 24

    max_storage_per_artist_per_day_gb = (
        max_uploads_per_hour * hours_per_day * max_file_size_mb / 1024
    )

    # With 10/hour limit: 10 * 24 * 50 / 1024 = ~11.7GB/day/artist
    assert max_storage_per_artist_per_day_gb < 15, (
        "Rate limit should cap storage growth at <15GB/day/artist. "
        f"Current: {max_storage_per_artist_per_day_gb:.1f}GB/day"
    )


def test_rate_limit_prevents_clamav_exhaustion():
    """
    Scenario test: Rate limiting protects ClamAV scan capacity.

    ClamAV scan performance:
    - Average scan time: 2 seconds per file
    - Single ClamAV daemon: ~1,800 scans/hour capacity

    Without rate limit:
    - 100 artists uploading 100 files/hour = 10,000 scans/hour
    - ClamAV queue size: 10,000 / 1,800 = 5.5 hour backlog
    - Legitimate users wait hours for scan results

    With 10 uploads/hour/artist:
    - 100 artists * 10 files/hour = 1,000 scans/hour
    - Well within ClamAV capacity (1,800/hour)
    - Near real-time scan results
    """
    max_uploads_per_artist_per_hour = UPLOAD_RATE_LIMIT_PER_ARTIST
    expected_peak_concurrent_artists = 100  # Conservative estimate

    total_scans_per_hour = max_uploads_per_artist_per_hour * expected_peak_concurrent_artists

    # Single ClamAV daemon can handle ~1,800 scans/hour
    clamav_capacity = 1800

    assert total_scans_per_hour < clamav_capacity, (
        f"Rate limit should keep scan load under ClamAV capacity. "
        f"Expected load: {total_scans_per_hour}/hour, "
        f"Capacity: {clamav_capacity}/hour"
    )
