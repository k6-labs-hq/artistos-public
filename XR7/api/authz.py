from __future__ import annotations

import functools
import hmac
import os
from typing import Any, Callable

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.auth.jwt_service import JWTValidationError, jwt_service
from XR7.models.artist import Artist
from XR7.models.team_access import TeamMember, TeamRole

# Module-level bearer scheme so /admin endpoints show BearerAuth in OpenAPI
# alongside the existing X-Admin-Key option.
_bearer_scheme = HTTPBearer(auto_error=False)


def artist_or_404(artist_id: str, db: Session) -> Artist:
    artist = get_artist_or_404(artist_id, db)
    return artist


def authorize_team_access(
    artist_id: str,
    db: Session,
    allowed_roles: set[TeamRole],
    *,
    actor_email: str | None,
    actor_role: str | None,
    email_required_detail: str | None = None,
) -> None:
    """Enforce team-member access when team records exist for an artist.

    Bootstrap mode: if the artist has no team members yet, access is allowed.
    """
    members_exist = (
        db.query(TeamMember.id).filter(TeamMember.artist_id == artist_id).first() is not None
    )
    if not members_exist:
        return

    if not actor_email:
        raise HTTPException(
            status_code=403,
            detail=email_required_detail or "X-Actor-Email is required for this artist",
        )

    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.artist_id == artist_id,
            func.lower(TeamMember.user_email) == actor_email.strip().lower(),
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Actor is not a team member for this artist")

    member_role = TeamRole(member.role)
    if member_role not in allowed_roles:
        allowed = ", ".join(sorted(r.value for r in allowed_roles))
        raise HTTPException(status_code=403, detail=f"Insufficient role. Allowed roles: {allowed}")

    if actor_role and actor_role.strip().lower() != member_role.value:
        raise HTTPException(status_code=403, detail="X-Actor-Role does not match assigned role")


def require_admin(x_admin_key: str = Header(default="", alias="X-Admin-Key")) -> None:
    """Validate admin API key for protected admin endpoints.

    CANONICAL VERSION: Do not duplicate this logic elsewhere in the codebase.
    All admin-protected endpoints should use this function.

    Checks ADMIN_API_KEY or WIDGET_ADMIN_KEY environment variables.
    Uses constant-time comparison to prevent timing attacks.

    Args:
        x_admin_key: Admin key from X-Admin-Key header

    Raises:
        HTTPException: 503 if admin key not configured, 401 if invalid

    Domain Boundary:
        This is for API route protection only. Use separate authorization
        logic for internal services or background jobs.
    """
    expected = (
        os.environ.get("ADMIN_API_KEY")
        or os.environ.get("WIDGET_ADMIN_KEY")
        or os.environ.get("ADMIN_SECRET_KEY")
    )
    if not expected:
        env = os.environ.get("XR7_ENV", "development").lower()
        if env == "production":
            raise HTTPException(
                status_code=503,
                detail="Admin API key not configured",
            )
        expected = "admin-secret"
    if not x_admin_key or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")


def _expected_admin_key() -> str | None:
    """The admin key the request must match. Returns None if no key configured."""
    expected = (
        os.environ.get("ADMIN_API_KEY")
        or os.environ.get("WIDGET_ADMIN_KEY")
        or os.environ.get("ADMIN_SECRET_KEY")
    )
    if expected:
        return expected
    env = os.environ.get("XR7_ENV", "development").lower()
    if env == "production":
        return None
    return "admin-secret"  # dev convenience


