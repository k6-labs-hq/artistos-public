"""Structured JSON logging middleware with request_id propagation.

Every inbound HTTP request is assigned a unique ``request_id`` (UUID4) which
is:
  - added to the request state (``request.state.request_id``)
  - injected into log records as the ``request_id`` field via contextvars
  - returned in the ``X-Request-ID`` response header

Downstream code can retrieve the current request_id with::

    from XR7.api.middleware.logging import request_id_var
    rid = request_id_var.get("")
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# ContextVar that holds the current request_id for the duration of a request.
# Down-stream code (tasks, services, etc.) can read this at any time.
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

_TRACEPARENT_RE = re.compile(
    r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$",
    flags=re.IGNORECASE,
)


def _trace_id_from_header(traceparent: str | None, fallback_request_id: str) -> str:
    if traceparent:
        match = _TRACEPARENT_RE.match(traceparent.strip())
        if match:
            return match.group(1).lower()

    fallback = fallback_request_id.replace("-", "").strip().lower()
    if len(fallback) >= 32:
        return fallback[:32]
    return uuid.uuid4().hex


class _StructuredLogFilter(logging.Filter):
    """Inject request and trace context into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("")  # type: ignore[attr-defined]
        record.trace_id = trace_id_var.get("")  # type: ignore[attr-defined]
        return True


def configure_structured_logging() -> None:
    """Install JSON formatter and request_id filter on the root logger.

    Called once at application startup.
    """
    root = logging.getLogger()
    if any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        # Already configured — add filter to existing handlers
        for handler in root.handlers:
            handler.addFilter(_StructuredLogFilter())
        return

    handler = logging.StreamHandler()
    handler.addFilter(_StructuredLogFilter())

    class _JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload: dict = {
                "ts": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
                "request_id": getattr(record, "request_id", ""),
                "trace_id": getattr(record, "trace_id", ""),
            }
            if record.exc_info:
                payload["exc"] = self.formatException(record.exc_info)
            # Preserve any extras the caller passed
            for key, val in record.__dict__.items():
                if key not in logging.LogRecord.__dict__ and key not in payload:
                    payload[key] = val
            return json.dumps(payload)

    handler.setFormatter(_JSONFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that stamps every request with a unique request_id.

    Usage (in app.py)::

        from XR7.api.middleware.logging import RequestIDMiddleware
        app.add_middleware(RequestIDMiddleware)
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self._header_name = header_name
        self._trace_header_name = "X-Trace-ID"

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        # Honour a caller-supplied request_id (e.g. from an API gateway) or
        # generate a fresh one.
        request_id = request.headers.get(self._header_name) or str(uuid.uuid4())
        trace_id = _trace_id_from_header(request.headers.get("traceparent"), request_id)
        request_token = request_id_var.set(request_id)
        trace_token = trace_id_var.set(trace_id)
        request.state.request_id = request_id
        request.state.trace_id = trace_id

        logger = logging.getLogger("xr7.access")
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed = time.perf_counter() - start
            logger.exception(
                "Unhandled error",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(elapsed * 1000, 1),
                },
            )
            raise
        finally:
            trace_id_var.reset(trace_token)
            request_id_var.reset(request_token)

        elapsed = time.perf_counter() - start
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(elapsed * 1000, 1),
            },
        )
        response.headers[self._header_name] = request_id
        response.headers[self._trace_header_name] = trace_id
        response.headers["traceparent"] = f"00-{trace_id}-{uuid.uuid4().hex[:16]}-01"
        return response
