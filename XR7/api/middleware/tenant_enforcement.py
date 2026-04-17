from __future__ import annotations

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from XR7.auth.jwt_service import JWTValidationError, jwt_service
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.base import SessionLocal
from XR7.services.tenant_context import reset_tenant_context, set_tenant_context

logger = logging.getLogger(__name__)


class TenantEnforcementMiddleware(BaseHTTPMiddleware):
    """Propagate JWT tenant context and block explicit cross-tenant attempts.

    Behavior:
    - If a bearer token is present and valid, extracts ``tenant_id`` and stores it
      in request-scoped contextvars for SQLAlchemy query filtering.
    - If the caller supplies ``X-Tenant-ID`` and it does not match the JWT
      ``tenant_id``, rejects with 403 and writes an AdminAuditLog entry.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    @staticmethod
    def _extract_bearer_token(request: Request) -> str:
        authz = request.headers.get("authorization", "")
        if not authz.lower().startswith("bearer "):
            return ""
        return authz[7:].strip()

    @staticmethod
    def _audit_cross_tenant_attempt(*, actor: str, tenant_jwt: str, tenant_header: str, request: Request) -> None:
        db = SessionLocal()
        try:
            db.add(
                AdminAuditLog(
                    actor=actor or "unknown",
                    action="cross_tenant_access_denied",
                    resource_type="tenant",
                    resource_id=tenant_header,
                    details={
                        "tenant_from_jwt": tenant_jwt,
                        "tenant_from_header": tenant_header,
                        "path": request.url.path,
                        "method": request.method,
                        "client": request.client.host if request.client else None,
                    },
                )
            )
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to persist cross-tenant audit log")
        finally:
            db.close()

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        token = self._extract_bearer_token(request)
        payload: dict | None = None
        if token:
            try:
                payload = jwt_service.verify_token(token)
            except JWTValidationError:
                # Auth dependency returns canonical 401 responses.
                payload = None

        tenant_id = ""
        actor_sub = ""
        if payload is not None:
            tenant_id = str(payload.get("tenant_id") or "").strip()
            actor_sub = str(payload.get("sub") or "").strip()

        header_tenant = request.headers.get("x-tenant-id", "").strip()
        if tenant_id and header_tenant and header_tenant != tenant_id:
            self._audit_cross_tenant_attempt(
                actor=actor_sub,
                tenant_jwt=tenant_id,
                tenant_header=header_tenant,
                request=request,
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Tenant mismatch between JWT and X-Tenant-ID header",
                    "tenant_id": tenant_id,
                },
            )

        context_tokens = set_tenant_context(tenant_id, actor_sub)
        request.state.tenant_id = tenant_id or None
        try:
            response = await call_next(request)
        finally:
            reset_tenant_context(context_tokens)

        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id
        return response
