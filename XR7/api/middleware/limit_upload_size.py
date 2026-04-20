"""
Request body size limit middleware to prevent OOM attacks.

CRITICAL SECURITY: Prevents resource exhaustion from oversized request bodies.

Without body size limits:
- Malicious clients can send multi-GB payloads
- API workers run out of memory and crash
- Service becomes unavailable for legitimate users
- Cascading failures across pods/containers

With body size limits (100MB default):
- FastAPI rejects oversized payloads before reading into memory
- Workers remain stable under attack
- Predictable memory usage patterns
- Fair resource allocation

Issue #73: Add request body size limits to prevent OOM attacks
"""

from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp


class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce maximum request body size.
    
    Checks Content-Length header before request body is read into memory.
    Rejects requests exceeding max_upload_size with HTTP 413.
    
    Args:
        app: ASGI application
        max_upload_size: Maximum allowed request body size in bytes (default: 100MB)
    
    Example:
        >>> app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=104857600)
    """
    
    def __init__(self, app: ASGIApp, max_upload_size: int = 104857600):
        super().__init__(app)
        self.max_upload_size = max_upload_size
    
    async def dispatch(self, request: Request, call_next):
        """
        Check Content-Length header and reject oversized requests.
        
        Returns:
            Response: 413 Payload Too Large if Content-Length exceeds limit,
                     otherwise passes request to next middleware/handler.
        """
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                content_length_bytes = int(content_length)
                if content_length_bytes > self.max_upload_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": (
                                f"Request body too large. Maximum allowed: "
                                f"{self.max_upload_size // (1024 * 1024)}MB, "
                                f"received: {content_length_bytes // (1024 * 1024)}MB"
                            )
                        },
                        headers={"Connection": "close"}
                    )
            except ValueError:
                # Invalid Content-Length header - let FastAPI handle it
                pass
        
        response = await call_next(request)
        return response
