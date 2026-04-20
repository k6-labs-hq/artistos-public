"""
Rate limiting service for upload endpoints.

CRITICAL SECURITY: Prevents resource exhaustion attacks on file upload endpoints.

Without rate limiting:
- Malicious artists can spam uploads 24/7
- Storage costs spike uncontrollably (S3/disk)
- ClamAV scan queue overwhelms (CPU/memory)
- Database write saturation from ingestion
- Legitimate users unable to upload

With 10 uploads/hour/artist:
- Cost-predictable S3 storage growth
- ClamAV scan capacity protected
- Fair resource distribution
- Attack surface minimized
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import redis
from fastapi import HTTPException, status

from xr7_common.logging import get_logger
from xr7_common.settings import settings

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Rate limit configuration
UPLOAD_RATE_LIMIT_PER_ARTIST = 10  # uploads per window
UPLOAD_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds


def get_redis_client() -> redis.Redis:
    """Get Redis client for rate limiting."""
    return redis.from_url(settings.redis_url, decode_responses=True)


def check_upload_rate_limit(artist_id: str) -> None:
    """
    Check if artist has exceeded upload rate limit.

    Implements sliding window rate limiting using Redis:
    - Key: upload_rate_limit:{artist_id}
    - Value: Upload count in current window
    - TTL: 1 hour (3600 seconds)

    Args:
        artist_id: The artist ID to check

    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded

    Example:
        >>> check_upload_rate_limit("artist_123")  # First upload: OK
        >>> check_upload_rate_limit("artist_123")  # Second upload: OK
        >>> # ... 8 more uploads ...
        >>> check_upload_rate_limit("artist_123")  # 11th upload: raises 429
    """
    try:
        r = get_redis_client()
        key = f"upload_rate_limit:{artist_id}"

        current_count = r.get(key)

        if current_count is None:
            r.setex(key, UPLOAD_RATE_LIMIT_WINDOW, 1)
            return

        count = int(current_count)
        if count >= UPLOAD_RATE_LIMIT_PER_ARTIST:
            ttl = r.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Upload rate limit exceeded. Maximum {UPLOAD_RATE_LIMIT_PER_ARTIST} uploads "
                    f"per hour allowed. Please try again in {ttl // 60 + 1} minutes."
                ),
                headers={"Retry-After": str(ttl if ttl > 0 else UPLOAD_RATE_LIMIT_WINDOW)},
            )

        r.incr(key)
    except redis.RedisError as exc:
        logger.warning(
            "Upload rate limiter unavailable; allowing request",
            extra={"artist_id": artist_id, "error": str(exc)[:200]},
        )
        return


def increment_upload_count(artist_id: str) -> None:
    """
    Increment upload counter after successful upload.

    This is called AFTER the upload is processed to ensure we only
    count successful uploads, not failed validation attempts.

    Args:
        artist_id: The artist ID
    """
    try:
        r = get_redis_client()
        key = f"upload_rate_limit:{artist_id}"

        if r.get(key) is None:
            r.setex(key, UPLOAD_RATE_LIMIT_WINDOW, 1)
        else:
            r.incr(key)
    except redis.RedisError as exc:
        logger.warning(
            "Upload rate limiter unavailable during increment; skipping counter update",
            extra={"artist_id": artist_id, "error": str(exc)[:200]},
        )
        return


def get_remaining_uploads(artist_id: str) -> dict[str, int]:
    """
    Get remaining upload quota for an artist.

    Returns:
        Dictionary with:
        - remaining: Number of uploads remaining in current window
        - reset_in_seconds: Seconds until rate limit resets
        - limit: Total uploads allowed per window

    Example:
        >>> get_remaining_uploads("artist_123")
        {"remaining": 7, "reset_in_seconds": 2400, "limit": 10}
    """
    try:
        r = get_redis_client()
        key = f"upload_rate_limit:{artist_id}"

        current_count = r.get(key)
        if current_count is None:
            return {
                "remaining": UPLOAD_RATE_LIMIT_PER_ARTIST,
                "reset_in_seconds": UPLOAD_RATE_LIMIT_WINDOW,
                "limit": UPLOAD_RATE_LIMIT_PER_ARTIST,
            }

        count = int(current_count)
        ttl = r.ttl(key)

        return {
            "remaining": max(0, UPLOAD_RATE_LIMIT_PER_ARTIST - count),
            "reset_in_seconds": ttl if ttl > 0 else UPLOAD_RATE_LIMIT_WINDOW,
            "limit": UPLOAD_RATE_LIMIT_PER_ARTIST,
        }
    except redis.RedisError as exc:
        logger.warning(
            "Upload rate limiter unavailable while reading quota; returning full allowance",
            extra={"artist_id": artist_id, "error": str(exc)[:200]},
        )
        return {
            "remaining": UPLOAD_RATE_LIMIT_PER_ARTIST,
            "reset_in_seconds": UPLOAD_RATE_LIMIT_WINDOW,
            "limit": UPLOAD_RATE_LIMIT_PER_ARTIST,
        }


def reset_upload_rate_limit(artist_id: str) -> None:
    """
    Reset upload rate limit for an artist.

    Used for:
    - Admin overrides
    - Testing
    - Customer support escalations

    Args:
        artist_id: The artist ID to reset
    """
    try:
        r = get_redis_client()
        key = f"upload_rate_limit:{artist_id}"
        r.delete(key)
    except redis.RedisError as exc:
        logger.warning(
            "Upload rate limiter unavailable during reset; skipping delete",
            extra={"artist_id": artist_id, "error": str(exc)[:200]},
        )
        return
