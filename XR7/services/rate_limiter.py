from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from fastapi import HTTPException
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Rate limiting configuration constants
UPLOAD_RATE_LIMIT_REQUESTS = 10
UPLOAD_RATE_LIMIT_WINDOW_SECONDS = 300
UPLOAD_RATE_LIMIT_PER_ARTIST = UPLOAD_RATE_LIMIT_REQUESTS  # Alias for backward compatibility
UPLOAD_RATE_LIMIT_WINDOW = UPLOAD_RATE_LIMIT_WINDOW_SECONDS  # Alias for backward compatibility


class _RateLimitBucket:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self.lock = Lock()
    def is_allowed(self):
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            self.requests = [ts for ts in self.requests if ts > cutoff]
            if len(self.requests) >= self.max_requests:
                return False, 0
            self.requests.append(now)
            return True, self.max_requests - len(self.requests)

class _InMemoryRateLimiter:
    def __init__(self):
        self._buckets = defaultdict(lambda: _RateLimitBucket(UPLOAD_RATE_LIMIT_REQUESTS, UPLOAD_RATE_LIMIT_WINDOW_SECONDS))
    def check_rate_limit(self, key):
        return self._buckets[key].is_allowed()

_rate_limiter = _InMemoryRateLimiter()

def check_upload_rate_limit(artist_id):
    allowed, remaining = _rate_limiter.check_rate_limit(f'upload:{artist_id}')
    if not allowed:
        logger.warning('upload_rate_limit_exceeded', extra={'artist_id': artist_id})
        raise HTTPException(status_code=429, detail=f'Upload rate limit exceeded. Maximum {UPLOAD_RATE_LIMIT_REQUESTS} uploads per {UPLOAD_RATE_LIMIT_WINDOW_SECONDS} seconds.', headers={'Retry-After': str(UPLOAD_RATE_LIMIT_WINDOW_SECONDS)})


def get_remaining_uploads(artist_id):
    """Get remaining upload allowance for an artist."""
    bucket = _rate_limiter._buckets.get(f'upload:{artist_id}')
    if not bucket:
        return UPLOAD_RATE_LIMIT_REQUESTS
    with bucket.lock:
        now = time.time()
        cutoff = now - bucket.window_seconds
        bucket.requests = [ts for ts in bucket.requests if ts > cutoff]
        return bucket.max_requests - len(bucket.requests)


def increment_upload_count(artist_id):
    """Manually increment upload count for an artist."""
    key = f'upload:{artist_id}'
    bucket = _rate_limiter._buckets[key]
    with bucket.lock:
        bucket.requests.append(time.time())


def reset_upload_rate_limit(artist_id):
    """Reset upload rate limit for an artist (testing/admin use)."""
    key = f'upload:{artist_id}'
    if key in _rate_limiter._buckets:
        del _rate_limiter._buckets[key]

