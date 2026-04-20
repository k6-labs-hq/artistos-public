"""HTTP idempotency middleware for POST endpoints.

This middleware implements lightweight idempotency support using Redis.
Requests that include an ``Idempotency-Key`` header are deduplicated on:
  - HTTP method
  - request path
  - request body hash

If a matching in-flight/completed request exists, the middleware returns the
cached response payload and status code.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from xr7_common.settings import settings

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Deduplicate POST requests that provide an Idempotency-Key header."""

    def __init__(self, app: ASGIApp, ttl_seconds: int = 3600) -> None:
        super().__init__(app)
        self._ttl_seconds = ttl_seconds
        self._redis = None
        if redis is not None:
            try:
                self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            except Exception:
                self._redis = None

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if request.method.upper() != "POST" or self._redis is None:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        if not idempotency_key:
            return await call_next(request)

        body_bytes = await request.body()
        body_hash = hashlib.sha256(body_bytes).hexdigest()
        redis_key = f"xr7:idempotency:{request.url.path}:{idempotency_key}:{body_hash}"

        existing = self._redis.get(redis_key)
        if existing:
            cached = json.loads(existing)
            return JSONResponse(
                status_code=int(cached.get("status_code", 200)),
                content=cached.get("body", {}),
                headers={"X-Idempotent-Replayed": "true"},
            )

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request = Request(request.scope, receive=receive)
        response = await call_next(request)

        # Cache only successful JSON responses
        if 200 <= response.status_code < 300:
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            raw_body = b"".join(chunks)
            payload: Any
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except Exception:
                payload = {"raw": raw_body.decode("utf-8", errors="ignore")}

            self._redis.setex(
                redis_key,
                self._ttl_seconds,
                json.dumps({"status_code": response.status_code, "body": payload}),
            )
            return JSONResponse(status_code=response.status_code, content=payload)

        return response
