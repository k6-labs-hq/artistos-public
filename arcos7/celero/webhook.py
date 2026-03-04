"""
Celero Commerce Webhook Handler for ARCOS7 Engine 2.

Celero sends real-time event notifications to ``POST /celero/webhook``
whenever a transaction changes state.  Every incoming request is validated
with an HMAC-SHA256 signature before any processing occurs.

Configuration
-------------
``CELERO_WEBHOOK_SECRET``
    The shared secret configured in the Celero merchant dashboard under
    Settings → Webhooks.  All incoming webhook requests must have an
    ``X-Celero-Signature`` header containing
    ``HMAC-SHA256(secret, raw_request_body)``.

    If this variable is not set, webhook signature validation is skipped
    **in development only** (``ARCOS7_ENV != production``).  In production
    the secret is mandatory.

Supported event types
---------------------
``transaction.approved``
    A charge or sale was approved.  ARCOS7 marks the corresponding
    CeleroTransaction as APPROVED and, if it is a contingency-fee charge,
    advances the Claim to CLOSED.

``transaction.declined``
    A charge was declined.  CeleroTransaction is marked DECLINED.

``transaction.void``
    A transaction was voided.  CeleroTransaction is marked VOIDED.

``transaction.refund``
    A refund was issued.  CeleroTransaction is marked REFUNDED.

``disbursement.settled``
    An ACH payout to an artist has settled.  CeleroTransaction is marked
    SETTLED.

``disbursement.failed``
    An ACH payout failed.  CeleroTransaction is marked FAILED.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported event types
# ---------------------------------------------------------------------------

EVENT_TRANSACTION_APPROVED = "transaction.approved"
EVENT_TRANSACTION_DECLINED = "transaction.declined"
EVENT_TRANSACTION_VOID = "transaction.void"
EVENT_TRANSACTION_REFUND = "transaction.refund"
EVENT_DISBURSEMENT_SETTLED = "disbursement.settled"
EVENT_DISBURSEMENT_FAILED = "disbursement.failed"

ALL_EVENTS = {
    EVENT_TRANSACTION_APPROVED,
    EVENT_TRANSACTION_DECLINED,
    EVENT_TRANSACTION_VOID,
    EVENT_TRANSACTION_REFUND,
    EVENT_DISBURSEMENT_SETTLED,
    EVENT_DISBURSEMENT_FAILED,
}

# CeleroTransaction status values that map from event types
_EVENT_TO_STATUS: dict[str, str] = {
    EVENT_TRANSACTION_APPROVED: "APPROVED",
    EVENT_TRANSACTION_DECLINED: "DECLINED",
    EVENT_TRANSACTION_VOID: "VOIDED",
    EVENT_TRANSACTION_REFUND: "REFUNDED",
    EVENT_DISBURSEMENT_SETTLED: "SETTLED",
    EVENT_DISBURSEMENT_FAILED: "FAILED",
}


# ---------------------------------------------------------------------------
# Signature validation
# ---------------------------------------------------------------------------

def validate_signature(
    raw_body: bytes,
    signature_header: str,
    webhook_secret: str | None = None,
) -> bool:
    """
    Validate an incoming Celero webhook signature.

    Celero computes ``HMAC-SHA256(webhook_secret, raw_body)`` and sends it
    as the ``X-Celero-Signature`` header (hex-encoded).

    Parameters
    ----------
    raw_body:
        The raw bytes of the HTTP request body — **must not** be parsed
        before validation.
    signature_header:
        The value of the ``X-Celero-Signature`` request header.
    webhook_secret:
        Override the ``CELERO_WEBHOOK_SECRET`` env var for testing.

    Returns
    -------
    ``True`` if the signature matches, ``False`` otherwise.
    Raises ``ValueError`` if no secret is configured in production.
    """
    secret = webhook_secret or os.environ.get("CELERO_WEBHOOK_SECRET", "")
    env = os.environ.get("ARCOS7_ENV", "development").lower()

    if not secret:
        if env == "production":
            raise ValueError(
                "CELERO_WEBHOOK_SECRET must be set in production.  "
                "Configure it in the Celero merchant dashboard under "
                "Settings → Webhooks, then set the env var."
            )
        # Development: skip validation with a warning
        logger.warning(
            "CELERO_WEBHOOK_SECRET is not set — skipping webhook signature "
            "validation.  Set this variable before going to production."
        )
        return True

    if not signature_header:
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected.lower(), signature_header.lower())


# ---------------------------------------------------------------------------
# Event parsing
# ---------------------------------------------------------------------------

def parse_event(raw_body: bytes) -> dict[str, Any]:
    """
    Parse a Celero webhook payload.

    Celero sends JSON payloads.  This function decodes the body and returns
    the event dict.  Raises ``ValueError`` on malformed payloads.
    """
    try:
        event = json.loads(raw_body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid webhook payload: {exc}") from exc

    if not isinstance(event, dict):
        raise ValueError("Webhook payload must be a JSON object.")

    event_type = event.get("event_type") or event.get("type", "")
    if not event_type:
        raise ValueError("Webhook payload missing 'event_type' field.")

    return event


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

class CeleroWebhookHandler:
    """
    Stateless handler for Celero webhook events.

    The ``handle()`` method is called from the FastAPI webhook endpoint
    after signature validation.  It updates the CeleroTransaction record
    and, for fee-charge events, advances the associated Claim.

    Parameters
    ----------
    db_session:
        SQLAlchemy session — injected from FastAPI dependency.
    """

    def __init__(self, db_session: Any) -> None:
        self.db = db_session

    def handle(self, event: dict) -> dict:
        """
        Dispatch a parsed webhook event to the appropriate handler.

        Returns a summary dict describing what was updated.
        """
        event_type = event.get("event_type") or event.get("type", "")
        celero_txn_id = (
            event.get("transaction_id")
            or event.get("transactionid")
            or ""
        )
        new_status = _EVENT_TO_STATUS.get(event_type)

        if not new_status:
            logger.warning("Received unknown Celero webhook event type: %s", event_type)
            return {"handled": False, "reason": f"Unknown event type: {event_type}"}

        if not celero_txn_id:
            logger.warning("Celero webhook missing transaction_id for event %s", event_type)
            return {"handled": False, "reason": "Missing transaction_id"}

        # Import here to avoid circular import at module load time
        from arcos7.models.celero_transaction import CeleroTransaction, CeleroTxnStatus
        from arcos7.models.claim import Claim, ClaimStatus

        # Find the matching transaction record
        txn = (
            self.db.query(CeleroTransaction)
            .filter(CeleroTransaction.celero_transaction_id == celero_txn_id)
            .first()
        )

        if not txn:
            logger.info(
                "No CeleroTransaction found for celero_transaction_id=%s — "
                "event may be for a transaction not yet recorded locally.",
                celero_txn_id,
            )
            return {
                "handled": False,
                "reason": f"No local transaction found for celero_transaction_id={celero_txn_id}",
            }

        # Update transaction status
        try:
            txn.status = CeleroTxnStatus(new_status)
        except ValueError:
            txn.status = new_status  # type: ignore[assignment]
        txn.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        result: dict = {
            "handled": True,
            "event_type": event_type,
            "celero_transaction_id": celero_txn_id,
            "new_status": new_status,
            "arcos7_transaction_id": txn.id,
        }

        # For approved contingency-fee charges: advance associated claim to CLOSED
        if event_type == EVENT_TRANSACTION_APPROVED and txn.type == "CHARGE" and txn.claim_id:
            claim = self.db.query(Claim).filter(Claim.id == txn.claim_id).first()
            if claim and ClaimStatus(claim.status) == ClaimStatus.PAID:
                claim.status = ClaimStatus.CLOSED
                self.db.commit()
                result["claim_advanced_to"] = "CLOSED"

        return result
