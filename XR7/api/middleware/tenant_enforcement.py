"""Tenant enforcement middleware stub."""

from starlette.middleware.base import BaseHTTPMiddleware


class TenantEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)
