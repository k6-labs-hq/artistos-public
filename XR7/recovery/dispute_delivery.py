"""Real dispute delivery via Postmark.

This module replaces the previous "simulated" delivery stub. When called,
it actually sends a dispute email to the configured payer, with the
evidence packet PDF as an attachment, and returns a result dict the
caller can persist on the Claim row.

Authentication / authority model: every dispute is sent on behalf of an
artist who has signed a Limited Power of Attorney granting XR7 the right
to submit audit findings on their behalf. The email body cites the LPOA;
operators must confirm a signed LPOA exists before invoking this path.
The check belongs in the operator dashboard (#181) — this module assumes
the caller has already verified.

Threat model and safety:
- Stub mode: when POSTMARK_API_TOKEN is unset, the Postmark client logs
  and returns success without sending. Local dev and CI default to stub.
- Refuses unknown payers: if `payer_id` doesn't resolve to a configured
  PayerConfig, the function returns a failure result rather than guessing
  a submission email. Auto-filing to a guessed address damages our
  deliverability reputation.
- Pass-through errors: Postmark API failures (suppressed recipient,
  bounce, rate limit) propagate as a structured failure with the
  Postmark error code so the caller can decide whether to retry,
  flag for review, or escalate.

Called by `XR7.tasks.pipeline.submit_recovery_action` (the Celery task)
and by the operator dashboard's "file now" button (#181 territory).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from XR7.recovery.payer_config import PayerConfig, get_payer_config
from XR7.services.postmark_client import (
    PostmarkAttachment,
    get_postmark_client,
)
from xr7_common.settings import settings

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent.parent / "services" / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


# Plain-English labels for rule IDs surfaced to dispute recipients. Keeping
# the internal rule_id (e.g. HIGH_RETROACTIVE_PAYMENT_RATIO) in the email
# body reads as algorithmic / form-letter and undermines the audit framing
# per docs/runbooks/bmi-dispute-attorney-brief.md §3.6.
#
# Both `subtype` and `rule_id` keys are handled because the AnomalyEngine
# emits both (subtype on the model, rule_id in the feature_snapshot).
# When a finding's identifier doesn't match any key, fall through to a
# sentence-case'd version of the underscores.
_RULE_FRIENDLY_LABELS: dict[str, str] = {
    "HIGH_RETROACTIVE_PAYMENT_RATIO": "Retroactive Payment Pattern",
    "HIGH_RETROACTIVE_RATIO": "Retroactive Payment Pattern",
    "STREAM_MONTH_WITHOUT_PAYMENT": "Stream Activity Without Corresponding Payment",
    "STREAM_MONTH_NO_PAYMENT": "Stream Activity Without Corresponding Payment",
    "PAYMENT_GAP_OVER_60_DAYS": "Extended Payment Gap",
    "PAYMENT_GAP_OVER_60": "Extended Payment Gap",
    "TRACK_RATE_OUTLIER_UNDERPAYMENT": "Per-Stream Rate Outlier",
    "TRACK_RATE_OUTLIER": "Per-Stream Rate Outlier",
}


def _friendly_finding_label(rule_or_subtype: str | None) -> str:
    """Map an internal rule_id / subtype to a human-readable finding label."""
    if not rule_or_subtype:
        return "Royalty audit finding"
    key = str(rule_or_subtype).upper()
    if key in _RULE_FRIENDLY_LABELS:
        return _RULE_FRIENDLY_LABELS[key]
    # Fall back to title-casing the underscores: "FOO_BAR_BAZ" → "Foo Bar Baz"
    return key.replace("_", " ").title()


def _render_email_body(
    *,
    payer: PayerConfig,
    claim: dict[str, Any],
    artist: dict[str, Any],
    anomaly: dict[str, Any],
    office: dict[str, Any] | None = None,
    redirected: bool = False,
    intended_recipient: str | None = None,
    redirect_recipient: str | None = None,
) -> tuple[str, str]:
    """Render both plain-text and HTML bodies for the dispute email.

    Returns (text_body, html_body). Postmark prefers when both are
    supplied — clients with HTML rendering see the rich version; clients
    that prefer or only support plain text get the flowing-prose version.
    """
    # Compose the salutation. If we have a regional office, address the team
    # by office name (e.g. "BMI Writer/Publisher Relations Team — Nashville
    # Office") rather than the generic salutation in payer_config. The
    # generic one is the fallback for payers without office records.
    salutation = payer.salutation
    if office and office.get("name"):
        salutation = (
            f"To the {payer.display_name} Writer/Publisher Relations Team "
            f"— {office['name']} Office,"
        )

    # Contractual citation. Per docs/runbooks/bmi-dispute-attorney-brief.md
    # §3.4, citing paragraph 6(b)(iv) of the BMI writer agreement signals
    # that we know the contractual basis and are filing within the 9-month
    # window. Other payers don't have an equivalent citation we've vetted
    # yet — they get no citation block until the attorney brief covering
    # them is reviewed.
    contractual_citation = None
    if payer.canonical_id == "BMI":
        contractual_citation = (
            "Pursuant to paragraph 6(b)(iv) of the BMI writer affiliation "
            "agreement, this constitutes timely written notice of claimed "
            "omission or miscalculation. The 9-month claim window from the "
            "subject distribution date applies; we are filing within that "
            "window."
        )

    # Response date — 30 days out from filing as our internal escalation
    # marker. Per attorney brief §3.3, framed as our request, not the
    # payer's published commitment.
    response_requested_by = (
        datetime.now(timezone.utc) + timedelta(days=payer.sla_acknowledge_days)
    ).strftime("%Y-%m-%d")

    # Common context for both renders. Confidence percentage is intentionally
    # omitted — surfacing a "78% confidence" number to the recipient reads as
    # spammy / algorithmic and undermines the audit framing per Matt's review.
    #
    # Human-facing reference is `reference_number` (XR7-2026-ABCDEF); the
    # UUID stays internal for metadata + attachment naming. Falls back to
    # the UUID for back-compat if a caller passes a claim dict without a
    # reference_number set.
    claim_reference = claim.get("reference_number") or claim.get("id") or "(unset)"
    ctx = {
        "salutation": salutation,
        "artist_name": artist.get("name") or "(artist name not on file)",
        "artist_pro_id": artist.get("pro_id_for_payer"),
        "payer_id": payer.canonical_id,
        "payer_display_name": payer.display_name,
        "contractual_citation": contractual_citation,
        "finding_subtype": _friendly_finding_label(
            anomaly.get("subtype") or anomaly.get("rule_id")
        ),
        "finding_description": anomaly.get("description")
        or "See attached evidence packet for the full audit determination.",
        "estimated_recoverable": anomaly.get("estimated_recoverable"),
        "response_requested_by": response_requested_by,
        "claim_reference": claim_reference,
        # Kept for back-compat with templates that still reference {{ claim_id }};
        # new templates should use {{ claim_reference }}.
        "claim_id": claim_reference,
        "filing_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "redirected": redirected,
        "intended_recipient": intended_recipient or "",
        "redirect_recipient": redirect_recipient or "",
    }

    text_body = _jinja_env.get_template("dispute_email.txt").render(**ctx)
    html_body = _jinja_env.get_template("dispute_email.html").render(**ctx)
    
    return text_body, html_body


def deliver_dispute(
    *,
    claim: dict[str, Any],
    artist: dict[str, Any],
    anomaly: dict[str, Any],
    pdf_bytes: bytes,
    payer_id: str,
    office: dict[str, Any] | None = None,
    metadata_extra: dict[str, str] | None = None,
) -> dict[str, Any]:
    """File a dispute with the payer via email + PDF attachment.

    Returns a structured result dict. The caller is responsible for
    persisting the result onto the Claim row (status, message_id, etc.)
    and for appending an immutable-ledger entry for the filing.

    Args:
        claim: Claim dict — must contain at least `id`. `payer_name` is
            used for matching but `payer_id` is authoritative.
        artist: Artist dict — must contain `name` for the email salutation.
            Optional `pro_id_for_payer` improves correlation on the payer's
            side (e.g., the BMI member id).
        anomaly: Anomaly finding dict — `subtype`, `description`,
            `estimated_recoverable`, `confidence_score`. Used for the
            email body summary.
        pdf_bytes: Rendered evidence packet PDF (use
            `XR7.services.evidence_packet_pdf.render_evidence_packet_pdf`).
        payer_id: Canonical payer identifier (`BMI`, `ASCAP`, `MLC`,
            `SoundExchange`). Resolved via `XR7.recovery.payer_config`.
            Returns failure result for unknown payers.
        metadata_extra: Additional key/value pairs to attach as Postmark
            metadata. The keys `claim_id`, `artist_id`, `payer_id` are
            always set by this function and override whatever's in
            metadata_extra.

    Returns:
        {
            "success": bool,
            "channel": "email" | "none",
            "payer_id": str,
            "submission_address": str | None,
            "message_id": str | None,
            "error_code": int | None,
            "error_message": str | None,
            "stubbed": bool,
        }
    """
    payer = get_payer_config(payer_id)
    if payer is None:
        logger.warning("Unknown payer_id=%s; refusing to file (no submission email)", payer_id)
        return {
            "success": False,
            "channel": "none",
            "payer_id": payer_id,
            "submission_address": None,
            "message_id": None,
            "error_code": -1,
            "error_message": f"Unknown payer '{payer_id}'; no configured submission address",
            "stubbed": False,
        }

    # Submission email source-of-truth ranking:
    #   1. The payer_office row passed in by the caller (per-artist routing —
    #      e.g. an artist whose BMI region is "New York" gets newyork@bmi.com)
    #   2. payer_config.PayerConfig.submission_email (legacy default — we're
    #      moving away from this for BMI since the placeholder bounces, but
    #      it remains the fallback for payers we don't have office records
    #      seeded for yet)
    submission_email = (
        (office or {}).get("submission_email") or payer.submission_email
    )
    if not submission_email:
        return {
            "success": False,
            "channel": "none",
            "payer_id": payer_id,
            "submission_address": None,
            "message_id": None,
            "error_code": -2,
            "error_message": (
                f"No submission_email available for payer '{payer_id}' — caller must "
                "supply a payer_office or the payer_config default must be set"
            ),
            "stubbed": False,
        }

    # Test-mode redirect. When XR7_DISPUTE_REDIRECT_EMAIL is set, every
    # outbound dispute is rerouted to that address instead of the payer's
    # real submission inbox. Use this while the packet/email body is
    # under review (attorney, internal QA) so we can fly the full pipeline
    # — Postmark send, MessageID persistence, status advance — without
    # actually contacting the payer. Unset the env var to fly real
    # disputes.
    redirect_email = (os.environ.get("XR7_DISPUTE_REDIRECT_EMAIL") or "").strip()
    intended_recipient = submission_email
    redirected = bool(redirect_email)
    if redirected:
        logger.info(
            "Dispute redirect active: %s -> %s (claim=%s)",
            intended_recipient,
            redirect_email,
            claim.get("id"),
        )
        submission_email = redirect_email

    text_body, html_body = _render_email_body(
        payer=payer,
        claim=claim,
        artist=artist,
        anomaly=anomaly,
        office=office,
        redirected=redirected,
        intended_recipient=intended_recipient,
        redirect_recipient=redirect_email if redirected else None,
    )

    claim_reference = claim.get("reference_number") or claim.get("id") or ""
    metadata: dict[str, str] = {
        "claim_id": str(claim.get("id") or ""),
        "claim_reference": claim_reference,
        "artist_id": str(artist.get("id") or ""),
        "payer_id": payer.canonical_id,
        "intended_recipient": intended_recipient,
        "redirected": "true" if redirect_email else "false",
    }
    if metadata_extra:
        for k, v in metadata_extra.items():
            if k not in metadata:
                metadata[k] = str(v)

    attachment = PostmarkAttachment(
        name=f"xr7-evidence-{claim_reference or 'packet'}.pdf",
        content=pdf_bytes,
        content_type="application/pdf",
    )

    subject_prefix = "[XR7 INTERNAL REVIEW] " if redirected else ""
    subject = (
        f"{subject_prefix}Royalty audit finding for "
        f"{artist.get('name') or 'XR7-represented artist'} — "
        f"{claim_reference or '(pending)'}"
    )

    client = get_postmark_client()
    result = client.send_email(
        to=submission_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        from_email=settings.POSTMARK_DISPUTES_FROM_EMAIL,
        reply_to=settings.POSTMARK_DISPUTES_FROM_EMAIL,
        tag=f"dispute-{payer.canonical_id.lower()}",
        metadata=metadata,
        attachments=[attachment],
    )

    return {
        "success": result.delivered,
        "channel": "email",
        "payer_id": payer.canonical_id,
        "submission_address": submission_email,
        "intended_recipient": intended_recipient,
        "redirected": redirected,
        "message_id": result.message_id,
        "error_code": result.error_code,
        "error_message": result.error_message,
        "stubbed": result.stubbed,
    }
