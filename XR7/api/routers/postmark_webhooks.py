"""Postmark inbound parse webhook.

Postmark POSTs JSON to this endpoint when someone replies to an email we sent
(e.g., BMI replies to a dispute filing with a case-reference number). The
payload includes the original email metadata, the reply body, and the
`Metadata` we attached when sending — which is how we correlate the reply
back to the originating Claim row.

Setup:
- In Postmark, point the inbound webhook for the relevant server at
  `https://api.qa.xr7.k6-labs.com/webhooks/postmark/inbound`
- Set `POSTMARK_INBOUND_WEBHOOK_TOKEN` to a strong random string and add
  it as a Basic Auth or custom header on the Postmark side; we validate it
  here. Without the env var set, the webhook returns 401 — never silently
  accepts unauthenticated payloads.

Tonight's scope is intentionally minimal: validate, log, and store the
inbound payload in the immutable ledger so we don't lose anything during
the per-payer playbook build (#179). The actual claim-correlation logic
ships with that work.
"""

from __future__ import annotations

import base64
import binascii
import hmac
import json
import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.recovery.dispute_correlation import (
    find_claim_by_outbound_message_id,
    record_inbound_reply,
)
from XR7.recovery.immutable_ledger import ImmutableLedgerService

router = APIRouter(tags=["postmark"])
logger = logging.getLogger(__name__)


def _basic_auth_password(authorization_header: str | None) -> str | None:
    """Extract the password component from an `Authorization: Basic <base64>` header.

    Postmark's inbound webhook authentication is "Basic Auth in the URL" — when
    the configured webhook URL is `https://user:secret@host/path`, Postmark
    sends `Authorization: Basic base64(user:secret)` on every POST. Returns the
    decoded password (everything after the first `:`), or None on any failure.
    """
    if not authorization_header:
        return None
    parts = authorization_header.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "basic":
        return None
    try:
        decoded = base64.b64decode(parts[1], validate=True).decode("utf-8", errors="replace")
    except (binascii.Error, UnicodeDecodeError):
        return None
    _, _, password = decoded.partition(":")
    return password or None


def _verify_inbound_auth(
    *,
    custom_header_value: str | None,
    authorization_header: str | None,
    expected: str,
) -> bool:
    """Return True if either auth path matches the expected secret.

    Two transports supported:
    - `X-Postmark-Webhook-Token: <secret>` (custom header, what curl tests use)
    - `Authorization: Basic <base64(any:secret)>` (what Postmark itself sends
      when the webhook URL is `https://user:secret@host/path`)

    Both routes hash the same `POSTMARK_INBOUND_WEBHOOK_TOKEN`. Constant-time
    compare via hmac.compare_digest to avoid timing-leak.
    """
    if custom_header_value and hmac.compare_digest(custom_header_value, expected):
        return True
    basic_password = _basic_auth_password(authorization_header)
    if basic_password and hmac.compare_digest(basic_password, expected):
        return True
    return False


@router.post("/webhooks/postmark/inbound")
async def postmark_inbound(
    request: Request,
    db: Session = Depends(get_db),
    x_postmark_webhook_token: str | None = Header(default=None, alias="X-Postmark-Webhook-Token"),
    authorization: str | None = Header(default=None),
) -> dict:
    """Receive an inbound email reply from Postmark's parse webhook.

    Authenticates via either:
    - X-Postmark-Webhook-Token header (curl-friendly, what tests use)
    - HTTP Basic Auth (what Postmark itself sends when the webhook URL
      is configured as `https://user:secret@host/path`)

    Returns 200 quickly so Postmark doesn't retry on slow processing.
    The actual claim-correlation work happens later via the immutable
    ledger entry this writes.
    """
    # Read at request time (not import time) so the test harness and
    # rotating secrets both see the current value. Same pattern as
    # /webhooks/trolley.
    expected = os.environ.get("POSTMARK_INBOUND_WEBHOOK_TOKEN")
    if not expected:
        # Hard fail: never accept unauthenticated webhook traffic. If the env
        # var isn't set, the endpoint isn't ready to receive — return 503 so
        # ops sees the misconfiguration in monitoring instead of letting
        # forged payloads through.
        raise HTTPException(
            status_code=503,
            detail="Inbound webhook not configured (POSTMARK_INBOUND_WEBHOOK_TOKEN unset)",
        )
    if not _verify_inbound_auth(
        custom_header_value=x_postmark_webhook_token,
        authorization_header=authorization,
        expected=expected,
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook auth")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Postmark's inbound format includes: From, To, Subject, MessageID,
    # InReplyTo, References, TextBody, HtmlBody, Headers[], Attachments[],
    # Metadata{}, Tag, MailboxHash, OriginalRecipient. See
    # https://postmarkapp.com/developer/user-guide/inbound/parse-an-email
    metadata = payload.get("Metadata") or {}
    in_reply_to = payload.get("InReplyTo") or None
    artist_id_meta = str(metadata.get("artist_id") or "") or None
    claim_id_meta = str(metadata.get("claim_id") or "") or None

    summary = {
        "from": payload.get("From"),
        "subject": payload.get("Subject"),
        "message_id": payload.get("MessageID"),
        "in_reply_to": in_reply_to,
        "tag": payload.get("Tag"),
        "claim_id_metadata": claim_id_meta,
        "artist_id_metadata": artist_id_meta,
        "text_excerpt": (payload.get("TextBody") or "")[:500],
    }
    logger.info("postmark_inbound_received", extra=summary)

    # Try to correlate this reply to a specific Claim by matching the
    # InReplyTo header against any outbound MessageID we've recorded in
    # Claim.communications. If we find a match, append the inbound to the
    # claim's communications and advance status (FILED → IN_REVIEW). If we
    # don't match (e.g., manual email to disputes@ from a non-XR7 sender),
    # we still log to the immutable ledger for operator review — never
    # silently drop inbound traffic.
    correlated_claim = find_claim_by_outbound_message_id(db, in_reply_to)
    correlated_claim_id: str | None = None
    correlated_artist_id: str | None = None
    if correlated_claim is not None:
        record_inbound_reply(correlated_claim, postmark_payload=payload)
        db.commit()
        correlated_claim_id = correlated_claim.id
        correlated_artist_id = correlated_claim.artist_id
        logger.info(
            "postmark_inbound_correlated",
            extra={
                "claim_id": correlated_claim.id,
                "in_reply_to": in_reply_to,
                "new_status": str(correlated_claim.status),
            },
        )

    # Persist into the immutable ledger as well — captures correlated AND
    # uncorrelated inbound traffic for audit. Use the correlated artist_id
    # when available, fall back to the metadata-supplied one.
    artist_id = correlated_artist_id or artist_id_meta
    if artist_id:
        ImmutableLedgerService(db).append(
            artist_id,
            "inbound_email_received",
            {
                **summary,
                "correlated_claim_id": correlated_claim_id,
                # Keep the full payload available for later replay; redacting
                # is the next-PR concern when we know what fields are sensitive.
                "raw_postmark_payload": payload,
            },
        )

    return {
        "status": "received",
        "correlated_claim_id": correlated_claim_id,
    }
