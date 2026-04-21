"""Supabase Auth integration (stub for MVP).

Supabase-issued JWTs are HS256 signed with the Supabase project JWT secret
(Settings → API → JWT Settings → JWT Secret). We validate tokens locally
using that secret — no round-trip to Supabase needed.

Flow:
    1. Client obtains a JWT from Supabase (email+password, magic link, OAuth).
    2. Client calls our API with `Authorization: Bearer <supabase_jwt>`.
    3. We verify the signature + claims with `verify_supabase_jwt`.
    4. We look up the Artist by `supabase_user_id` or provision on first login.
    5. We attach the resolved identity to the request context.

Environment variables:
    SUPABASE_URL               — e.g. https://xxxxx.supabase.co
    SUPABASE_JWT_SECRET        — shared HS256 secret
    SUPABASE_JWT_AUDIENCE      — default "authenticated"
    SUPABASE_JWT_ISSUER        — default "{SUPABASE_URL}/auth/v1"
"""

from __future__ import annotations

import os
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.base import get_db


class SupabaseAuthError(ValueError):
    pass


_bearer_scheme = HTTPBearer(auto_error=False)


def _get_supabase_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
    if not secret:
        raise SupabaseAuthError(
            "SUPABASE_JWT_SECRET is not configured. "
            "Set it from Supabase project Settings → API → JWT Secret."
        )
    return secret


def _get_audience() -> str:
    return os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated").strip() or "authenticated"


def _get_issuer() -> str | None:
    explicit = os.environ.get("SUPABASE_JWT_ISSUER", "").strip()
    if explicit:
        return explicit
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    return f"{url}/auth/v1" if url else None


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Validate a Supabase-issued JWT and return its claims.

    Raises HTTPException(401) on any validation failure.
    """
    try:
        secret = _get_supabase_secret()
    except SupabaseAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    options: dict[str, Any] = {}
    kwargs: dict[str, Any] = {
        "algorithms": ["HS256"],
        "audience": _get_audience(),
    }
    issuer = _get_issuer()
    if issuer:
        kwargs["issuer"] = issuer
    else:
        options["verify_iss"] = False

    try:
        claims = jwt.decode(token, secret, options=options or None, **kwargs)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Supabase token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase token: {exc}") from exc

    if not claims.get("sub"):
        raise HTTPException(status_code=401, detail="Supabase token missing subject")

    return claims


def get_supabase_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """FastAPI dependency: validate bearer token as a Supabase JWT."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return verify_supabase_jwt(credentials.credentials)


def resolve_artist_from_claims(claims: dict[str, Any], db: Session) -> Artist | None:
    """Look up the XR7 Artist that corresponds to a Supabase user.

    Returns None if no Artist is linked yet (first login — caller decides
    whether to auto-provision or require pre-onboarding).
    """
    supabase_uid = str(claims.get("sub") or "")
    if not supabase_uid:
        return None

    # Primary: match by supabase_user_id column.
    artist = (
        db.query(Artist).filter(Artist.supabase_user_id == supabase_uid).first()
        if hasattr(Artist, "supabase_user_id")
        else None
    )
    if artist:
        return artist

    # Fallback during migration: match by email claim.
    email = str(claims.get("email") or "").strip().lower()
    if email:
        return (
            db.query(Artist)
            .filter(Artist.email.isnot(None))
            .filter(Artist.email.ilike(email))
            .first()
        )
    return None


def get_current_artist(
    claims: dict[str, Any] = Depends(get_supabase_claims),
    db: Session = Depends(get_db),
) -> Artist:
    """FastAPI dependency: resolve the authenticated artist or 403.

    For MVP: artists must be pre-onboarded (manual). Auto-provisioning
    can be added later by flipping this to upsert on first login.
    """
    artist = resolve_artist_from_claims(claims, db)
    if artist is None:
        raise HTTPException(
            status_code=403,
            detail=(
                "Authenticated Supabase user is not linked to an XR7 Artist record. "
                "Contact your admin to complete onboarding."
            ),
        )
    return artist
