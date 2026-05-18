"""Human-readable labels for internal anomaly rule identifiers.

Recipient-facing surfaces — the dispute email and the evidence packet
PDF — must never show in-house rule names like ``STREAM_MONTH_NO_PAYMENT``
or enum values like ``ROYALTY`` / ``HIGH``. A payer's investigator reading
``Rule ID: STREAM_MONTH_NO_PAYMENT`` reads it as algorithmic output and
discounts the claim; the audit framing depends on plain-language
findings.

This module is the single source of truth for that mapping. Both
``dispute_delivery`` (email) and ``evidence_packet_pdf`` (PDF) import
from here so the two surfaces never drift.
"""

from __future__ import annotations

# Both `subtype` (on the Anomaly model) and `rule_id` (in the
# feature_snapshot) are handled — the engine emits both spellings.
_RULE_FRIENDLY_LABELS: dict[str, str] = {
    "HIGH_RETROACTIVE_PAYMENT_RATIO": "Retroactive Payment Pattern",
    "HIGH_RETROACTIVE_RATIO": "Retroactive Payment Pattern",
    "STREAM_MONTH_WITHOUT_PAYMENT": "Stream Activity Without Corresponding Payment",
    "STREAM_MONTH_NO_PAYMENT": "Stream Activity Without Corresponding Payment",
    "PAYMENT_GAP_OVER_60_DAYS": "Extended Payment Gap",
    "PAYMENT_GAP_OVER_60": "Extended Payment Gap",
    "TRACK_RATE_OUTLIER_UNDERPAYMENT": "Per-Stream Rate Outlier",
    "TRACK_RATE_OUTLIER": "Per-Stream Rate Outlier",
    "STREAM_PAYOUT_BELOW_50PCT": "Streaming Payout Below Market Baseline",
    "STREAM_PAYOUT_UNDER_50": "Streaming Payout Below Market Baseline",
    "CONTRACT_RATE_DEVIATION_OVER_20PCT": "Contract Rate Deviation",
    "CONTRACT_RATE_DEVIATION_OVER_20": "Contract Rate Deviation",
    "PAYMENT_CONCENTRATION": "Payment Concentration Risk",
}


def friendly_finding_label(rule_or_subtype: str | None) -> str:
    """Map an internal rule_id / subtype to a human-readable finding label.

    Falls back to title-casing the underscores for unmapped identifiers
    (``FOO_BAR`` → ``Foo Bar``) — never leaks a raw SCREAMING_SNAKE id.
    """
    if not rule_or_subtype:
        return "Royalty audit finding"
    key = str(rule_or_subtype).upper()
    if key in _RULE_FRIENDLY_LABELS:
        return _RULE_FRIENDLY_LABELS[key]
    return key.replace("_", " ").title()
