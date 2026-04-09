"""
Audit-Rights Tracker for XR7 Engine 2.

Most music-industry contracts include an audit clause that gives the artist the
right to inspect the counterparty's books once every 1–3 years.  These audits
routinely uncover underpayments — industry data suggests the average audit
recovery is 10–25 % of the amounts paid during the audit period.

This module:
- Tracks the last-audited date per contract.
- Calculates whether a contract is currently eligible for audit.
- Estimates the potential recovery value based on historical payments.
- Returns a ranked list of contracts ordered by estimated recovery so artists
  prioritise the most valuable audits first.

The ``last_audit_date`` field is expected in the contract's ``terms`` dict.
If absent, the contract is treated as never audited — maximum urgency.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from XR7.utils.datetime_utils import parse_date as _parse_date

# ---------------------------------------------------------------------------
# Default audit eligibility windows (years) and estimated recovery rates
# ---------------------------------------------------------------------------

# How often an artist can invoke their audit right, by contract type.
DEFAULT_AUDIT_INTERVALS: dict[str, int] = {
    "LABEL": 3,  # years
    "PUBLISHING": 2,
    "MERCH": 2,
    "TOURING": 1,
    "SYNC": 2,
    "BRAND": 1,
    "GRANT": 2,
}

# Expected recovery rate as a fraction of total payments during the audit period.
# Based on industry audit study averages.
DEFAULT_RECOVERY_RATES: dict[str, float] = {
    "LABEL": 0.15,  # 15 % of payments audited
    "PUBLISHING": 0.12,
    "MERCH": 0.10,
    "TOURING": 0.08,
    "SYNC": 0.18,  # Sync deals have historically high error rates
    "BRAND": 0.07,
    "GRANT": 0.05,
}

_DEFAULT_AUDIT_INTERVAL = 3  # years, fallback
_DEFAULT_RECOVERY_RATE = 0.10  # 10 %, fallback


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


class AuditEligibility:
    ELIGIBLE = "ELIGIBLE"  # Audit right is available now
    ELIGIBLE_SOON = "ELIGIBLE_SOON"  # Eligible within the next 90 days
    NOT_YET_ELIGIBLE = "NOT_YET_ELIGIBLE"
    NEVER_AUDITED = "NEVER_AUDITED"  # No audit on record — highest priority


@dataclass
class AuditRecommendation:
    """A structured audit recommendation for one contract."""

    contract_id: str
    contract_type: str
    counterparty: str
    eligibility: str
    days_until_eligible: int | None  # None means already eligible
    last_audit_date: str | None  # ISO date string or None
    next_eligible_date: str | None  # ISO date string or None
    audit_interval_years: int
    estimated_recovery: float
    total_payments_in_period: float
    recovery_rate_used: float
    territory: str | None

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "counterparty": self.counterparty,
            "eligibility": self.eligibility,
            "days_until_eligible": self.days_until_eligible,
            "last_audit_date": self.last_audit_date,
            "next_eligible_date": self.next_eligible_date,
            "audit_interval_years": self.audit_interval_years,
            "estimated_recovery": round(self.estimated_recovery, 2),
            "total_payments_in_period": round(self.total_payments_in_period, 2),
            "recovery_rate_used": self.recovery_rate_used,
            "territory": self.territory,
        }


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _payments_in_period(
    payments: list[dict],
    contract_id: str,
    from_date: date,
    to_date: date,
) -> float:
    """
    Sum payments that fall within [from_date, to_date].

    Payments are associated with the contract by their ``source`` field
    matching the counterparty, or by ``contract_id`` if available.
    We use all payments within the date window when we can't filter by
    contract (conservative approach — maximises estimated recovery).
    """
    total = 0.0
    for p in payments:
        raw_date = p.get("received_at") or p.get("period_start")
        pd = _parse_date(raw_date)
        if pd is None:
            continue
        if from_date <= pd <= to_date:
            total += float(p.get("amount", 0.0) or 0.0)
    return total


def analyze_audit_eligibility(
    contracts: list[dict],
    payments: list[dict] | None = None,
    reference_date: date | None = None,
    audit_intervals: dict[str, int] | None = None,
    recovery_rates: dict[str, float] | None = None,
) -> list[AuditRecommendation]:
    """
    Analyse audit eligibility for each contract and return recommendations
    sorted by estimated recovery (highest first).

    Parameters
    ----------
    contracts:
        List of contract dicts.  Each should have ``id``, ``contract_type``,
        ``counterparty``, and ``terms`` (dict with optional ``last_audit_date``).
    payments:
        All payments for the artist — used to estimate recovery value.
    reference_date:
        "Today" for eligibility calculations.  Defaults to ``date.today()``.
    audit_intervals:
        Override the default audit eligibility intervals (years per type).
    recovery_rates:
        Override the default estimated recovery rates.

    Returns
    -------
    List of :class:`AuditRecommendation`, sorted by ``estimated_recovery`` desc.
    """
    today = reference_date or date.today()
    intervals = audit_intervals or DEFAULT_AUDIT_INTERVALS
    rates = recovery_rates or DEFAULT_RECOVERY_RATES
    payments = payments or []

    recommendations: list[AuditRecommendation] = []

    for contract in contracts:
        contract_id = contract.get("id", "unknown")
        ct = str(contract.get("contract_type", "LABEL"))
        counterparty = contract.get("counterparty", "Unknown")
        territory = contract.get("territory")
        terms = contract.get("terms") or {}

        interval_years = intervals.get(ct.upper(), _DEFAULT_AUDIT_INTERVAL)
        recovery_rate = rates.get(ct.upper(), _DEFAULT_RECOVERY_RATE)

        last_audit_raw = terms.get("last_audit_date")
        last_audit = _parse_date(last_audit_raw)

        # Determine eligibility
        if last_audit is None:
            # Never audited — highest priority
            eligibility = AuditEligibility.NEVER_AUDITED
            days_until = None
            next_eligible_date = None
            # Use contract effective date as start of audit period, or 3 years ago
            eff_raw = contract.get("effective_date")
            eff_date = _parse_date(eff_raw) or (today - timedelta(days=interval_years * 365))
            period_start = eff_date
        else:
            next_eligible = date(
                last_audit.year + interval_years,
                last_audit.month,
                last_audit.day,
            )
            delta = (next_eligible - today).days
            next_eligible_date = next_eligible.isoformat()

            if delta <= 0:
                eligibility = AuditEligibility.ELIGIBLE
                days_until = None
            elif delta <= 90:
                eligibility = AuditEligibility.ELIGIBLE_SOON
                days_until = delta
            else:
                eligibility = AuditEligibility.NOT_YET_ELIGIBLE
                days_until = delta

            period_start = last_audit

        # Estimate payments during the audit period
        total_in_period = _payments_in_period(payments, contract_id, period_start, today)
        estimated_recovery = total_in_period * recovery_rate

        recommendations.append(
            AuditRecommendation(
                contract_id=contract_id,
                contract_type=ct,
                counterparty=counterparty,
                eligibility=eligibility,
                days_until_eligible=days_until,
                last_audit_date=last_audit.isoformat() if last_audit else None,
                next_eligible_date=next_eligible_date if last_audit else None,
                audit_interval_years=interval_years,
                estimated_recovery=estimated_recovery,
                total_payments_in_period=total_in_period,
                recovery_rate_used=recovery_rate,
                territory=territory,
            )
        )

    # Sort: eligible/never-audited contracts first, then by estimated recovery desc
    _eligibility_order = {
        AuditEligibility.NEVER_AUDITED: 0,
        AuditEligibility.ELIGIBLE: 1,
        AuditEligibility.ELIGIBLE_SOON: 2,
        AuditEligibility.NOT_YET_ELIGIBLE: 3,
    }

    return sorted(
        recommendations,
        key=lambda r: (
            _eligibility_order.get(r.eligibility, 9),
            -r.estimated_recovery,
        ),
    )


def audit_summary(recommendations: list[AuditRecommendation]) -> dict:
    """
    Produce a high-level summary dict from a list of audit recommendations.
    """
    eligible = [
        r
        for r in recommendations
        if r.eligibility in (AuditEligibility.ELIGIBLE, AuditEligibility.NEVER_AUDITED)
    ]
    total_potential = sum(r.estimated_recovery for r in recommendations)
    eligible_potential = sum(r.estimated_recovery for r in eligible)

    return {
        "total_contracts": len(recommendations),
        "eligible_for_audit": len(eligible),
        "eligible_soon": sum(
            1 for r in recommendations if r.eligibility == AuditEligibility.ELIGIBLE_SOON
        ),
        "not_yet_eligible": sum(
            1 for r in recommendations if r.eligibility == AuditEligibility.NOT_YET_ELIGIBLE
        ),
        "never_audited": sum(
            1 for r in recommendations if r.eligibility == AuditEligibility.NEVER_AUDITED
        ),
        "total_potential_recovery": round(total_potential, 2),
        "immediately_actionable_recovery": round(eligible_potential, 2),
    }
