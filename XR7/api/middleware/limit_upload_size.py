"""Middleware to limit request body size and prevent OOM from large uploads."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces a maximum request body size to prevent OOM.

    Checks the Content-Length header and rejects requests exceeding the limit
    before reading the body into memory. This prevents malicious or accidental
    large file uploads from exhausting server resources.

    Args:
        app: The ASGI application.
        max_upload_size: Maximum request body size in bytes (default: 100MB).

    Returns:
        JSONResponse with 413 status if Content-Length exceeds limit.

    Note:
        This middleware should be added early in the middleware stack, before
        any middleware that reads the request body.
    """

    def __init__(self, app: ASGIApp, max_upload_size: int = 104857600) -> None:
        """
        Initialize the upload size limiter.

        Args:
            app: The ASGI application.
            max_upload_size: Maximum size in bytes (default: 100MB = 104857600).
        """
        super().__init__(app)
        self._max_upload_size = int(max_upload_size)

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        """
        Check Content-Length header and reject oversized requests.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.

        Returns:
            Response from the next handler if size is acceptable,
            or JSONResponse with 413 status if too large.
        """
        content_length = request.headers.get("content-length")

        if content_length is not None:
            try:
                content_length_bytes = int(content_length)
                if content_length_bytes > self._max_upload_size:
                    max_mb = self._max_upload_size / (1024 * 1024)
                    actual_mb = content_length_bytes / (1024 * 1024)
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": (
                                f"Request body too large. Maximum allowed: {max_mb:.1f} MB, "
                                f"received: {actual_mb:.1f} MB. For large files, use multipart "
                                f"upload or contact support for alternatives."
                            )
                        },
                    )
            except ValueError:
                # Content-Length header is invalid, let request proceed
                # and let validation/body parsing handle it
                pass

        return await call_next(request)