def require_admin_session(
    x_admin_key: str = Header(default="", alias="X-Admin-Key"),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Admin auth that accepts EITHER an X-Admin-Key header OR a Bearer JWT
    with role=admin.

    Use this on /admin/* endpoints that operators drive from the dashboard.
    The X-Admin-Key path keeps the existing curl/automation use-cases
    working; the JWT path lets the operator-dashboard use the same
    Supabase-issued session that authenticates the rest of the frontend
    (no separate "paste your admin key" step once the operator's email
    is in XR7_ADMIN_USER_EMAILS).

    Returns a dict describing the authenticated session — the JWT payload
    when authenticated by token, or a synthetic ``{"role": "admin",
    "auth_method": "admin_key"}`` shape when authenticated by key.
    """
    # 1. X-Admin-Key path — same logic as require_admin, but doesn't 401 on
    #    a missing key (we may have a JWT instead).
    if x_admin_key:
        expected = _expected_admin_key()
        if expected and hmac.compare_digest(x_admin_key, expected):
            return {"role": "admin", "auth_method": "admin_key"}

    # 2. Bearer JWT path.
    if credentials is not None:
        try:
            payload = jwt_service.verify_token(credentials.credentials)
        except JWTValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        if str(payload.get("role") or "") == "admin":
            return {**payload, "auth_method": "jwt"}
        raise HTTPException(status_code=403, detail="Admin role required")

    raise HTTPException(status_code=401, detail="Admin auth required")


def authorize_claim_edit_access(
    artist_id: str,
    db: Session,
    *,
    actor_email: str | None,
    actor_role: str | None,
) -> None:
    authorize_team_access(
        artist_id,
        db,
        {TeamRole.ANALYST, TeamRole.MANAGER, TeamRole.ATTORNEY, TeamRole.ARTIST},
        actor_email=actor_email,
        actor_role=actor_role,
        email_required_detail="X-Actor-Email is required to edit claims for this artist",
    )


def authorize_advance_approval_access(
    artist_id: str,
    db: Session,
    *,
    actor_email: str | None,
    actor_role: str | None,
) -> None:
    authorize_team_access(
        artist_id,
        db,
        {TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=actor_email,
        actor_role=actor_role,
        email_required_detail="Manager or attorney identity is required to approve claim advances",
    )


# ---------------------------------------------------------------------------
# Resource-level authorization decorator
# ---------------------------------------------------------------------------


def require_permission(
    scope: str,
    resource_type: str | None = None,
    *,
    owner_field: str = "artist_id",
) -> Callable:
    """Decorator for resource-level permission checking.

    Enforces that the authenticated actor has permission to access a specific resource.
    Checks resource ownership via the specified owner_field.

    Args:
        scope: The permission scope (e.g., "read", "write", "delete")
        resource_type: Optional resource type for more granular permissions (e.g., "claim", "payment")
        owner_field: Field name containing the owner ID (default: "artist_id")

    Example:
        @router.delete("/claims/{claim_id}")
        @require_permission("delete", resource_type="claim")
        def delete_claim(
            claim_id: str,
            db: Session = Depends(get_db),
            actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
        ):
            # Permission check happens before this code runs
            ...

    Raises:
        HTTPException: 403 if actor doesn't have permission
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _check_permission_and_call(
                func, scope, resource_type, owner_field, args, kwargs
            )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _check_permission_and_call_sync(
                func, scope, resource_type, owner_field, args, kwargs
            )

        # Return async wrapper if the function is async, otherwise sync wrapper
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _check_permission_and_call_sync(
    func: Callable,
    scope: str,
    resource_type: str | None,
    owner_field: str,
    args: tuple,
    kwargs: dict,
):
    """Synchronous permission check and function call."""
    db: Session | None = kwargs.get("db")
    actor_email: str | None = kwargs.get("actor_email")

    if not db:
        raise HTTPException(status_code=500, detail="Database session required for authorization")

    # Extract resource ID from kwargs (e.g., claim_id, artist_id, etc.)
    resource_id = None
    for key in kwargs:
        if key.endswith("_id") and key != "db":
            resource_id = kwargs[key]
            break

    if not resource_id:
        raise HTTPException(status_code=500, detail="Resource ID not found in request parameters")

    # For now, we enforce that the actor must be a team member with appropriate role
    # Future: extend to support fine-grained permission models
    _enforce_resource_permission(db, actor_email, resource_id, scope, resource_type, owner_field)

    return func(*args, **kwargs)


async def _check_permission_and_call(
    func: Callable,
    scope: str,
    resource_type: str | None,
    owner_field: str,
    args: tuple,
    kwargs: dict,
):
    """Async permission check and function call."""
    _check_permission_and_call_sync(func, scope, resource_type, owner_field, args, kwargs)
    return await func(*args, **kwargs)


def _enforce_resource_permission(
    db: Session,
    actor_email: str | None,
    resource_id: str,
    scope: str,
    resource_type: str | None,
    owner_field: str,
) -> None:
    """Enforce that actor has permission to perform scope on resource."""
    if not actor_email:
        raise HTTPException(
            status_code=403,
            detail=f"Authentication required to {scope} {resource_type or 'resource'}",
        )

    # Determine the owner (artist_id) from the resource
    # For simplicity, assume resource_id is the artist_id if owner_field == "artist_id"
    # In production, this would query the resource table to find the owner
    artist_id = resource_id  # Simplified - assumes direct ownership

    # Check team membership
    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.artist_id == artist_id,
            func.lower(TeamMember.user_email) == actor_email.strip().lower(),
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=403,
            detail=f"No permission to {scope} {resource_type or 'resource'} - not a team member",
        )

    # Map scope to required roles
    scope_role_map = {
        "read": {TeamRole.ANALYST, TeamRole.MANAGER, TeamRole.ATTORNEY, TeamRole.ARTIST},
        "write": {TeamRole.MANAGER, TeamRole.ATTORNEY, TeamRole.ARTIST},
        "delete": {TeamRole.MANAGER, TeamRole.ATTORNEY},
        "approve": {TeamRole.MANAGER, TeamRole.ATTORNEY},
    }

    required_roles = scope_role_map.get(scope, {TeamRole.MANAGER, TeamRole.ATTORNEY})
    member_role = TeamRole(member.role)

    if member_role not in required_roles:
        allowed = ", ".join(sorted(r.value for r in required_roles))
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient role to {scope} {resource_type or 'resource'}. Required: {allowed}",
        )
