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
from datetime import datetime, timezone
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


def _render_email_body(
    *,
    payer: PayerConfig,
    claim: dict[str, Any],
    artist: dict[str, Any],
    anomaly: dict[str, Any],
) -> str:
    """Render the dispute email body from the Jinja template."""
    confidence = anomaly.get("confidence_score")
    confidence_pct = f"{int(round(float(confidence) * 100))}" if confidence is not None else None

    template = _jinja_env.get_template("dispute_email.txt")
    return template.render(
        salutation=payer.salutation,
        artist_name=artist.get("name") or "(artist name not on file)",
        artist_pro_id=artist.get("pro_id_for_payer"),
        payer_id=payer.canonical_id,
        payer_display_name=payer.display_name,
        finding_subtype=anomaly.get("subtype") or anomaly.get("rule_id") or "Royalty audit finding",
        finding_description=anomaly.get("description")
        or "See attached evidence packet for the full audit determination.",
        estimated_recoverable=anomaly.get("estimated_recoverable"),
        confidence_pct=confidence_pct,
        sla_acknowledge_days=payer.sla_acknowledge_days,
        sla_decision_days=payer.sla_decision_days,
        claim_id=claim.get("id") or "(unset)",
        filing_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


def deliver_dispute(
    *,
    claim: dict[str, Any],
    artist: dict[str, Any],
    anomaly: dict[str, Any],
    pdf_bytes: bytes,
    payer_id: str,
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

    body = _render_email_body(payer=payer, claim=claim, artist=artist, anomaly=anomaly)

    metadata: dict[str, str] = {
        "claim_id": str(claim.get("id") or ""),
        "artist_id": str(artist.get("id") or ""),
        "payer_id": payer.canonical_id,
    }
    if metadata_extra:
        for k, v in metadata_extra.items():
            if k not in metadata:
                metadata[k] = str(v)

    attachment = PostmarkAttachment(
        name=f"xr7-evidence-{claim.get('id') or 'packet'}.pdf",
        content=pdf_bytes,
        content_type="application/pdf",
    )

    subject = (
        f"Royalty audit finding for {artist.get('name') or 'XR7-represented artist'} — "
        f"claim {claim.get('id') or '(pending)'}"
    )

    client = get_postmark_client()
    result = client.send_email(
        to=payer.submission_email,
        subject=subject,
        text_body=body,
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
        "submission_address": payer.submission_email,
        "message_id": result.message_id,
        "error_code": result.error_code,
        "error_message": result.error_message,
        "stubbed": result.stubbed,
    }
