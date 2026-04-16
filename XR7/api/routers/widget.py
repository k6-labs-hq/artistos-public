"""
Artist Royalty Estimation Widget — API Endpoints

Three-step MFA-gated flow
--------------------------

Step 1 — Register  ``POST /widget/register``
    Artist submits name, phone, and email.  Two OTPs are sent: one via SMS
    and one via email.  Returns a session ID.

Step 2 — Verify  ``POST /widget/verify``
    Artist submits the session ID along with both OTPs.  Both must be correct
    and the session must not be expired (5 minutes) or locked (3 failures).
    Returns a short-lived estimate token (1 hour).

Step 3 — Estimate  ``POST /widget/estimate``
    Artist submits the estimate token plus optional career profile details
    (career stage, genre, years active).  Saves a lead record, emails the
    results to the artist, and returns the full royalty owed estimate.

Step 4 (optional) — Claim  ``POST /widget/claim``
    Artist who has already received an estimate clicks "Claim My Recovery".
    Marks the lead record as claimed and notifies the recovery team.

Admin — ``GET /widget/leads``
    Returns all persisted leads.  Protected by ``WIDGET_ADMIN_KEY`` env var.

Security layers
---------------
- Phone E.164 validation via regex
- Email format validation via regex
- Artist name sanitisation (length cap, strip)
- OTP rate limiting: 3 sends / phone / hour
- Attempt lockout: 3 failures → 15-minute cooldown
- Session expiry: 5 minutes
- Token expiry: 1 hour
- Constant-time OTP comparison (timing-attack resistant)
- Mock OTPs only returned when ``XR7_ENV`` ≠ ``production``
- Admin endpoint gated by ``WIDGET_ADMIN_KEY`` bearer token
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from XR7.api.authz import require_admin
from XR7.auth import otp_service
from XR7.auth.notification_service import get_notification_service
from XR7.ml.royalty_estimator import VALID_CAREER_STAGES, estimate_royalties
from XR7.models.base import get_db
from XR7.models.widget_lead import WidgetLead, WidgetLeadSchema, hash_phone
from XR7.tasks.hubspot import hubspot_sync_widget_lead, hubspot_sync_widget_registration
from xr7_common.logging import get_logger

router = APIRouter(prefix="/widget", tags=["widget"])
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

# E.164 phone regex: optional '+', country code + up to 15 digits
_PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")

# Basic email regex (RFC 5322 simplified)
_EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[a-zA-Z]{2,}$")

_MAX_NAME_LEN = 120


def _validate_phone(phone: str) -> str:
    """
    Return a normalised E.164 phone string or raise ValueError.

    Common formatting characters (spaces, dashes, parentheses) are stripped.
    A leading '+' is added if absent so that artists who omit it (e.g. they
    type "15551234567" instead of "+15551234567") are not penalised — the
    country code must still be present.  A bare 10-digit local number such as
    "5551234567" will fail validation because it does not include a country code.
    """
    cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    if not _PHONE_RE.match(cleaned):
        raise ValueError(
            "Phone number must include your country code in E.164 format "
            "(e.g. +15551234567 for US). Bare 10-digit local numbers are not accepted."
        )
    return cleaned


def _validate_email(email: str) -> str:
    cleaned = email.strip().lower()
    if not _EMAIL_RE.match(cleaned):
        raise ValueError("Please enter a valid email address.")
    return cleaned


def _validate_artist_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Artist name cannot be empty.")
    if len(cleaned) > _MAX_NAME_LEN:
        raise ValueError(f"Artist name must be {_MAX_NAME_LEN} characters or fewer.")
    return cleaned


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    artist_name: str
    phone: str
    email: str

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v: str) -> str:
        return _validate_phone(v)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        return _validate_email(v)

    @field_validator("artist_name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        return _validate_artist_name(v)


class RegisterResponse(BaseModel):
    session_id: str
    message: str
    expires_in_seconds: int
    # Only present in development/test environments
    dev_phone_otp: Optional[str] = None
    dev_email_otp: Optional[str] = None


class VerifyRequest(BaseModel):
    session_id: str
    phone_otp: str
    email_otp: str


class VerifyResponse(BaseModel):
    estimate_token: str
    artist_name: str
    message: str
    expires_in_seconds: int


class EstimateRequest(BaseModel):
    estimate_token: str
    career_stage: str = "DEVELOPING"
    genre: str = "OTHER"
    years_active: int = 5
    territory: str = "US"

    @field_validator("career_stage")
    @classmethod
    def stage_must_be_valid(cls, v: str) -> str:
        upper = v.strip().upper()
        if upper not in VALID_CAREER_STAGES:
            raise ValueError(f"career_stage must be one of: {', '.join(VALID_CAREER_STAGES)}")
        return upper

    @field_validator("genre")
    @classmethod
    def genre_must_be_valid(cls, v: str) -> str:
        # Allow unknown genres — the estimator normalises them to OTHER
        return v.strip()

    @field_validator("years_active")
    @classmethod
    def years_must_be_positive(cls, v: int) -> int:
        if not 1 <= v <= 50:
            raise ValueError("years_active must be between 1 and 50.")
        return v


# ---------------------------------------------------------------------------
# Dependency: notification service
# ---------------------------------------------------------------------------


def _get_notification_service():
    return get_notification_service()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest):
    """
    Step 1 of the MFA flow.

    Validates the artist's identity details, creates a verification session,
    and dispatches a 6-digit OTP to both the provided phone number and email
    address.

    In **development** environments (``XR7_ENV`` ≠ ``production``), the
    OTPs are also returned in the response body under ``dev_phone_otp`` and
    ``dev_email_otp`` so that local testing requires no external credentials.
    These fields are **absent** in production.
    """
    try:
        session = otp_service.create_session(
            artist_name=body.artist_name,
            phone=body.phone,
            email=body.email,
        )
    except otp_service.RateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))

    svc = _get_notification_service()

    sms_ok = svc.send_phone_otp(body.phone, session.phone_otp, body.artist_name)
    email_ok = svc.send_email_otp(body.email, session.email_otp, body.artist_name)

    if not sms_ok or not email_ok:
        raise HTTPException(
            status_code=503,
            detail="Failed to send verification codes. Please try again.",
        )

    is_dev = os.environ.get("XR7_ENV", "development").lower() != "production"

    try:
        hubspot_sync_widget_registration.delay(
            artist_name=body.artist_name,
            email=body.email,
            session_id=session.session_id,
        )
    except Exception:  # noqa: BLE001
        logger.exception(
            "Failed to enqueue widget registration HubSpot sync",
            extra={"session_id": session.session_id},
        )

    return RegisterResponse(
        session_id=session.session_id,
        message=(
            "Verification codes have been sent to your phone and email. "
            "Enter both codes within 5 minutes to continue."
        ),
        expires_in_seconds=otp_service.OTP_EXPIRY_SECONDS,
        dev_phone_otp=session.phone_otp if is_dev else None,
        dev_email_otp=session.email_otp if is_dev else None,
    )


@router.post("/verify", response_model=VerifyResponse)
def verify(body: VerifyRequest):
    """
    Step 2 of the MFA flow.

    Both the phone OTP and email OTP must be correct.  On success, a
    short-lived estimate token is returned.  This token must be presented
    to ``POST /widget/estimate`` to retrieve the royalty estimate.
    """
    try:
        token = otp_service.verify_session(
            session_id=body.session_id,
            phone_otp=body.phone_otp,
            email_otp=body.email_otp,
        )
    except otp_service.SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except otp_service.SessionLockedError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except otp_service.InvalidOTPError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return VerifyResponse(
        estimate_token=token.token,
        artist_name=token.artist_name,
        message="Identity verified. You may now retrieve your royalty estimate.",
        expires_in_seconds=otp_service.ESTIMATE_TOKEN_EXPIRY_SECONDS,
    )


@router.post("/estimate")
def estimate(body: EstimateRequest, db: Session = Depends(get_db)):
    """
    Step 3 of the MFA flow.

    Presents the estimate token obtained from ``POST /widget/verify`` along
    with optional career profile information.  Saves a lead record to the
    database, emails the estimate results to the artist, and returns the
    full royalty owed estimate.
    """
    try:
        token = otp_service.validate_token(body.estimate_token)
    except otp_service.TokenError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

    result = estimate_royalties(
        artist_name=token.artist_name,
        career_stage=body.career_stage,
        genre=body.genre,
        years_active=body.years_active,
        territory=body.territory,
    )
    estimate_dict = result.to_dict()

    # Persist the lead record
    lead = WidgetLead(
        artist_name=token.artist_name,
        email=token.email,
        phone_hash=hash_phone(token.phone),
        career_stage=body.career_stage,
        genre=body.genre,
        years_active=body.years_active,
        territory=body.territory,
        estimate_conservative=estimate_dict["total_conservative"],
        estimate_likely=estimate_dict["total_likely"],
        estimate_optimistic=estimate_dict["total_optimistic"],
        currency=estimate_dict.get("currency", "USD"),
        results_emailed=False,
        claimed=False,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Send results email (non-fatal if it fails)
    svc = _get_notification_service()
    email_sent = svc.send_estimate_results(
        email=token.email,
        artist_name=token.artist_name,
        estimate=estimate_dict,
    )
    if email_sent:
        lead.results_emailed = True
        db.commit()

    try:
        hubspot_sync_widget_lead.delay(lead.id, event="widget_estimate")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue widget lead HubSpot sync", extra={"lead_id": lead.id})

    return {
        "lead_id": lead.id,
        "artist_name": token.artist_name,
        "estimate": estimate_dict,
    }


# ---------------------------------------------------------------------------
# CTA — Claim My Recovery
# ---------------------------------------------------------------------------


class ClaimRequest(BaseModel):
    lead_id: str


@router.post("/claim")
def claim(body: ClaimRequest, db: Session = Depends(get_db)):
    """
    Mark a lead as "claimed" when the artist clicks the recovery CTA.

    The ``lead_id`` returned by ``POST /widget/estimate`` is required.
    Idempotent — calling this multiple times on the same lead is safe.
    """
    lead = db.query(WidgetLead).filter(WidgetLead.id == body.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    if not lead.claimed:
        lead.claimed = True
        lead.claim_submitted_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "lead_id": lead.id,
        "artist_name": lead.artist_name,
        "claimed": True,
        "message": (
            "Your recovery request has been received. An XR7 specialist "
            "will contact you at the email address you provided within 2 business days."
        ),
    }


# ---------------------------------------------------------------------------
# Admin — list all leads
# ---------------------------------------------------------------------------


@router.get("/leads", response_model=List[WidgetLeadSchema])
def list_leads(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """
    Return all widget leads in reverse-chronological order.

    Requires the ``X-Admin-Key`` request header to equal the
    ``WIDGET_ADMIN_KEY`` environment variable.
    """
    leads = db.query(WidgetLead).order_by(WidgetLead.created_at.desc()).all()
    return leads
