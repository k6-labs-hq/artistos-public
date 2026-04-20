"""Simple in-memory caching service for API responses.

Provides decorator-based response caching with TTL (time-to-live) support.
Reduces database load for frequently accessed, slow-changing data.

TODO: Replace with Redis/ElastiCache for production multi-instance deployments.
Current implementation is in-process only and does not share cache across workers.
"""

from __future__ import annotations

import functools
import hashlib
import json
import time
from typing import Any, Callable

from xr7_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# In-memory cache store
# ---------------------------------------------------------------------------


class _CacheEntry:
    """Cache entry with value and expiration timestamp."""

    def __init__(self, value: Any, expires_at: float) -> None:
        self.value = value
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


class _InMemoryCache:
    """Thread-unsafe in-memory cache with TTL support.

    NOTE: This is a simple MVP implementation. For production:
    - Use Redis for distributed caching across workers
    - Add cache warming strategies
    - Implement cache invalidation events
    - Add cache hit/miss metrics
    """

    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self._store:
            self._misses += 1
            return None

        entry = self._store[key]

        if entry.is_expired():
            # Lazy expiration: remove on access
            del self._store[key]
            self._evictions += 1
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        expires_at = time.time() + ttl_seconds
        self._store[key] = _CacheEntry(value, expires_at)

    def delete(self, key: str) -> None:
        """Delete key from cache.

        Args:
            key: Cache key to delete
        """
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._store)
        self._store.clear()
        logger.info("cache_cleared", extra={"entries_cleared": count})

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict with hits, misses, size, hit rate
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "size": len(self._store),
            "hit_rate": hit_rate,
        }


# Global cache instance
_cache = _InMemoryCache()


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def cached_response(cache_key: str, ttl_seconds: int = 60) -> Callable:
    """Decorator to cache API response with TTL.

    Caches the result of the decorated function based on a generated key
    that includes the cache_key prefix and function arguments.

    Args:
        cache_key: Cache key prefix (e.g., "earnings_summary")
        ttl_seconds: Time-to-live in seconds (default: 60)

    Returns:
        Decorator function

    Example::

        @router.get("/artists/{artist_id}/earnings")
        @cached_response("earnings_summary", ttl_seconds=120)
        def get_earnings(artist_id: str, db: Session = Depends(get_db)):
            # Expensive database query here
            return {"artist_id": artist_id, "total": 5000.0}

    Notes:
        - Cache key includes function name and serialized arguments
        - Only caches on successful execution (no exceptions)
        - Does NOT cache based on request headers or user identity
        - For production, replace with Redis and add cache invalidation
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Build cache key from function and arguments
            # Include positional args (skip 'self' if present) and keyword args
            func_args = args[1:] if args and hasattr(args[0], "__dict__") else args

            # Serialize args for cache key (ignore db sessions, request objects)
            serializable_kwargs = {
                k: v
                for k, v in kwargs.items()
                if not (
                    k == "db"  # Skip database session
                    or k.startswith("_")  # Skip internal params
                    or callable(v)  # Skip callables
                )
            }

            args_str = json.dumps(
                {
                    "args": [str(a) for a in func_args],
                    "kwargs": serializable_kwargs,
                },
                sort_keys=True,
            )

            # Hash to keep key length manageable
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            full_key = f"{cache_key}:{func.__name__}:{args_hash}"

            # Try to get from cache
            cached_value = _cache.get(full_key)
            if cached_value is not None:
                logger.debug(
                    "cache_hit",
                    extra={
                        "cache_key": cache_key,
                        "full_key": full_key,
                        "ttl_seconds": ttl_seconds,
                    },
                )
                return cached_value

            # Cache miss: execute function
            logger.debug(
                "cache_miss",
                extra={
                    "cache_key": cache_key,
                    "full_key": full_key,
                },
            )

            result = func(*args, **kwargs)

            # Store in cache
            _cache.set(full_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


def invalidate_cache(cache_key: str | None = None) -> None:
    """Invalidate cache entries.

    Args:
        cache_key: Specific key prefix to invalidate, or None to clear all

    TODO: Implement prefix-based invalidation for targeted cache clearing
    """
    if cache_key is None:
        _cache.clear()
    else:
        # TODO: Implement prefix-based invalidation
        # For now, just clear everything
        logger.warning(
            "cache_invalidation_requested_but_clearing_all",
            extra={"requested_key": cache_key},
        )
        _cache.clear()


def get_cache_stats() -> dict:
    """Get cache statistics for monitoring.

    Returns:
        Dict with cache hits, misses, size, hit rate
    """
    return _cache.get_stats()
