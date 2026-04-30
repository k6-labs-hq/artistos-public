"""Thin Postmark API client for transactional email + inbound parse.

We chose Postmark over SendGrid for the recovery loop's deliverability
requirements (transactional-only IP pool, clean reply correlation via
inbound parse). See docs/strategy/disruption-analysis-2026-04-29.md
for the rationale.

This wrapper deliberately stays small. Postmark's REST API is simple
(Bearer token, JSON in/out, predictable status codes); using their
SDK adds a dependency for negligible benefit. httpx is already in
requirements.

Behavior in different modes:
- `POSTMARK_API_TOKEN` set        → real send
- `POSTMARK_API_TOKEN` unset      → log-only stub (returns success).
  Local dev and CI run in stub mode; QA + prod set the env var.

Stub mode is intentional. We do NOT fail-open into a "send via some
other provider" fallback because:
  1. Behavior should be predictable per environment, not depend on which
     provider env vars are set
  2. A misconfigured prod accidentally sending via a stale dev provider
     would be worse than not sending at all
  3. The notification log captures the stub send, so we can replay
     anything that was suppressed
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

from xr7_common.settings import settings

logger = logging.getLogger(__name__)

_POSTMARK_API = "https://api.postmarkapp.com"
_POSTMARK_TIMEOUT = 10.0


@dataclass(frozen=True)
class PostmarkAttachment:
    """A file to attach to an outbound email.

    `content` is the raw bytes; the client base64-encodes for the Postmark API.
    Don't pre-encode — that's the client's job and double-encoding will silently
    corrupt the attachment.
    """

    name: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass(frozen=True)
class PostmarkSendResult:
    """The outcome of a single send attempt.

    `message_id` is Postmark's UUID for the sent message — store it on
    the originating Claim/Notification row so the inbound webhook can
    correlate replies via the In-Reply-To / References headers.
    """

    delivered: bool
    message_id: str | None
    error_code: int | None = None
    error_message: str | None = None
    stubbed: bool = False


class PostmarkClient:
    """Minimal Postmark sender. One client per process is fine."""

    def __init__(
        self,
        *,
        api_token: str | None = None,
        default_from: str | None = None,
    ) -> None:
        # Read at construction time, not at module load. Settings is a frozen
        # dataclass evaluated when xr7_common is imported — that's too early
        # for tests that monkeypatch env vars at fixture time. Falling back to
        # os.environ keeps the test path working without giving up the typed
        # settings dataclass for production paths.
        self._api_token = (
            api_token
            if api_token is not None
            else (os.environ.get("POSTMARK_API_TOKEN") or settings.POSTMARK_API_TOKEN)
        )
        self._default_from = (
            default_from or os.environ.get("POSTMARK_FROM_EMAIL") or settings.POSTMARK_FROM_EMAIL
        )

    @property
    def configured(self) -> bool:
        return bool(self._api_token)

    def send_email(
        self,
        *,
        to: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
        from_email: str | None = None,
        reply_to: str | None = None,
        message_stream: str = "outbound",
        metadata: dict[str, str] | None = None,
        tag: str | None = None,
        attachments: list[PostmarkAttachment] | None = None,
    ) -> PostmarkSendResult:
        """Send a single transactional email.

        `message_stream` defaults to Postmark's transactional stream;
        broadcast/marketing requires a separate stream by Postmark
        policy. Don't change the default unless you understand why.

        `metadata` is propagated through to inbound parse webhooks
        when recipients reply, which is how we correlate dispute
        responses back to a Claim row.
        """
        if not self.configured:
            logger.info(
                "[POSTMARK STUB] Would send to %s subject=%r tag=%s metadata=%s attachments=%d",
                to,
                subject,
                tag,
                metadata,
                len(attachments) if attachments else 0,
            )
            return PostmarkSendResult(delivered=True, message_id=None, stubbed=True)

        payload: dict[str, Any] = {
            "From": from_email or self._default_from,
            "To": to,
            "Subject": subject,
            "TextBody": text_body,
            "MessageStream": message_stream,
        }
        if html_body is not None:
            payload["HtmlBody"] = html_body
        if reply_to is not None:
            payload["ReplyTo"] = reply_to
        if metadata:
            payload["Metadata"] = metadata
        if tag is not None:
            payload["Tag"] = tag
        if attachments:
            payload["Attachments"] = [
                {
                    "Name": a.name,
                    "Content": base64.b64encode(a.content).decode("ascii"),
                    "ContentType": a.content_type,
                }
                for a in attachments
            ]

        try:
            resp = httpx.post(
                f"{_POSTMARK_API}/email",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Postmark-Server-Token": self._api_token,
                },
                json=payload,
                timeout=_POSTMARK_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            logger.exception("Postmark send failed (transport)", extra={"to": to})
            return PostmarkSendResult(
                delivered=False,
                message_id=None,
                error_code=-1,
                error_message=f"transport: {exc}",
            )

        try:
            data = resp.json()
        except ValueError:
            data = {}

        # Postmark uses ErrorCode=0 for success, non-zero for failure. HTTP 200
        # with ErrorCode != 0 is still a failure (e.g., suppressed recipient).
        # See https://postmarkapp.com/developer/api/email-api
        error_code = int(data.get("ErrorCode", 0)) if data else None
        if resp.status_code == 200 and error_code == 0:
            return PostmarkSendResult(
                delivered=True,
                message_id=str(data.get("MessageID") or "") or None,
            )

        message = str(data.get("Message", resp.text)) if data else resp.text
        logger.warning(
            "Postmark send failed: status=%s error_code=%s message=%s",
            resp.status_code,
            error_code,
            message,
        )
        return PostmarkSendResult(
            delivered=False,
            message_id=None,
            error_code=error_code if error_code is not None else resp.status_code,
            error_message=message,
        )


# Module-level instance for callers that don't need to inject — most of the app.
# Tests should construct their own with a pinned token + httpx mock.
_default_client: PostmarkClient | None = None


def get_postmark_client() -> PostmarkClient:
    global _default_client
    if _default_client is None:
        _default_client = PostmarkClient()
    return _default_client


def reset_default_client() -> None:
    """Test helper — drop the cached singleton so settings reloads pick up env changes."""
    global _default_client
    _default_client = None
