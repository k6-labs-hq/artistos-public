"""
OTP (One-Time Passcode) Service for the XR7 Artist Recovery Widget.

Security design
---------------
- **Passcodes** are 6-digit strings generated with Python's ``secrets`` module
  (cryptographically secure PRNG) to ensure unpredictability.
- **Storage** is an in-memory dict keyed by session ID.  In production this
  should be replaced with a Redis store so it survives process restarts and
  horizontal scaling.  The API is designed to make that swap trivial.
- **Expiry** — each OTP session expires 5 minutes after creation.  Any
  verification attempt after expiry is rejected regardless of the code.
- **Rate limiting** — at most 3 OTP send requests are permitted per phone
  number within a rolling 1-hour window, preventing SMS-bombing attacks.
- **Attempt lockout** — after 3 consecutive failed verification attempts the
  session is locked for 15 minutes; a new ``/widget/register`` call is
  required.  This limits brute-force attacks on the 6-digit code space
  (10⁶ possibilities) to at most 3 guesses.
- **Constant-time comparison** — ``hmac.compare_digest`` is used instead of
  ``==`` for OTP comparison to eliminate timing-side-channel leakage.
- **PII hygiene** — phone numbers and email addresses are never included in
  exception messages or log strings.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 minutes
SESSION_LOCKOUT_SECONDS = 900  # 15 minutes after 3 failed attempts
MAX_ATTEMPTS = 3
MAX_SENDS_PER_PHONE_PER_HOUR = 3
ESTIMATE_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour


# ---------------------------------------------------------------------------
# Internal data classes
# ---------------------------------------------------------------------------


@dataclass
class OTPSession:
    session_id: str
    artist_name: str
    phone: str  # stored for rate-limit lookup; never logged
    email: str  # stored for routing; never logged
    phone_otp: str
    email_otp: str
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    locked_until: datetime | None = None
    verified: bool = False

    def is_expired(self, now: datetime | None = None) -> bool:
        ref = now or datetime.now(timezone.utc)
        return ref >= self.expires_at

    def is_locked(self, now: datetime | None = None) -> bool:
        if self.locked_until is None:
            return False
        ref = now or datetime.now(timezone.utc)
        return ref < self.locked_until


@dataclass
class EstimateToken:
    token: str
    session_id: str
    artist_name: str
    phone: str
    email: str
    expires_at: datetime

    def is_expired(self, now: datetime | None = None) -> bool:
        ref = now or datetime.now(timezone.utc)
        return ref >= self.expires_at


# ---------------------------------------------------------------------------
# In-memory stores  (swap for Redis in production)
# ---------------------------------------------------------------------------

# session_id → OTPSession
_sessions: dict[str, OTPSession] = {}

# phone_hash → list[datetime] of recent send timestamps
_send_log: dict[str, list[datetime]] = {}

# token → EstimateToken
_tokens: dict[str, EstimateToken] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _phone_key(phone: str) -> str:
    """Return a stable key for rate-limit tracking without storing the raw number."""
    return hashlib.sha256(phone.encode()).hexdigest()[:16]


def _generate_otp() -> str:
    """Return a 6-digit numeric OTP using a CSPRNG."""
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(OTP_LENGTH))


def _generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def _generate_token() -> str:
    return secrets.token_urlsafe(48)


def _prune_expired(now: datetime | None = None) -> None:
    """Remove stale sessions and tokens to prevent memory growth."""
    ref = now or _now()
    expired_sessions = [sid for sid, s in _sessions.items() if s.is_expired(ref)]
    for sid in expired_sessions:
        _sessions.pop(sid, None)
    expired_tokens = [t for t, tok in _tokens.items() if tok.is_expired(ref)]
    for t in expired_tokens:
        _tokens.pop(t, None)


def _check_rate_limit(phone: str, now: datetime | None = None) -> None:
    """Raise ``RateLimitError`` if too many OTPs have been sent to this phone."""
    ref = now or _now()
    key = _phone_key(phone)
    window_start = ref - timedelta(hours=1)
    history = _send_log.get(key, [])
    # Keep only timestamps within the last hour
    recent = [ts for ts in history if ts >= window_start]
    if len(recent) >= MAX_SENDS_PER_PHONE_PER_HOUR:
        raise RateLimitError("Too many verification requests.  Please wait before trying again.")
    recent.append(ref)
    _send_log[key] = recent


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class OTPError(Exception):
    """Base class for OTP service errors."""


class RateLimitError(OTPError):
    """Raised when a phone number has hit the send rate limit."""


class SessionNotFoundError(OTPError):
    """Raised when the session ID is not found or has expired."""


class SessionLockedError(OTPError):
    """Raised when the session is locked due to too many failed attempts."""


class InvalidOTPError(OTPError):
    """Raised when an OTP does not match or the session has expired."""


class TokenError(OTPError):
    """Raised when an estimate token is invalid or expired."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_session(
    artist_name: str,
    phone: str,
    email: str,
    now: datetime | None = None,
) -> OTPSession:
    """
    Create a new OTP session and return it.

    The caller is responsible for transmitting the OTPs to the artist
    via :class:`~XR7.auth.notification_service.NotificationService`.

    Raises
    ------
    RateLimitError
        If the phone number has exceeded the hourly send limit.
    """
    ref = now or _now()
    _prune_expired(ref)
    _check_rate_limit(phone, ref)

    session_id = _generate_session_id()
    phone_otp = _generate_otp()
    email_otp = _generate_otp()

    session = OTPSession(
        session_id=session_id,
        artist_name=artist_name,
        phone=phone,
        email=email,
        phone_otp=phone_otp,
        email_otp=email_otp,
        created_at=ref,
        expires_at=ref + timedelta(seconds=OTP_EXPIRY_SECONDS),
    )
    _sessions[session_id] = session
    return session


