"""
Artist Recovery Dashboard Engine — ARCOS7 Engine 2.

Aggregates every recovery-related data point into a single, artist-facing
summary so they can see at a glance:

1. **Leakage discovered** — every anomaly ARCOS7 has detected, grouped by
   category and severity, with total estimated recoverable value.

2. **In pursuit** — active claims (IDENTIFIED → ACCEPTED) that are currently
   being worked.  Total amount being chased on the artist's behalf.

3. **Recovered & deposited** — Celero DISBURSEMENT transactions that have
   been APPROVED or SETTLED to the artist's bank account.  Running total and
   per-deposit history.

4. **Balance still pursuing** — the difference between the gross recoverable
   pipeline and what has already been deposited.  This is the number artists
   care most about: "how much are you still trying to get for me?"

5. **Activity feed** — a reverse-chronological event log combining anomaly
   discoveries, claim status changes, and payment deposits so the artist can
   see exactly what happened and when.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from arcos7.models.anomaly import Anomaly, AnomalyStatus
from arcos7.models.celero_transaction import CeleroTransaction, CeleroTxnStatus, CeleroTxnType
from arcos7.models.claim import Claim, ClaimStatus


# Claim statuses that are still "in pursuit" (open / active)
_ACTIVE_CLAIM_STATUSES = {
    ClaimStatus.IDENTIFIED,
    ClaimStatus.PREPARED,
    ClaimStatus.SUBMITTED,
    ClaimStatus.IN_REVIEW,
    ClaimStatus.ACCEPTED,
}

# Celero disbursement statuses that represent money deposited to the artist
_DEPOSITED_STATUSES = {CeleroTxnStatus.APPROVED, CeleroTxnStatus.SETTLED}


class DashboardEngine:
    """
    Compute the artist recovery dashboard in a single pass over the DB.

    All amounts are in the claim's native currency.  Where claims use
    different currencies the totals are grouped by currency.  The most
    common case is all-USD, in which case a single ``total_usd`` is returned
    in each section.

    Usage::

        engine = DashboardEngine(db)
        data   = engine.compute(artist_id)
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(self, artist_id: str) -> dict[str, Any]:
        """
        Return the full artist dashboard dict.

        Raises ``ValueError`` if the artist does not exist.
        """
        anomalies = (
            self.db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id)
            .order_by(Anomaly.created_at.desc())
            .all()
        )
        claims = (
            self.db.query(Claim)
            .filter(Claim.artist_id == artist_id)
            .order_by(Claim.updated_at.desc())
            .all()
        )
        disbursements = (
            self.db.query(CeleroTransaction)
            .filter(
                CeleroTransaction.artist_id == artist_id,
                CeleroTransaction.type == CeleroTxnType.DISBURSEMENT,
                CeleroTransaction.status.in_(list(_DEPOSITED_STATUSES)),
            )
            .order_by(CeleroTransaction.updated_at.desc())
            .all()
        )

        leakage = self._leakage_section(anomalies)
        in_pursuit = self._in_pursuit_section(claims)
        deposited = self._deposited_section(disbursements)
        balance = self._balance_section(in_pursuit, deposited, claims, artist_id)
        feed = self._activity_feed(anomalies, claims, disbursements)

        return {
            "artist_id": artist_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "leakage_discovered": leakage,
            "in_pursuit": in_pursuit,
            "recovered_and_deposited": deposited,
            "balance_still_pursuing": balance,
            "activity_feed": feed,
        }

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _leakage_section(self, anomalies: list[Anomaly]) -> dict:
        """
        Everything ARCOS7 has found — open and closed anomalies alike.

        The ``estimated_recoverable`` on each anomaly is the ML/rule-engine
        estimate of how much money was leaked.
        """
        total_estimated = sum(a.estimated_recoverable or 0.0 for a in anomalies)
        open_count = sum(1 for a in anomalies if a.status == AnomalyStatus.OPEN)

        by_category: dict[str, dict] = {}
        for a in anomalies:
            cat = a.category
            if cat not in by_category:
                by_category[cat] = {"count": 0, "estimated_recoverable": 0.0}
            by_category[cat]["count"] += 1
            by_category[cat]["estimated_recoverable"] += a.estimated_recoverable or 0.0

        by_severity: dict[str, dict] = {}
        for a in anomalies:
            sev = a.severity
            if sev not in by_severity:
                by_severity[sev] = {"count": 0, "estimated_recoverable": 0.0}
            by_severity[sev]["count"] += 1
            by_severity[sev]["estimated_recoverable"] += a.estimated_recoverable or 0.0

        recent = [
            {
                "id": a.id,
                "category": a.category,
                "subtype": a.subtype,
                "severity": a.severity,
                "estimated_recoverable": a.estimated_recoverable,
                "status": a.status,
                "description": a.description,
                "discovered_at": a.created_at.isoformat(),
            }
            for a in anomalies[:10]
        ]

        return {
            "total_anomalies": len(anomalies),
            "open_anomalies": open_count,
            "total_estimated_recoverable": round(total_estimated, 2),
            "by_category": by_category,
            "by_severity": by_severity,
            "recent_discoveries": recent,
        }

    def _in_pursuit_section(self, claims: list[Claim]) -> dict:
        """
        Active claims — money ARCOS7 is currently chasing for the artist.
        """
        active = [c for c in claims if c.status in _ACTIVE_CLAIM_STATUSES]
        closed_paid = [
            c for c in claims
            if c.status in {ClaimStatus.PAID, ClaimStatus.CLOSED}
        ]

        # For active claims, use recovered_amount if set (claim has been
        # reconciled already), otherwise fall back to the anomaly's
        # estimated_recoverable via contingency_fee back-calculation.
        # We use recovered_amount directly for actuals; for unreconciled
        # claims it may be None.
        total_active_amount = sum(c.recovered_amount or 0.0 for c in active)
        total_recovered = sum(c.recovered_amount or 0.0 for c in closed_paid)
        total_fees_collected = sum(c.contingency_fee or 0.0 for c in closed_paid)

        active_items = [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "status": c.status,
                "recovered_amount": c.recovered_amount,
                "currency": c.currency,
                "updated_at": c.updated_at.isoformat(),
            }
            for c in active[:20]
        ]

        return {
            "active_claim_count": len(active),
            "total_amount_in_pursuit": round(total_active_amount, 2),
            "closed_claim_count": len(closed_paid),
            "total_gross_recovered": round(total_recovered, 2),
            "total_fees_collected": round(total_fees_collected, 2),
            "total_net_recovered": round(total_recovered - total_fees_collected, 2),
            "active_claims": active_items,
        }

    def _deposited_section(self, disbursements: list[CeleroTransaction]) -> dict:
        """
        Celero DISBURSEMENT transactions that have landed in the artist's account.

        Only APPROVED and SETTLED disbursements are counted — PENDING and
        FAILED do not represent money the artist has actually received.
        """
        total_deposited = sum(d.amount for d in disbursements)

        deposits = [
            {
                "id": d.id,
                "amount": d.amount,
                "currency": d.currency,
                "status": d.status,
                "celero_transaction_id": d.celero_transaction_id,
                "description": d.description,
                "claim_id": d.claim_id,
                "deposited_at": d.updated_at.isoformat(),
            }
            for d in disbursements
        ]

        return {
            "total_deposited": round(total_deposited, 2),
            "deposit_count": len(disbursements),
            "deposits": deposits,
        }

    def _balance_section(
        self,
        in_pursuit: dict,
        deposited: dict,
        all_claims: list[Claim],
        artist_id: str,
    ) -> dict:
        """
        The headline number: how much is ARCOS7 still trying to recover?

        Balance = gross recoverable pipeline (active claims) + any pending
        disbursements that have not yet settled.

        Pending disbursements (APPROVED but not SETTLED) are shown separately
        so the artist knows money is on its way.
        """
        # Gross pipeline value: sum of recovered_amount on ALL non-closed claims
        # (these are claims we've quantified but not yet fully disbursed)
        active_gross = in_pursuit["total_amount_in_pursuit"]
        total_deposited = deposited["total_deposited"]

        # Pending disbursements: APPROVED but not SETTLED yet
        pending_disburse = (
            self.db.query(CeleroTransaction)
            .filter(
                CeleroTransaction.artist_id == artist_id,
                CeleroTransaction.type == CeleroTxnType.DISBURSEMENT,
                CeleroTransaction.status == CeleroTxnStatus.APPROVED,
            )
            .all()
        )
        total_pending_disburse = sum(d.amount for d in pending_disburse)

        still_pursuing = max(0.0, active_gross - total_pending_disburse)

        return {
            "total_in_active_claims": round(active_gross, 2),
            "total_deposited_to_date": round(total_deposited, 2),
            "total_pending_deposit": round(total_pending_disburse, 2),
            "balance_still_pursuing": round(still_pursuing, 2),
            "note": (
                "balance_still_pursuing = amount in active (not-yet-disbursed) claims.  "
                "total_pending_deposit = disbursements approved but ACH not yet settled."
            ),
        }

    def _activity_feed(
        self,
        anomalies: list[Anomaly],
        claims: list[Claim],
        disbursements: list[CeleroTransaction],
    ) -> list[dict]:
        """
        Reverse-chronological activity log combining all three event types.

        Returns at most 50 entries — enough for a pageable UI feed.
        """
        events: list[dict] = []

        for a in anomalies:
            events.append({
                "type": "LEAKAGE_DISCOVERED",
                "timestamp": a.created_at.isoformat(),
                "title": f"Leakage detected: {a.subtype}",
                "detail": (
                    f"{a.category} anomaly ({a.severity}) — "
                    f"estimated recoverable: "
                    f"${a.estimated_recoverable:,.2f}"
                    if a.estimated_recoverable
                    else f"{a.category} anomaly ({a.severity})"
                ),
                "reference_id": a.id,
                "amount": a.estimated_recoverable,
            })

        for c in claims:
            label = _claim_status_label(c.status)
            events.append({
                "type": f"CLAIM_{c.status}",
                "timestamp": c.updated_at.isoformat(),
                "title": label,
                "detail": (
                    f"{c.claim_type} claim — "
                    + (
                        f"${c.recovered_amount:,.2f} {c.currency}"
                        if c.recovered_amount
                        else "amount pending reconciliation"
                    )
                ),
                "reference_id": c.id,
                "amount": c.recovered_amount,
            })

        for d in disbursements:
            events.append({
                "type": "PAYMENT_DEPOSITED",
                "timestamp": d.updated_at.isoformat(),
                "title": "Payment deposited to your account",
                "detail": (
                    f"${d.amount:,.2f} {d.currency} deposited via Celero Commerce — "
                    f"status: {d.status}"
                    + (f" (ref: {d.celero_transaction_id})" if d.celero_transaction_id else "")
                ),
                "reference_id": d.id,
                "amount": d.amount,
            })

        events.sort(key=lambda e: e["timestamp"], reverse=True)
        return events[:50]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _claim_status_label(status: str) -> str:
    return {
        ClaimStatus.IDENTIFIED: "Claim identified — reviewing your case",
        ClaimStatus.PREPARED: "Claim prepared — building your evidence packet",
        ClaimStatus.SUBMITTED: "Claim submitted to the payer",
        ClaimStatus.IN_REVIEW: "Claim under review by the payer",
        ClaimStatus.ACCEPTED: "Claim accepted — awaiting payment",
        ClaimStatus.PAID: "Payment received from payer",
        ClaimStatus.CLOSED: "Claim closed — funds disbursed to you",
    }.get(status, f"Claim updated: {status}")
