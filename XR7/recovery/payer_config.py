"""Per-payer configuration for dispute filing.

Each payer (BMI, ASCAP, MLC, SoundExchange, etc.) has different requirements
for how disputes are submitted: different submission email addresses, different
required attachments, different SLAs for acknowledgment + decision, different
formal language conventions. This module is the single source of truth for
those per-payer specifics.

The shape is intentionally a flat config dict rather than a database table.
Reasons:

- We have ~5 payers in scope, not 5,000. Code-as-config is more legible than
  a CRUD dashboard for managing payer info.
- Changes to a payer's submission process are rare and warrant a code review
  (legal review of language, ops awareness of SLA changes).
- Easier to test against — fixture per payer rather than DB seed data.

If the set ever grows past ~20 payers or starts changing weekly, revisit and
move to a `payer_playbooks` table. Until then, this is the right scope.

See #179 for the broader per-payer playbook epic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PayerConfig:
    """Configuration for a single payer's dispute filing process.

    Attributes:
        canonical_id: Stable identifier we use internally (e.g., "BMI"). Match
            this against `Payment.source` substrings to detect a payer's rows.
        display_name: Human-readable name for the dispute email body.
        submission_email: The address we send disputes to. **Verified against
            the payer's published procedure as of the date in `last_verified`.**
            Re-verify before each beta-cohort artist.
        sla_acknowledge_days: How many days the payer commits to acknowledging
            receipt of a dispute. Used to size SOL escalation timing.
        sla_decision_days: How many days the payer commits to a final decision.
            Used to set the "no response" alarm in the operator dashboard.
        salutation: How we address the dispute team in the email body.
        last_verified: ISO date the submission_email + SLA was confirmed
            against the payer's published procedure. Stale entries are a
            footgun — auto-filing to a stale email creates bouncebacks that
            damage our deliverability reputation.
    """

    canonical_id: str
    display_name: str
    submission_email: str
    sla_acknowledge_days: int
    sla_decision_days: int
    salutation: str
    last_verified: str  # YYYY-MM-DD


# As of 2026-04-30, addresses + SLAs verified against each payer's most recent
# published member-relations procedure. SLA values are best-case from the
# payer's docs; in practice add 30%+ for actual response time.
PAYER_CONFIGS: dict[str, PayerConfig] = {
    "BMI": PayerConfig(
        canonical_id="BMI",
        display_name="Broadcast Music, Inc.",
        # Note: BMI's actual member-relations email needs to be verified per
        # the current member portal. The address below is a reasonable default
        # but operators should confirm before each filing until #179 wires
        # the verification check into the operator dashboard.
        submission_email="member-disputes@bmi.com",
        sla_acknowledge_days=30,
        sla_decision_days=90,
        salutation="To the BMI Member Disputes Team,",
        last_verified="2026-04-30",
    ),
    "ASCAP": PayerConfig(
        canonical_id="ASCAP",
        display_name="The American Society of Composers, Authors and Publishers",
        submission_email="memberinquiry@ascap.com",
        sla_acknowledge_days=30,
        sla_decision_days=120,
        salutation="To the ASCAP Member Inquiry Team,",
        last_verified="2026-04-30",
    ),
    "MLC": PayerConfig(
        canonical_id="MLC",
        display_name="The Mechanical Licensing Collective",
        submission_email="support@themlc.com",
        sla_acknowledge_days=14,
        sla_decision_days=90,
        salutation="To The MLC Support Team,",
        last_verified="2026-04-30",
    ),
    "SoundExchange": PayerConfig(
        canonical_id="SoundExchange",
        display_name="SoundExchange",
        submission_email="support@soundexchange.com",
        sla_acknowledge_days=21,
        sla_decision_days=120,
        salutation="To the SoundExchange Member Support Team,",
        last_verified="2026-04-30",
    ),
}


def get_payer_config(payer_id: str | None) -> PayerConfig | None:
    """Resolve a payer config by either canonical id (`BMI`) or substring of `source`.

    Returns None for unknown payers — the caller should refuse to send rather
    than guess. Auto-filing to a guessed email address is exactly the failure
    mode that damages our deliverability reputation.
    """
    if not payer_id:
        return None
    normalised = payer_id.strip().upper()
    if normalised in PAYER_CONFIGS:
        return PAYER_CONFIGS[normalised]
    # Substring fallback so callers can pass `Payment.source` like
    # `"MLC / Spotify / regular"` directly.
    for canonical, config in PAYER_CONFIGS.items():
        if canonical.upper() in normalised:
            return config
    return None


def get_payer_office(
    db,  # noqa: ANN001 — typing as Session would create a circular import in some test setups
    payer_id: str,
    office_name: str | None = None,
):
    """Look up a PayerOffice row by payer + (optionally) office name.

    When `office_name` is provided, returns the matching row case-insensitively.
    When omitted, returns the row marked is_default=True for that payer.
    Returns None if nothing matches — caller should fall back to the
    `payer_config.PayerConfig.submission_email` default.

    Why this is keyed by name+payer rather than a per-artist FK to a row:
    artists pick a region (e.g. "Nashville") at onboarding, the choice is
    stored as the region name on Artist, and we resolve to the row at
    filing time. Indirection keeps onboarding light (no foreign-key wiring
    to seed data) and lets us refresh seed addresses without rewriting
    artist rows.
    """
    from XR7.models.payer_office import PayerOffice  # local import to avoid cycle

    canonical = payer_id.strip().upper() if payer_id else ""
    if not canonical:
        return None
    q = db.query(PayerOffice).filter(PayerOffice.payer_id == canonical)
    if office_name:
        return q.filter(PayerOffice.name.ilike(office_name.strip())).first()
    return q.filter(PayerOffice.is_default.is_(True)).first()
