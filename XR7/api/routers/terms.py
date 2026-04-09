"""
Terms & Conditions endpoints for XR7 Engine 2.

GET  /terms
    Return the current T&C text, version, and SHA-256 hash.  The client
    should display this text in full before presenting the acceptance checkbox.

POST /artists/{artist_id}/terms/accept
    Record the artist's acceptance of the current T&C.  Requires a JSON body
    confirming the version the artist was shown; if the version does not match
    the live version the server rejects the request (stale-page protection).

GET  /artists/{artist_id}/terms/status
    Return whether the artist has accepted the current T&C, with the
    acceptance timestamp and version they agreed to.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.legal.terms import TERMS_TEXT, TERMS_VERSION, terms_text_sha256
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.terms_acceptance import TermsAcceptance, TermsAcceptanceSchema
from XR7.api.deps import get_artist_or_404
from XR7.services.branding import inject_branding_metadata
from XR7.services.artist_lifecycle import promote_to_onboarded

router = APIRouter(tags=["terms"])

_CURRENT_SHA256 = terms_text_sha256()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class TermsAcceptRequest(BaseModel):
    """
    Body for POST /artists/{artist_id}/terms/accept.

    ``terms_version`` must match the version the server returns from
    GET /terms.  This prevents a client that cached an old version of the
    T&C from accidentally accepting stale terms.
    """
    terms_version: str
    # Explicit acknowledgement checkbox — must be True
    agreed: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/terms")
def get_terms() -> dict:
    """
    Return the current Artist Recovery Services Agreement text, version
    identifier, and SHA-256 hash.

    The client should render the full ``text`` field for the artist to read
    before presenting the acceptance checkbox.  The ``version`` and ``sha256``
    values must be echoed back verbatim in POST /artists/{id}/terms/accept.
    """
    return {
        "version": TERMS_VERSION,
        "sha256": _CURRENT_SHA256,
        "text": TERMS_TEXT,
    }


@router.post(
    "/artists/{artist_id}/terms/accept",
    response_model=TermsAcceptanceSchema,
    status_code=201,
)
def accept_terms(
    artist_id: str,
    body: TermsAcceptRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TermsAcceptance:
    """
    Record the artist's acceptance of the current Artist Recovery Services
    Agreement.

    This endpoint:
    1. Verifies the artist exists.
    2. Verifies the version the artist was shown matches the live version
       (stale-page protection).
    3. Verifies the ``agreed`` flag is ``true`` — a bare form POST cannot
       accidentally create an acceptance record.
    4. Persists an immutable TermsAcceptance row with server-set timestamp,
       IP address, and User-Agent string.

    Submitting again after the artist has already accepted the current version
    is idempotent — the existing acceptance record is returned without creating
    a duplicate.
    """
    # 1. Artist must exist
    artist = get_artist_or_404(artist_id, db)

    # 2. Stale-version protection
    if body.terms_version != TERMS_VERSION:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Terms version mismatch.  You were shown version "
                f"'{body.terms_version}' but the current version is "
                f"'{TERMS_VERSION}'.  Please reload the terms and accept "
                f"the latest version."
            ),
        )

    # 3. Explicit opt-in required
    if not body.agreed:
        raise HTTPException(
            status_code=422,
            detail="You must set 'agreed' to true to accept the terms.",
        )

    # 4. Idempotency — return existing record if artist already accepted this version
    existing = (
        db.query(TermsAcceptance)
        .filter(
            TermsAcceptance.artist_id == artist_id,
            TermsAcceptance.terms_version == TERMS_VERSION,
        )
        .first()
    )
    if existing:
        return existing

    # 5. Persist the acceptance record
    ip_address = _extract_client_ip(request)
    user_agent = (request.headers.get("user-agent") or "")[:512]

    record = TermsAcceptance(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        terms_version=TERMS_VERSION,
        text_sha256=_CURRENT_SHA256,
        accepted_at=datetime.now(timezone.utc),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(record)
    promote_to_onboarded(artist)
    db.commit()
    db.refresh(record)
    return record


@router.get("/artists/{artist_id}/terms/status")
def terms_status(artist_id: str, db: Session = Depends(get_db)) -> dict:
    """
    Return whether the artist has accepted the current version of the
    Artist Recovery Services Agreement.

    ``accepted`` is ``True`` only if there is an acceptance record for the
    *current* live version.  If the terms were updated since the artist last
    agreed, ``accepted`` will be ``False`` and ``pending_version`` will
    indicate the version the artist needs to accept.
    """
    artist = get_artist_or_404(artist_id, db)

    record = (
        db.query(TermsAcceptance)
        .filter(
            TermsAcceptance.artist_id == artist_id,
            TermsAcceptance.terms_version == TERMS_VERSION,
        )
        .first()
    )

    if record:
        return inject_branding_metadata(db, {
            "artist_id": artist_id,
            "accepted": True,
            "terms_version": record.terms_version,
            "accepted_at": record.accepted_at.isoformat(),
            "text_sha256": record.text_sha256,
            "pending_version": None,
        })

    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "accepted": False,
        "terms_version": None,
        "accepted_at": None,
        "text_sha256": None,
        "pending_version": TERMS_VERSION,
    })


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_client_ip(request: Request) -> str | None:
    """
    Return the client IP from X-Forwarded-For (trusted reverse-proxy header)
    or fall back to the direct connection address.  Stored for audit purposes.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For may be a comma-separated list; take the leftmost
        # entry which represents the originating client.
        return forwarded_for.split(",")[0].strip()[:45]
    if request.client:
        return request.client.host[:45]
    return None


def require_terms_accepted(artist_id: str, db: Session) -> None:
    """
    Guard helper — raises HTTP 403 if the artist has not accepted the current
    T&C.  Import and call this at the top of any endpoint that requires prior
    T&C acceptance before processing artist data.
    """
    record = (
        db.query(TermsAcceptance)
        .filter(
            TermsAcceptance.artist_id == artist_id,
            TermsAcceptance.terms_version == TERMS_VERSION,
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=403,
            detail=(
                "You must accept the Artist Recovery Services Agreement before "
                "submitting data for analysis.  Please call "
                "GET /terms to read the agreement, then "
                "POST /artists/{artist_id}/terms/accept to accept it."
            ),
        )
