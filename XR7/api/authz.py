from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.models.artist import Artist
from XR7.models.team_access import TeamMember, TeamRole


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
