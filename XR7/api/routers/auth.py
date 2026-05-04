from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.auth.jwt_service import JWTValidationError, jwt_service
from XR7.auth.supabase import (
    get_supabase_claims,
    resolve_artist_from_claims,
)
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["auth"])

# Shared HTTPBearer scheme — auto-injects BearerAuth securityScheme into the OpenAPI spec
# for every endpoint that depends on get_auth_payload or get_optional_auth_payload.
_bearer_scheme = HTTPBearer(auto_error=False)

# When XR7_ENFORCE_AUTH_GLOBALLY=1, soft-guarded endpoints reject unauthenticated requests.
_ENFORCE_AUTH_GLOBALLY = os.environ.get("XR7_ENFORCE_AUTH_GLOBALLY", "0").strip() == "1"
_DEFAULT_TENANT_ID = os.environ.get("XR7_DEFAULT_TENANT_ID", "default").strip() or "default"


def _admin_email_allowlist() -> set[str]:
    """Bootstrap allowlist of email addresses that get role=admin on sign-in.

    Read from ``XR7_ADMIN_USER_EMAILS`` (comma-separated). Lowercased.

    Why an env-var allowlist and not a DB table: there are 1-3 admins for
    the entire closed beta. Putting them in env keeps the bootstrap problem
    simple — no chicken-and-egg of "you need an admin to add admins."

    When the company has more than ~5 admins or admin assignments change
    during the beta, swap this for a `users.role` column with admin-only
    CRUD. Until then, env is the right shape.
    """
    raw = os.environ.get("XR7_ADMIN_USER_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def _is_admin_email(email: str | None) -> bool:
    if not email:
        return False
    return email.strip().lower() in _admin_email_allowlist()


def get_auth_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """Strict bearer-auth dependency. Raises 401 if the token is absent or invalid."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return jwt_service.verify_token(credentials.credentials)
    except JWTValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def get_optional_auth_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict[str, Any] | None:
    """Soft bearer-auth dependency for staged rollout.

    - Returns the JWT payload when a valid token is present.
    - Returns ``None`` when no token is supplied (backwards-compatible).
    - Raises 401 on an *invalid* token regardless of enforcement flag.
    - When ``XR7_ENFORCE_AUTH_GLOBALLY=1`` is set, a missing token also raises 401.
    """
    if credentials is None:
        if _ENFORCE_AUTH_GLOBALLY:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        return None
    try:
        return jwt_service.verify_token(credentials.credentials)
    except JWTValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_admin(payload: dict[str, Any] = Depends(get_auth_payload)) -> dict[str, Any]:
    if str(payload.get("role") or "") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return payload


def require_analyst(payload: dict[str, Any] = Depends(get_auth_payload)) -> dict[str, Any]:
    role = str(payload.get("role") or "").strip().lower()
    if role in {"analyst", "admin", "exec", "executive"}:
        return payload
    raise HTTPException(status_code=403, detail="Analyst role required")


def require_executive(payload: dict[str, Any] = Depends(get_auth_payload)) -> dict[str, Any]:
    role = str(payload.get("role") or "").strip().lower()
    if role in {"exec", "executive", "admin", "ceo", "cfo"}:
        return payload
    raise HTTPException(status_code=403, detail="Executive role required")


def require_legal(payload: dict[str, Any] = Depends(get_auth_payload)) -> dict[str, Any]:
    role = str(payload.get("role") or "").strip().lower()
    if role in {"legal", "counsel", "general_counsel", "admin"}:
        return payload
    raise HTTPException(status_code=403, detail="Legal role required")


def require_artist_access(
    artist_id: str,
    payload: dict[str, Any] = Depends(get_auth_payload),
) -> dict[str, Any]:
    role = str(payload.get("role") or "")
    if role == "admin":
        return payload
    if role == "artist" and str(payload.get("artist_id") or "") == artist_id:
        return payload
    raise HTTPException(status_code=403, detail="Insufficient access for artist scope")


def enforce_claim_access(claim_artist_id: str, payload: dict[str, Any]) -> None:
    role = str(payload.get("role") or "")
    if role == "admin":
        return
    if role == "artist" and str(payload.get("artist_id") or "") == claim_artist_id:
        return
    raise HTTPException(status_code=403, detail="Insufficient access for claim scope")


class ArtistLoginRequest(BaseModel):
    artist_id: str
    email: str | None = None


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


@router.post(
    "/auth/login/artist",
    response_model=TokenResponse,
    openapi_extra={
        "responses": {
            "200": {
                "description": "JWT access token for artist",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "expires_in_seconds": 3600,
                        }
                    }
                },
            },
            "401": {"description": "Artist email mismatch"},
            "404": {"description": "Artist not found"},
        }
    },
)
def artist_login(payload: ArtistLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    artist = get_artist_or_404(payload.artist_id, db)

    if (
        payload.email
        and artist.email
        and payload.email.strip().lower() != artist.email.strip().lower()
    ):
        raise HTTPException(status_code=401, detail="Artist email does not match")

    token = jwt_service.issue_token(
        subject=artist.id,
        role="artist",
        extra={
            "artist_id": artist.id,
            "artist_email": artist.email,
            "tenant_id": _DEFAULT_TENANT_ID,
        },
    )
    return TokenResponse(access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60)


@router.post(
    "/auth/login/admin",
    response_model=TokenResponse,
    openapi_extra={
        "responses": {
            "200": {
                "description": "JWT access token for admin",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer",
                            "expires_in_seconds": 3600,
                        }
                    }
                },
            },
            "401": {"description": "Invalid admin credentials"},
            "503": {"description": "Admin login not configured"},
        }
    },
)
def admin_login(payload: AdminLoginRequest) -> TokenResponse:
    admin_email = os.getenv("XR7_ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("XR7_ADMIN_PASSWORD", "")

    if not admin_email or not admin_password:
        raise HTTPException(
            status_code=503,
            detail="Admin login is not configured. Set XR7_ADMIN_EMAIL and XR7_ADMIN_PASSWORD.",
        )

    if payload.email.strip().lower() != admin_email or payload.password != admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = jwt_service.issue_token(
        subject=payload.email,
        role="admin",
        extra={"tenant_id": _DEFAULT_TENANT_ID},
    )
    return TokenResponse(access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60)


@router.get(
    "/auth/me",
    openapi_extra={
        "responses": {
            "200": {
                "description": "Decoded JWT claims for the authenticated caller",
                "content": {
                    "application/json": {
                        "example": {
                            "subject": "art_xyz789",
                            "role": "artist",
                            "artist_id": "art_xyz789",
                            "artist_email": "artist@example.com",
                            "tenant_id": "default",
                            "issued_at": 1700000000,
                            "expires_at": 1700003600,
                        }
                    }
                },
            },
            "401": {"description": "Missing or invalid token"},
        }
    },
)
def auth_me(
    payload: dict[str, Any] = Depends(get_auth_payload), db: Session = Depends(get_db)
) -> dict:

    artist_id = payload.get("artist_id")
    artist_name: str | None = None
    if artist_id and payload.get("role") == "artist":
        row = db.query(Artist).filter(Artist.id == artist_id).first()
        if row is not None:
            artist_name = row.name

    return inject_branding_metadata(
        db,
        {
            "subject": payload.get("sub"),
            "role": payload.get("role"),
            "artist_id": artist_id,
            "artist_name": artist_name,
            "artist_email": payload.get("artist_email"),
            "admin_email": payload.get("admin_email"),
            "tenant_id": payload.get("tenant_id"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
        },
    )


# ---------------------------------------------------------------------------
# Supabase Auth — exchanges a Supabase JWT for an XR7 session token.
# Stub endpoint while we migrate off the legacy artist_login flow.
# ---------------------------------------------------------------------------


def _provision_artist_from_supabase_claims(claims: dict[str, Any], db: Session) -> Artist:
    """Create an Artist row for a freshly-authenticated Supabase user.

    Identity provenance: the Artist is keyed by ``supabase_user_id`` (the
    JWT's ``sub``). Email is captured if present in the claims. The
    artist's display name uses the ``user_metadata.artist_name`` if set
    (we populate this on admin-created Supabase users), otherwise falls
    back to the email local-part, otherwise "New artist".

    This runs from /auth/supabase/exchange when no Artist matches the
    Supabase user — i.e. on the user's very first sign-in. Subsequent
    sign-ins find the row and skip this path.

    Security note: this trusts that the Supabase project's signup policy
    matches what we want. For closed beta we run with email/password
    signup disabled and admins create users via the admin API, so any
    valid token here corresponds to an admin-vetted person. For open
    signup later, this provisioning step would need additional gates
    (email-domain allow-list, admin-approval queue, payment, etc.).
    """
    supabase_uid = str(claims.get("sub") or "")
    if not supabase_uid:
        # verify_supabase_jwt enforces sub already, but defense in depth.
        raise HTTPException(status_code=401, detail="Supabase token missing subject")

    email = str(claims.get("email") or "").strip().lower() or None
    user_metadata = claims.get("user_metadata") or {}
    name = (
        str(user_metadata.get("artist_name") or "").strip()
        or (email.split("@", 1)[0] if email else "")
        or "New artist"
    )

    artist = Artist(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        supabase_user_id=supabase_uid,
        country_code="US",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@router.post(
    "/auth/supabase/exchange",
    response_model=TokenResponse,
    openapi_extra={
        "responses": {
            "200": {"description": "XR7 access token for the linked Artist"},
            "401": {"description": "Invalid or expired Supabase token"},
            "503": {"description": "SUPABASE_JWT_SECRET not configured"},
        }
    },
)
def supabase_exchange(
    supabase_claims: dict[str, Any] = Depends(get_supabase_claims),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Verify a Supabase JWT, look up (or auto-provision) the linked Artist, and issue an XR7 token.

    This is the authentication path for MVP. Clients authenticate via Supabase
    (email+password, magic link, OAuth), then POST the Supabase access token here
    to get an XR7-signed token that the rest of the API accepts.

    First-time sign-in auto-provisions an Artist row keyed by the Supabase
    user id. Subsequent sign-ins resolve the existing row.

    Admin emails (in ``XR7_ADMIN_USER_EMAILS``) bypass artist provisioning
    and receive an admin token directly. Admins are not artists in this
    system — they're operators of the platform on behalf of artists.
    """
    email = str(supabase_claims.get("email") or "").strip().lower() or None
    supabase_uid = str(supabase_claims.get("sub") or "")

    if _is_admin_email(email):
        token = jwt_service.issue_token(
            subject=email or supabase_uid,
            role="admin",
            extra={
                "admin_email": email,
                "tenant_id": _DEFAULT_TENANT_ID,
                "supabase_user_id": supabase_uid,
            },
        )
        return TokenResponse(
            access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60
        )

    artist = resolve_artist_from_claims(supabase_claims, db)
    if artist is None:
        artist = _provision_artist_from_supabase_claims(supabase_claims, db)

    # Back-fill the link if we resolved by email.
    if not getattr(artist, "supabase_user_id", None):
        artist.supabase_user_id = supabase_uid or None
        db.commit()

    token = jwt_service.issue_token(
        subject=artist.id,
        role="artist",
        extra={
            "artist_id": artist.id,
            "artist_email": artist.email,
            "tenant_id": _DEFAULT_TENANT_ID,
            "supabase_user_id": supabase_uid,
        },
    )
    return TokenResponse(access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60)
