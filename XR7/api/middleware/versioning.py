"""API versioning middleware stub."""

from starlette.middleware.base import BaseHTTPMiddleware


class APIVersioningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)
