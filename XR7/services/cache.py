"""Small Redis cache helpers for API endpoint response caching."""

from __future__ import annotations

import hashlib
import json
from functools import wraps
from typing import Any, Callable

from fastapi.encoders import jsonable_encoder

from xr7_common.settings import settings

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

_cache_client = None
if redis is not None:
    try:
        _cache_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        _cache_client = None


def _build_cache_key(prefix: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    payload = json.dumps({"args": args, "kwargs": kwargs}, default=str, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"xr7:cache:{prefix}:{digest}"


def cached_response(prefix: str, ttl_seconds: int = 120) -> Callable:
    """Cache pure endpoint responses in Redis by function args/kwargs."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _cache_client is None:
                return func(*args, **kwargs)

            key = _build_cache_key(prefix, args, kwargs)
            try:
                existing = _cache_client.get(key)
            except Exception:
                return func(*args, **kwargs)
            if existing:
                return json.loads(existing)

            result = func(*args, **kwargs)
            try:
                _cache_client.setex(key, ttl_seconds, json.dumps(jsonable_encoder(result), default=str))
            except Exception:
                pass
            return result

        return wrapper

    return decorator
