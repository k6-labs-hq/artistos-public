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
        # NOTE: empty by design. BMI dispute submissions go to the
        # regional Writer/Publisher Relations office, not a single global
        # address. Look up the right office via
        # `XR7.recovery.payer_config.get_payer_office(db, "BMI", artist.bmi_office_name)`
        # at filing time and pass it to `deliver_dispute(office=...)`.
        # If we ever start defaulting to a single address again, update
        # this string AND the comment.
        submission_email="",
        sla_acknowledge_days=30,
        sla_decision_days=90,
        salutation="To the BMI Writer/Publisher Relations Team,",
        last_verified="2026-05-04",
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


def compute_payer_claim_deadline(
    payer_id: str,
    distribution_date,  # noqa: ANN001 — datetime.date or datetime.datetime
):
    """Return the contractual claim deadline for a single distribution date.

    BMI: 9 months from the distribution date per writer agreement
    paragraph 6(b)(iv) — the binding rule that supersedes the generic
    SOL on the cover page. Other payers don't have a vetted contractual
    deadline yet (ASCAP brief flags Article XIV, MLC has the statutory
    audit right with different math, SoundExchange has its own framework
    — pending attorney review of the four briefs in docs/runbooks/).

    Returns None when no contractual deadline applies to this payer
    (caller should fall back to the SOL deadline).
    """
    if not payer_id or not distribution_date:
        return None
    canonical = payer_id.strip().upper()
    if canonical != "BMI":
        # Other payers: defer until the attorney reviews the briefs.
        return None
    # Add 9 calendar months. Using simple month arithmetic (vs. a 270-day
    # heuristic) so e.g. Q3 2025 (period_end 2025-09-30) → 2026-06-30 reads
    # as a full quarter-aligned deadline.
    from datetime import date as _date  # noqa: PLC0415

    if hasattr(distribution_date, "date"):
        d = distribution_date.date()
    else:
        d = distribution_date
    year = d.year + (d.month + 9 - 1) // 12
    month = (d.month + 9 - 1) % 12 + 1
    # Clamp the day to the last day of the target month (e.g. Aug 31 + 9mo).
    import calendar as _cal  # noqa: PLC0415

    last_day = _cal.monthrange(year, month)[1]
    day = min(d.day, last_day)
    return _date(year, month, day)


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


# Map US state two-letter codes to the BMI Writer/Publisher Relations regional
# office that handles affiliates with mailing addresses in that state. Sourced
# from BMI's published regional territory map. We use this to skip the manual
# "where do your statements come from?" onboarding gate when we can pull the
# affiliate's address out of the BMI PDF cover ourselves.
#
# When a state isn't covered (e.g. an artist with a foreign address, or a state
# we haven't mapped) we fall back to Nashville — the highest-volume office and
# the best default for unknown country/songwriters.
_STATE_TO_BMI_OFFICE: dict[str, str] = {
    # Nashville — Southeast + most of the country/folk corridor
    "TN": "Nashville", "KY": "Nashville", "AL": "Nashville", "MS": "Nashville",
    "AR": "Nashville", "WV": "Nashville", "VA": "Nashville", "NC": "Nashville",
    "SC": "Nashville", "IN": "Nashville", "OH": "Nashville", "MI": "Nashville",
    "IL": "Nashville", "WI": "Nashville", "MO": "Nashville", "IA": "Nashville",
    "MN": "Nashville", "ND": "Nashville", "SD": "Nashville", "NE": "Nashville",
    "KS": "Nashville", "OK": "Nashville",
    # Atlanta — Southeast pop/R&B/hip-hop
    "GA": "Atlanta", "FL": "Atlanta",
    # New York — Northeast + mid-Atlantic
    "NY": "New York", "NJ": "New York", "PA": "New York", "CT": "New York",
    "MA": "New York", "RI": "New York", "VT": "New York", "NH": "New York",
    "ME": "New York", "MD": "New York", "DE": "New York", "DC": "New York",
    # Los Angeles — West Coast + Mountain
    "CA": "Los Angeles", "OR": "Los Angeles", "WA": "Los Angeles",
    "NV": "Los Angeles", "AZ": "Los Angeles", "UT": "Los Angeles",
    "ID": "Los Angeles", "MT": "Los Angeles", "WY": "Los Angeles",
    "CO": "Los Angeles", "NM": "Los Angeles", "AK": "Los Angeles",
    "HI": "Los Angeles",
    # Austin — Texas + Louisiana
    "TX": "Austin", "LA": "Austin",
}


def infer_bmi_office_from_state(state_code: str | None) -> str:
    """Map a US state code to the BMI regional office handling that territory.

    Falls back to Nashville for unknown / missing states — Nashville is the
    largest BMI office and a safe default when an artist's PDF cover doesn't
    include a parseable mailing address.
    """
    if not state_code:
        return "Nashville"
    return _STATE_TO_BMI_OFFICE.get(state_code.strip().upper(), "Nashville")