def verify_session(
    session_id: str,
    phone_otp: str,
    email_otp: str,
    now: datetime | None = None,
) -> EstimateToken:
    """
    Verify both OTPs and, on success, return a short-lived estimate token.

    The phone OTP and email OTP must BOTH be correct and the session must
    not be expired or locked.

    Raises
    ------
    SessionNotFoundError
        Session ID is unknown or already expired.
    SessionLockedError
        Too many failed attempts; locked until ``session.locked_until``.
    InvalidOTPError
        One or both OTPs are incorrect, or the session has expired.
    """
    ref = now or _now()
    _prune_expired(ref)

    session = _sessions.get(session_id)
    if session is None:
        raise SessionNotFoundError("Session not found or has expired.  Please start over.")

    if session.is_expired(ref):
        _sessions.pop(session_id, None)
        raise SessionNotFoundError("Verification session has expired.  Please start over.")

    if session.is_locked(ref):
        remaining = int((session.locked_until - ref).total_seconds())
        raise SessionLockedError(
            f"Too many failed attempts.  Please wait {remaining // 60} minutes before trying again."
        )

    # Constant-time comparison to prevent timing attacks
    phone_match = hmac.compare_digest(session.phone_otp, phone_otp.strip())
    email_match = hmac.compare_digest(session.email_otp, email_otp.strip())

    if not (phone_match and email_match):
        session.attempts += 1
        if session.attempts >= MAX_ATTEMPTS:
            session.locked_until = ref + timedelta(seconds=SESSION_LOCKOUT_SECONDS)
            raise SessionLockedError(
                "Too many failed attempts.  Session is now locked for 15 minutes."
            )
        remaining_attempts = MAX_ATTEMPTS - session.attempts
        raise InvalidOTPError(
            f"Verification codes did not match.  {remaining_attempts} attempt(s) remaining."
        )

    # Both codes verified — issue an estimate token
    session.verified = True

    token_str = _generate_token()
    token = EstimateToken(
        token=token_str,
        session_id=session_id,
        artist_name=session.artist_name,
        phone=session.phone,
        email=session.email,
        expires_at=ref + timedelta(seconds=ESTIMATE_TOKEN_EXPIRY_SECONDS),
    )
    _tokens[token_str] = token

    # Remove the session — it's been consumed
    _sessions.pop(session_id, None)

    return token


def validate_token(token_str: str, now: datetime | None = None) -> EstimateToken:
    """
    Look up and validate an estimate token.

    Raises
    ------
    TokenError
        Token is unknown, expired, or already consumed.
    """
    ref = now or _now()
    _prune_expired(ref)

    token = _tokens.get(token_str)
    if token is None:
        raise TokenError("Invalid or expired estimate token.  Please complete verification again.")

    if token.is_expired(ref):
        _tokens.pop(token_str, None)
        raise TokenError("Estimate token has expired.  Please complete verification again.")

    return token


def clear_all() -> None:
    """Clear all in-memory state.  Used in tests only."""
    _sessions.clear()
    _send_log.clear()
    _tokens.clear()
