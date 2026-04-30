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

import hmac
import json
import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.recovery.immutable_ledger import ImmutableLedgerService

router = APIRouter(tags=["postmark"])
logger = logging.getLogger(__name__)


@router.post("/webhooks/postmark/inbound")
async def postmark_inbound(
    request: Request,
    db: Session = Depends(get_db),
    x_postmark_webhook_token: str | None = Header(default=None, alias="X-Postmark-Webhook-Token"),
) -> dict:
    """Receive an inbound email reply from Postmark's parse webhook.

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
    if not x_postmark_webhook_token or not hmac.compare_digest(x_postmark_webhook_token, expected):
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Postmark's inbound format includes: From, To, Subject, MessageID,
    # InReplyTo, References, TextBody, HtmlBody, Headers[], Attachments[],
    # Metadata{}, Tag, MailboxHash, OriginalRecipient. See
    # https://postmarkapp.com/developer/user-guide/inbound/parse-an-email
    metadata = payload.get("Metadata") or {}
    artist_id = str(metadata.get("artist_id") or "") or None
    claim_id = str(metadata.get("claim_id") or "") or None

    summary = {
        "from": payload.get("From"),
        "subject": payload.get("Subject"),
        "message_id": payload.get("MessageID"),
        "in_reply_to": payload.get("InReplyTo"),
        "tag": payload.get("Tag"),
        "claim_id": claim_id,
        "artist_id": artist_id,
        "text_excerpt": (payload.get("TextBody") or "")[:500],
    }
    logger.info("postmark_inbound_received", extra=summary)

    # Persist into the immutable ledger so nothing is lost while the
    # per-payer correlation logic (#179) is still under construction.
    if artist_id:
        ImmutableLedgerService(db).append(
            artist_id,
            "inbound_email_received",
            {
                **summary,
                # Keep the full payload available for later replay; redacting
                # is the next-PR concern when we know what fields are sensitive.
                "raw_postmark_payload": payload,
            },
        )

    return {"status": "received"}
