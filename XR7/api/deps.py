"""Shared FastAPI dependencies and helper utilities for all routers.

DOMAIN BOUNDARY NOTE:
    This module contains CANONICAL versions of common FastAPI operations.
    All API routers and application services should import from here to avoid
    duplication. This ensures consistent error handling and response formats
    across the API surface.

    Do NOT duplicate these functions in other modules. If you need similar
    functionality, either:
    1. Use this canonical version if you're in the API/service layer
    2. Create a separate domain-specific variant if you need different behavior
       (e.g., raising ValueError instead of HTTPException for pure business logic)
"""

from __future__ import annotations

import hmac
import os

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist


def get_current_admin(
    x_admin_key: str = Header(default="", alias="X-Admin-Key"),
    x_admin_actor: str | None = Header(default=None, alias="X-Admin-Actor"),
) -> dict[str, str | None]:
    """Validate admin API key and return admin context.

    CANONICAL VERSION: Do not duplicate this logic elsewhere in the codebase.
    All admin-protected endpoints requiring admin context should use this function.

    Args:
        x_admin_key: Admin key from X-Admin-Key header
        x_admin_actor: Optional admin actor identifier from X-Admin-Actor header

    Returns:
        Dict with admin context (sub, email, actor)

    Raises:
        HTTPException: 503 if admin key not configured, 401 if invalid
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

    return {
        "sub": "admin",
        "email": x_admin_actor or "admin@xr7.ai",
        "actor": x_admin_actor,
    }


def get_artist_or_404(artist_id: str, db: Session) -> Artist:
    """Fetch an artist by primary key or raise HTTP 404.

    CANONICAL VERSION: Do not duplicate this logic elsewhere in the codebase.
    All API routes and application services should use this function.

    Args:
        artist_id: The artist's unique identifier (UUID string)
        db: SQLAlchemy database session

    Returns:
        Artist: The artist record

    Raises:
        HTTPException: 404 if artist not found

    Domain Boundary:
        - For API routes: Use this directly
        - For background jobs/services: Use this or extract to a shared service layer
        - For pure domain logic: Consider raising ValueError instead and catching
          at the API boundary
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist
