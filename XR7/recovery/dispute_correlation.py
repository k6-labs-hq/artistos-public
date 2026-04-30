"""Outbound MessageID persistence + inbound reply correlation.

When we file a dispute via Postmark, the result includes a Postmark MessageID
that uniquely identifies the outbound email. When the payer replies, the
reply lands at our inbound parse webhook with an `InReplyTo` header pointing
at that MessageID. This module provides the persistence + lookup helpers
that connect the two ends.

Storage choice: appending to `Claim.communications` (existing JSON column)
rather than introducing a new table. Reasons:
- No migration required
- Naturally co-located with the claim's other audit history
- Works for the closed-beta volume; will need a separate `claim_messages`
  table + index when we hit ~10K claims

Trade-off: the inbound lookup walks a JSON column rather than hitting an
index. Fine at our scale (single-digit beta artists, single-digit messages
per claim). Revisit at scale.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.claim import Claim, ClaimStatus

logger = logging.getLogger(__name__)


def record_outbound_filing(
    claim: Claim,
    *,
    send_result: dict[str, Any],
    artist_id: str,
) -> None:
    """Append an outbound filing entry to Claim.communications and advance status.

    Mutates the claim in-place. Caller is responsible for committing the
    surrounding transaction.

    Status transition: any pre-FILED state → FILED on success. On failure
    (send_result.success=False) the claim stays at its current state and
    the caller should decide whether to retry, surface for review, or fail.
    """
    if not send_result.get("success"):
        # Don't advance status or record outbound if delivery failed —
        # otherwise we'd lie to ourselves about having filed something
        # that's actually still queued.
        logger.warning(
            "record_outbound_filing called with failed send_result; not recording",
            extra={"claim_id": claim.id, "error": send_result.get("error_message")},
        )
        return

    entry = {
        "direction": "outbound",
        "message_id": send_result.get("message_id"),
        "channel": send_result.get("channel"),
        "payer_id": send_result.get("payer_id"),
        "submission_address": send_result.get("submission_address"),
        "stubbed": send_result.get("stubbed", False),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artist_id": artist_id,
    }

    existing = list(claim.communications or [])
    existing.append(entry)
    claim.communications = existing

    # Advance status — only for the actual filing event, not for stub-mode
    # rehearsals. Stub mode is for testing the wiring, not for moving claims
    # through their real lifecycle.
    if not send_result.get("stubbed"):
        claim.status = ClaimStatus.FILED
        claim.proof_submitted_at = datetime.now(timezone.utc)

    claim.updated_at = datetime.now(timezone.utc)


def find_claim_by_outbound_message_id(db: Session, message_id: str | None) -> Claim | None:
    """Find the Claim whose outbound communications include this MessageID.

    Postmark's inbound parse webhook delivers replies with an `InReplyTo`
    header pointing at our original outbound MessageID. This is how we
    correlate "BMI replied to our dispute" back to a specific Claim.

    Returns None if no match — the inbound webhook should still accept
    and persist the inbound payload (in the immutable ledger) for operator
    review, just without auto-advancing a claim.
    """
    if not message_id:
        return None

    # Brute-force scan of claims with non-null communications. At our scale
    # this is fine; once we have >10K claims we'll add a claim_messages
    # table with a unique index on (message_id, direction).
    candidates = db.query(Claim).filter(Claim.communications.isnot(None)).all()
    for claim in candidates:
        for entry in claim.communications or []:
            if entry.get("direction") == "outbound" and entry.get("message_id") == message_id:
                return claim
    return None


def record_inbound_reply(
    claim: Claim,
    *,
    postmark_payload: dict[str, Any],
) -> None:
    """Append an inbound reply entry to Claim.communications and advance status.

    Mutates the claim in-place. Caller commits.

    Status transition: FILED → IN_REVIEW on first inbound reply. Subsequent
    replies don't change status — operator review handles further state
    transitions (ACCEPTED, FUNDS_RECEIVED, etc.) from the dashboard.

    Case-reference extraction (parsing "Case ID: BMI-DR-12345" from the
    body) is intentionally not done here. Operators can read the email
    body in the inbound payload and edit Claim.payer_case_reference
    manually. Auto-extraction is fragile and worth a dedicated effort
    once we see real reply patterns from each payer.
    """
    body_excerpt = (postmark_payload.get("TextBody") or "")[:1000]

    entry = {
        "direction": "inbound",
        "message_id": postmark_payload.get("MessageID"),
        "in_reply_to": postmark_payload.get("InReplyTo"),
        "from_address": postmark_payload.get("From"),
        "subject": postmark_payload.get("Subject"),
        "body_excerpt": body_excerpt,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

    existing = list(claim.communications or [])
    existing.append(entry)
    claim.communications = existing

    # First reply moves FILED → IN_REVIEW. Don't downgrade if already
    # past IN_REVIEW (e.g., ACCEPTED). Don't upgrade pre-FILED states
    # because a reply to nothing is nonsensical.
    if claim.status == ClaimStatus.FILED:
        claim.status = ClaimStatus.IN_REVIEW

    claim.updated_at = datetime.now(timezone.utc)
