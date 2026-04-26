"""Supabase Auth integration.

Supabase projects created after ~2026 sign tokens with asymmetric keys
(ES256 by default) and publish the public key at
``{SUPABASE_URL}/auth/v1/.well-known/jwks.json``. Older projects still
sign with a shared HS256 secret. This module verifies both by inspecting
the token header's ``alg`` / ``kid`` and picking the right key source.

Flow:
    1. Client obtains a JWT from Supabase (email+password, magic link, OAuth).
    2. Client calls our API with `Authorization: Bearer <supabase_jwt>`.
    3. We verify the signature + claims with `verify_supabase_jwt`.
    4. We look up the Artist by `supabase_user_id` or provision on first login.
    5. We attach the resolved identity to the request context.

Environment variables:
    SUPABASE_URL               — e.g. https://xxxxx.supabase.co (required for JWKS)
    SUPABASE_JWT_SECRET        — legacy HS256 secret (optional; only needed for
                                 projects still using HS256 signing)
    SUPABASE_JWT_AUDIENCE      — default "authenticated"
    SUPABASE_JWT_ISSUER        — default "{SUPABASE_URL}/auth/v1"
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.base import get_db

# Supported asymmetric algorithms. HS256 is handled separately with the
# shared secret path.
_ASYMMETRIC_ALGORITHMS = ("ES256", "RS256", "EdDSA")


class SupabaseAuthError(ValueError):
    pass


_bearer_scheme = HTTPBearer(auto_error=False)


def _get_supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    if not url:
        raise SupabaseAuthError("SUPABASE_URL is not configured.")
    return url


def _get_supabase_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET", "").strip()
    if not secret:
        raise SupabaseAuthError(
            "SUPABASE_JWT_SECRET is not configured. This project appears to use "
            "HS256 signing — set it from Supabase Settings → API → JWT Secret, or "
            "switch the project to asymmetric (ES256/RS256) signing keys."
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


@lru_cache(maxsize=4)
def _jwk_client(supabase_url: str) -> jwt.PyJWKClient:
    """Cached JWKS client (one per Supabase URL). Handles key rotation via
    its own internal cache TTL."""
    return jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")


def _resolve_signing_key(token: str) -> tuple[str | Any, str]:
    """Return ``(key, algorithm)`` used to verify ``token``.

    For asymmetric algorithms, fetch the key from the project's JWKS using
    the token's ``kid``. For HS256, use the configured shared secret. In
    either case the algorithm is chosen from the token header so a compromised
    header cannot downgrade us — the allowed set is restricted by caller.
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Supabase token: {exc}") from exc

    algorithm = str(header.get("alg") or "").upper()
    if algorithm in _ASYMMETRIC_ALGORITHMS:
        try:
            url = _get_supabase_url()
        except SupabaseAuthError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        try:
            signing_key = _jwk_client(url).get_signing_key_from_jwt(token)
        except jwt.PyJWKClientError as exc:
            raise HTTPException(
                status_code=401, detail=f"Unable to resolve JWKS signing key: {exc}"
            ) from exc
        return signing_key.key, algorithm
    if algorithm == "HS256":
        try:
            return _get_supabase_secret(), "HS256"
        except SupabaseAuthError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    raise HTTPException(status_code=401, detail=f"Unsupported JWT algorithm: {algorithm}")


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Validate a Supabase-issued JWT and return its claims.

    Raises HTTPException(401) on any validation failure.
    """
    key, algorithm = _resolve_signing_key(token)

    options: dict[str, Any] = {}
    kwargs: dict[str, Any] = {
        "algorithms": [algorithm],
        "audience": _get_audience(),
    }
    issuer = _get_issuer()
    if issuer:
        kwargs["issuer"] = issuer
    else:
        options["verify_iss"] = False

    try:
        claims = jwt.decode(token, key, options=options or None, **kwargs)
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
