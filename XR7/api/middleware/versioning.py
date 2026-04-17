from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class APIVersioningMiddleware(BaseHTTPMiddleware):
    """Support `/v1/*` paths without duplicating router registration."""

    def __init__(self, app: ASGIApp, supported_version: str = "v1") -> None:
        super().__init__(app)
        self._supported_prefix = f"/{supported_version}"

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        path = request.scope.get("path") or ""
        is_versioned = path == self._supported_prefix or path.startswith(f"{self._supported_prefix}/")
        if is_versioned:
            request.scope["path"] = path[len(self._supported_prefix) :] or "/"

        response = await call_next(request)
        response.headers["X-API-Version"] = "v1"
        response.headers["Deprecation"] = "false" if is_versioned else "true"
        if not is_versioned:
            response.headers["Sunset"] = "Wed, 31 Dec 2026 23:59:59 GMT"
            response.headers["Link"] = '</v1>; rel="successor-version"'
        return response