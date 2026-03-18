from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.auth.jwt_service import JWTValidationError, jwt_service
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["auth"])

# Shared HTTPBearer scheme — auto-injects BearerAuth securityScheme into the OpenAPI spec
# for every endpoint that depends on get_auth_payload or get_optional_auth_payload.
_bearer_scheme = HTTPBearer(auto_error=False)

# When XR7_ENFORCE_AUTH_GLOBALLY=1, soft-guarded endpoints reject unauthenticated requests.
_ENFORCE_AUTH_GLOBALLY = os.environ.get("XR7_ENFORCE_AUTH_GLOBALLY", "0").strip() == "1"


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


@router.post("/auth/login/artist", response_model=TokenResponse)
def artist_login(payload: ArtistLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    artist = db.query(Artist).filter(Artist.id == payload.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    if payload.email and artist.email and payload.email.strip().lower() != artist.email.strip().lower():
        raise HTTPException(status_code=401, detail="Artist email does not match")

    token = jwt_service.issue_token(
        subject=artist.id,
        role="artist",
        extra={"artist_id": artist.id, "artist_email": artist.email},
    )
    return TokenResponse(access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60)


@router.post("/auth/login/admin", response_model=TokenResponse)
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

    token = jwt_service.issue_token(subject=payload.email, role="admin")
    return TokenResponse(access_token=token, expires_in_seconds=jwt_service.access_ttl_minutes * 60)


@router.get("/auth/me")
def auth_me(payload: dict[str, Any] = Depends(get_auth_payload), db: Session = Depends(get_db)) -> dict:

    return inject_branding_metadata(db, {
        "subject": payload.get("sub"),
        "role": payload.get("role"),
        "artist_id": payload.get("artist_id"),
        "artist_email": payload.get("artist_email"),
        "issued_at": payload.get("iat"),
        "expires_at": payload.get("exp"),
    })
