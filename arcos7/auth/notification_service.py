"""
Notification Service for ARCOS7 OTP delivery.

Architecture
------------
``NotificationService`` is an abstract base that defines the interface for
sending OTPs.  Three implementations are provided:

1. **MockNotificationService** (default in tests / development) — returns the
   OTP in the API response payload so that automated tests and local
   development work without external credentials.  This MUST NOT be used in
   production.  Set ``ARCOS7_ENV=production`` to prevent accidental use.

2. **TwilioSMSService** — sends real SMS messages via Twilio.  Requires:
   - ``TWILIO_ACCOUNT_SID`` environment variable
   - ``TWILIO_AUTH_TOKEN`` environment variable
   - ``TWILIO_FROM_NUMBER`` environment variable (E.164 format, e.g. +15551234567)

3. **SMTPEmailService** — sends real email via SMTP.  Requires:
   - ``SMTP_HOST`` environment variable (default: localhost)
   - ``SMTP_PORT`` environment variable (default: 587)
   - ``SMTP_USER`` environment variable
   - ``SMTP_PASSWORD`` environment variable
   - ``SMTP_FROM`` environment variable (sender address)

Swapping providers
------------------
Inject a different ``NotificationService`` implementation into
:func:`~arcos7.api.routers.widget.get_notification_service` to switch
providers without changing any business logic.

Production checklist
---------------------
- Set ``ARCOS7_ENV=production``
- Configure Twilio credentials in environment variables
- Configure SMTP credentials in environment variables
- Ensure all connections use TLS/STARTTLS
- Rotate Twilio auth tokens regularly
"""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class NotificationService(ABC):
    """Abstract interface for OTP delivery."""

    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Send *message* to *phone* (E.164 format).

        Returns ``True`` on success, ``False`` on delivery failure.
        """

    @abstractmethod
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """
        Send an email to *email*.

        Returns ``True`` on success, ``False`` on delivery failure.
        """

    def send_phone_otp(self, phone: str, otp: str, artist_name: str) -> bool:
        """Format and send a phone OTP message."""
        message = (
            f"ARCOS7 Royalty Widget: Your phone verification code is {otp}. "
            f"This code expires in 5 minutes. Do not share it with anyone."
        )
        return self.send_sms(phone, message)

    def send_email_otp(self, email: str, otp: str, artist_name: str) -> bool:
        """Format and send an email OTP message."""
        subject = "Your ARCOS7 Verification Code"
        body = (
            f"Hi {artist_name},\n\n"
            f"Your email verification code for the ARCOS7 Royalty Estimator is:\n\n"
            f"    {otp}\n\n"
            f"This code expires in 5 minutes. Do not share it with anyone.\n\n"
            f"If you did not request this code, please ignore this email.\n\n"
            f"— The ARCOS7 Team"
        )
        return self.send_email(email, subject, body)

    def send_estimate_results(
        self,
        email: str,
        artist_name: str,
        estimate: dict,
    ) -> bool:
        """
        Email the royalty estimate results to the artist.

        Parameters
        ----------
        email:
            Destination address.
        artist_name:
            Used in the greeting line.
        estimate:
            The dict returned by :func:`~arcos7.ml.royalty_estimator.RoyaltyEstimate.to_dict`.
        """
        likely      = estimate.get("total_likely", 0)
        conservative = estimate.get("total_conservative", 0)
        optimistic  = estimate.get("total_optimistic", 0)
        currency    = estimate.get("currency", "USD")
        streams     = estimate.get("streams", [])
        disclaimer  = estimate.get("disclaimer", "")

        def _fmt(n: float) -> str:
            return f"{currency} {n:,.2f}"

        stream_lines = "\n".join(
            f"  • {s.get('label', s.get('stream_type', ''))}: {_fmt(s.get('likely', 0))}"
            for s in streams
        )

        subject = f"Your ARCOS7 Royalty Estimate — {_fmt(likely)} likely owed"
        body = (
            f"Hi {artist_name},\n\n"
            f"Here is your personalised royalty estimate from the ARCOS7 Royalty Estimator.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ESTIMATED UNPAID ROYALTIES\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Conservative:  {_fmt(conservative)}\n"
            f"  Likely:        {_fmt(likely)}\n"
            f"  Optimistic:    {_fmt(optimistic)}\n\n"
            f"Breakdown by revenue stream:\n"
            f"{stream_lines}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Want to pursue recovery?\n"
            f"Reply to this email or visit https://arcos7.com/recovery to speak\n"
            f"with an ARCOS7 recovery specialist.\n\n"
            f"Important notice\n"
            f"────────────────\n"
            f"{disclaimer}\n\n"
            f"— The ARCOS7 Team\n"
            f"https://arcos7.com\n"
        )
        return self.send_email(email, subject, body)


# ---------------------------------------------------------------------------
# Mock implementation (development / testing only)
# ---------------------------------------------------------------------------

class MockNotificationService(NotificationService):
    """
    Development / test notification service.

    OTPs are logged at DEBUG level and returned in the API response so
    that automated tests and local development work without external
    credentials.

    **This service MUST NOT be used in production.**  If ``ARCOS7_ENV``
    is set to ``production`` (case-insensitive), constructing this class
    raises ``RuntimeError``.
    """

    def __init__(self) -> None:
        env = os.environ.get("ARCOS7_ENV", "development").lower()
        if env == "production":
            raise RuntimeError(
                "MockNotificationService cannot be used in production. "
                "Configure TWILIO_ACCOUNT_SID and SMTP_HOST to use real providers."
            )
        self.sent_sms: list[dict] = []
        self.sent_emails: list[dict] = []

    def send_sms(self, phone: str, message: str) -> bool:
        # Do NOT log the actual phone number in production code paths.
        logger.debug("MockSMS → [REDACTED]: %s", message)
        self.sent_sms.append({"phone": phone, "message": message})
        return True

    def send_email(self, email: str, subject: str, body: str) -> bool:
        logger.debug("MockEmail → [REDACTED] subject=%r", subject)
        self.sent_emails.append({"email": email, "subject": subject, "body": body})
        return True


# ---------------------------------------------------------------------------
# Twilio SMS implementation
# ---------------------------------------------------------------------------

class TwilioSMSService(NotificationService):
    """
    Production SMS delivery via Twilio.

    Required environment variables
    --------------------------------
    ``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``, ``TWILIO_FROM_NUMBER``

    Install dependency: ``pip install twilio``
    """

    def __init__(self) -> None:
        self._account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        self._auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self._from_number = os.environ["TWILIO_FROM_NUMBER"]

        try:
            from twilio.rest import Client  # type: ignore[import]
            self._client = Client(self._account_sid, self._auth_token)
        except ImportError as exc:
            raise ImportError(
                "Twilio is not installed.  Run: pip install twilio"
            ) from exc

    def send_sms(self, phone: str, message: str) -> bool:
        try:
            self._client.messages.create(
                body=message,
                from_=self._from_number,
                to=phone,
            )
            return True
        except Exception:
            logger.exception("Twilio SMS delivery failed")
            return False

    def send_email(self, email: str, subject: str, body: str) -> bool:
        # Twilio does not send email — use SMTPEmailService alongside this.
        raise NotImplementedError(
            "TwilioSMSService does not support email. Use SMTPEmailService."
        )


# ---------------------------------------------------------------------------
# SMTP email implementation
# ---------------------------------------------------------------------------

class SMTPEmailService(NotificationService):
    """
    Production email delivery via SMTP (e.g. SendGrid, AWS SES, Gmail).

    Required environment variables
    --------------------------------
    ``SMTP_HOST``, ``SMTP_PORT`` (default 587), ``SMTP_USER``,
    ``SMTP_PASSWORD``, ``SMTP_FROM``

    Uses STARTTLS by default (port 587).  For port 465 (SSL), override
    ``SMTP_PORT=465`` and set ``SMTP_USE_SSL=true``.
    """

    def __init__(self) -> None:
        self._host = os.environ.get("SMTP_HOST", "localhost")
        self._port = int(os.environ.get("SMTP_PORT", "587"))
        self._user = os.environ.get("SMTP_USER", "")
        self._password = os.environ.get("SMTP_PASSWORD", "")
        self._from_addr = os.environ.get("SMTP_FROM", "noreply@arcos7.com")
        self._use_ssl = os.environ.get("SMTP_USE_SSL", "false").lower() == "true"

    def send_sms(self, phone: str, message: str) -> bool:
        raise NotImplementedError(
            "SMTPEmailService does not support SMS. Use TwilioSMSService."
        )

    def send_email(self, email: str, subject: str, body: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self._from_addr
            msg["To"] = email
            msg.attach(MIMEText(body, "plain"))

            context = ssl.create_default_context()
            if self._use_ssl:
                with smtplib.SMTP_SSL(self._host, self._port, context=context) as server:
                    if self._user:
                        server.login(self._user, self._password)
                    server.sendmail(self._from_addr, email, msg.as_string())
            else:
                with smtplib.SMTP(self._host, self._port) as server:
                    server.starttls(context=context)
                    if self._user:
                        server.login(self._user, self._password)
                    server.sendmail(self._from_addr, email, msg.as_string())
            return True
        except Exception:
            logger.exception("SMTP email delivery failed")
            return False


# ---------------------------------------------------------------------------
# Combined service (phone via Twilio + email via SMTP)
# ---------------------------------------------------------------------------

class CombinedNotificationService(NotificationService):
    """
    Delegates SMS to a :class:`TwilioSMSService` and email to an
    :class:`SMTPEmailService`.  This is the recommended production setup.
    """

    def __init__(self) -> None:
        self._sms = TwilioSMSService()
        self._email = SMTPEmailService()

    def send_sms(self, phone: str, message: str) -> bool:
        return self._sms.send_sms(phone, message)

    def send_email(self, email: str, subject: str, body: str) -> bool:
        return self._email.send_email(email, subject, body)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_notification_service() -> NotificationService:
    """
    Return the appropriate notification service based on environment.

    - If ``ARCOS7_ENV=production``: returns :class:`CombinedNotificationService`
      (requires Twilio + SMTP env vars).
    - Otherwise: returns :class:`MockNotificationService` (for dev/test).
    """
    env = os.environ.get("ARCOS7_ENV", "development").lower()
    if env == "production":
        return CombinedNotificationService()
    return MockNotificationService()
