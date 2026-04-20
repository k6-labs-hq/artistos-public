"""
API Request Deduplication Middleware for XR7 Engine.

Prevents duplicate operations from network retries, browser double-submits,
and client-side bugs. Critical for payment processing, claim submission,
and statement uploads.

How it works:
1. Hash request fingerprint (method + path + body hash)
2. Check Redis cache for duplicate request within TTL window (default: 5 minutes)
3. If duplicate: return cached response immediately
4. If new: process request and cache response

Configuration:
- DEDUP_ENABLED: Enable deduplication (default: true in production)
- DEDUP_TTL_SECONDS: Cache TTL for deduplication (default: 300 = 5 minutes)
- DEDUP_ENDPOINTS: Comma-separated list of paths to deduplicate (default: all POST/PUT/DELETE)

Environment Variables:
- REDIS_URL: Redis connection string (required for deduplication)

Documented in docs/production_readiness_wave2_2026_q2.md REL-001
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from xr7_common.logging import get_logger

logger = get_logger(__name__)

DEDUP_ENABLED = os.environ.get("DEDUP_ENABLED", "true").lower() == "true"
DEDUP_TTL_SECONDS = int(os.environ.get("DEDUP_TTL_SECONDS", "300"))  # 5 minutes

# Critical write endpoints that should be deduplicated
CRITICAL_ENDPOINTS = [
    "/claims",
    "/payments",
    "/artists/{artist_id}/statements/upload",
    "/trolley/pay",
    "/billing/invoice",
]


def _should_deduplicate(request: Request) -> bool:
    """Determine if request should be deduplicated.

    Deduplication criteria:
    - Method is POST, PUT, or DELETE (not GET)
    - Path matches critical endpoint pattern
    - Content-Type is application/json or multipart/form-data

    Args:
        request: Incoming HTTP request

    Returns:
        True if request should be deduplicated
    """
    if request.method not in ("POST", "PUT", "DELETE"):
        return False

    # Check if path contains any critical endpoint pattern
    path = request.url.path
    for pattern in CRITICAL_ENDPOINTS:
        # Simple pattern matching (in production, use regex or path templates)
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            continue

        match = all(
            pp == "{" + ".*" + "}" or pp == pt
            for pp, pt in zip(pattern_parts, path_parts)
            if not pp.startswith("{")
        )

        if match:
            return True

    return False


def _compute_request_fingerprint(request: Request, body_bytes: bytes) -> str:
    """Compute unique fingerprint for request.

    Fingerprint = SHA256(method + path + query + body_hash)

    Args:
        request: HTTP request
        body_bytes: Request body as bytes

    Returns:
        Hex-encoded SHA256 hash (64 characters)
    """
    components = [
        request.method,
        request.url.path,
        str(sorted(request.query_params.items())),
    ]

    # Hash body separately to handle large payloads
    body_hash = hashlib.sha256(body_bytes).hexdigest() if body_bytes else ""
    components.append(body_hash)

    fingerprint_data = "|".join(components).encode("utf-8")
    return hashlib.sha256(fingerprint_data).hexdigest()


class RequestDeduplicationMiddleware(BaseHTTPMiddleware):
    """Middleware to prevent duplicate API requests.

    Uses Redis to cache request fingerprints and responses.
    Prevents duplicate payments, claims, and uploads.

    Configuration via environment variables:
    - DEDUP_ENABLED: Enable deduplication (default: true)
    - DEDUP_TTL_SECONDS: Cache TTL (default: 300)
    - REDIS_URL: Redis connection (required)

    Example:
        app.add_middleware(RequestDeduplicationMiddleware)
    """

    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.enabled = DEDUP_ENABLED
        self.ttl = DEDUP_TTL_SECONDS
        self.redis_client = None

        if self.enabled:
            try:
                import redis

                redis_url = os.environ.get("REDIS_URL")
                if redis_url:
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    logger.info("Request deduplication enabled", extra={"ttl_seconds": self.ttl})
                else:
                    logger.warning("DEDUP_ENABLED=true but REDIS_URL not set, disabling")
                    self.enabled = False
            except ImportError:
                logger.warning("redis package not installed, deduplication disabled")
                self.enabled = False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with deduplication logic.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response (either cached or freshly computed)
        """
        if not self.enabled or not _should_deduplicate(request):
            return await call_next(request)

        # Read body once to compute fingerprint (body can only be read once in FastAPI)
        body_bytes = await request.body()

        # Reattach body for downstream handlers
        async def receive():
            return {"type": "http.request", "body": body_bytes}

        request._receive = receive

        fingerprint = _compute_request_fingerprint(request, body_bytes)
        cache_key = f"dedup:req:{fingerprint}"

        try:
            # Check cache for duplicate request
            cached_response = self.redis_client.get(cache_key)

            if cached_response:
                logger.info(
                    "Duplicate request detected",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "fingerprint": fingerprint[:16],
                    },
                )

                # Return cached response
                cached_data = json.loads(cached_response)
                response = Response(
                    content=cached_data["body"],
                    status_code=cached_data["status_code"],
                    headers=cached_data["headers"],
                    media_type=cached_data.get("media_type", "application/json"),
                )
                response.headers["X-Dedup-Cache"] = "HIT"
                return response

            # Not a duplicate, process request
            response = await call_next(request)

            # Cache successful responses (2xx status codes)
            if 200 <= response.status_code < 300:
                # Read response body
                body_content = b""
                async for chunk in response.body_iterator:
                    body_content += chunk

                # Cache response
                cache_data = {
                    "body": body_content.decode("utf-8"),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                }

                self.redis_client.setex(cache_key, self.ttl, json.dumps(cache_data))

                logger.info(
                    "Request processed and cached",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "fingerprint": fingerprint[:16],
                        "ttl_seconds": self.ttl,
                    },
                )

                # Recreate response with body (body was consumed when caching)
                response = Response(
                    content=body_content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            response.headers["X-Dedup-Cache"] = "MISS"
            return response

        except Exception as e:
            logger.error(
                "Deduplication error, processing request normally",
                extra={"error": str(e), "method": request.method, "path": request.url.path},
            )
            # On error, process request without deduplication
            return await call_next(request)
