"""
Artist Recovery Dashboard Engine — XR7 Engine 2.

Aggregates every recovery-related data point into a single, artist-facing
summary so they can see at a glance:

1. **Leakage discovered** — every anomaly XR7 has detected, grouped by
   category and severity, with total estimated recoverable value.

2. **In pursuit** — active claims (IDENTIFIED → ACCEPTED) that are currently
   being worked.  Total amount being chased on the artist's behalf.

3. **Recovered & deposited** — Celero DISBURSEMENT transactions that have
   been APPROVED or SETTLED to the artist's bank account.  Running total and
   per-deposit history.

4. **Balance still pursuing** — the difference between the gross recoverable
   pipeline and what has already been deposited.  This is the number artists
   care most about: "how much are you still trying to get for me?"

5. **Deadlines** — statute-of-limitations urgency overview.  Shows which
   anomalies are EXPIRED, URGENT (<90 days), or AT_RISK (90–180 days) so
   artists know what they could permanently lose the right to claim.

6. **Priority actions** — top 10 ranked items from the recovery priority
   queue, combining anomalies and claims by (value × confidence × urgency).
   The artist's actionable "do-this-now" list.

7. **Catalog health** — ML-derived 0–100 composite score (A–F grade) that
   combines metadata completeness, payment regularity, anomaly density,
   recovery rate, and earnings accuracy.

8. **Earnings trend** — 90-day earnings forecast showing whether the artist's
   income is GROWING, FLAT, or DECLINING, with a predicted dollar range.

9. **Activity feed** — a reverse-chronological event log combining anomaly
   discoveries, claim status changes, and payment deposits so the artist can
   see exactly what happened and when.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.celero_transaction import CeleroTransaction, CeleroTxnStatus, CeleroTxnType
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.catalog_scorer import CatalogScorer
from XR7.ml.catalog_segmenter import CatalogSegmenter
from XR7.ml.forecaster import EarningsForecaster
from XR7.ml.recovery_potential import RecoveryPotentialModel
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.models.contract import Contract
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary


# Claim statuses that are still "in pursuit" (open / active)
_ACTIVE_CLAIM_STATUSES = {
    ClaimStatus.IDENTIFIED,
    ClaimStatus.PREPARED,
    ClaimStatus.FILED,
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
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        contracts = self.db.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()

        leakage = self._leakage_section(anomalies)
        in_pursuit = self._in_pursuit_section(claims)
        deposited = self._deposited_section(disbursements)
        balance = self._balance_section(in_pursuit, deposited, claims, artist_id)
        deadlines = self._deadlines_section(anomalies, claims, contracts, payments)
        priority_actions = self._priority_actions_section(anomalies, claims)
        calibration_health = self._calibration_health_section(artist_id)
        catalog_health = self._catalog_health_section(artist_id, works, payments, anomalies, claims)
        segment_insight = self._catalog_segment_section(works, payments, anomalies)
        recovery_potential = self._recovery_potential_section(anomalies, contracts, catalog_health, segment_insight)
        earnings_trend = self._earnings_trend_section(artist_id)
        feed = self._activity_feed(anomalies, claims, disbursements)

        return {
            "artist_id": artist_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "leakage_discovered": leakage,
            "in_pursuit": in_pursuit,
            "recovered_and_deposited": deposited,
            "balance_still_pursuing": balance,
            "deadlines": deadlines,
            "priority_actions": priority_actions,
            "calibration_health": calibration_health,
            "catalog_health": catalog_health,
            "catalog_segments": segment_insight,
            "recovery_potential": recovery_potential,
            "earnings_trend": earnings_trend,
            "activity_feed": feed,
        }

    def _catalog_segment_section(self, works: list[Work], payments: list[Payment], anomalies: list[Anomaly]) -> dict:
        segmenter = CatalogSegmenter()
        return segmenter.segment(
            [{"id": w.id} for w in works],
            [{"amount": p.amount} for p in payments],
            [{"status": a.status, "estimated_recoverable": a.estimated_recoverable} for a in anomalies],
        )

    def _recovery_potential_section(self, anomalies: list[Anomaly], contracts: list[Contract], catalog_health: dict, segment: dict) -> dict:
        model = RecoveryPotentialModel()
        peer_multiplier = 1.15 if segment.get("segment") == "frontline_releases" else 1.0
        return model.score(
            anomalies=[
                {
                    "estimated_recoverable": a.estimated_recoverable,
                    "status": a.status,
                }
                for a in anomalies
            ],
            contracts=[
                {
                    "territory": c.territory,
                    "terms": c.terms,
                }
                for c in contracts
            ],
            catalog_health_score=float(catalog_health.get("health_score", 0.0) or 0.0),
            peer_multiplier=peer_multiplier,
        )

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _leakage_section(self, anomalies: list[Anomaly]) -> dict:
        """
        Everything XR7 has found — open and closed anomalies alike.

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
        Active claims — money XR7 is currently chasing for the artist.
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
        The headline number: how much is XR7 still trying to recover?

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

    def _deadlines_section(
        self,
        anomalies: list[Anomaly],
        claims: list[Claim],
        contracts: list[Contract],
        payments: list[Payment],
    ) -> dict:
        """
        Statute-of-limitations urgency overview.

        EXPIRED anomalies have permanently lost their recovery window.
        URGENT (<90 days) and AT_RISK (90–180 days) require immediate action.
        This section surfaces the most time-sensitive items so artists never
        miss a filing deadline and permanently lose their right to recover.
        """
        anomaly_dicts = [
            {
                "id": a.id,
                "category": str(a.category),
                "subtype": a.subtype,
                "severity": str(a.severity),
                "status": str(a.status),
                "estimated_recoverable": a.estimated_recoverable,
                "confidence_score": a.confidence_score,
                "territory": a.territory,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in anomalies
            if a.status != AnomalyStatus.CLOSED
        ]
        summary = sol_summary(anomaly_dicts)

        # Surface the top 5 most urgent items with enough detail to act on
        classified = classify_anomalies(anomaly_dicts)
        urgent_items = [
            {
                "id": item.get("id"),
                "category": item.get("category"),
                "subtype": item.get("subtype"),
                "sol_status": item.get("sol_status"),
                "days_remaining": item.get("days_remaining"),
                "estimated_recoverable": item.get("estimated_recoverable"),
                "territory": item.get("territory"),
            }
            for item in classified
            if item.get("sol_status") in ("EXPIRED", "URGENT", "AT_RISK")
        ]
        urgent_items.sort(key=lambda x: x.get("days_remaining") or 9999)

        deadline_risk = evaluate_deadline_risk(
            anomalies=anomaly_dicts,
            claims=[
                {
                    "id": c.id,
                    "status": str(c.status),
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in claims
            ],
            contracts=[
                {
                    "id": c.id,
                    "contract_type": str(c.contract_type),
                    "territory": c.territory,
                    "terms": c.terms or {},
                }
                for c in contracts
            ],
            payments=[
                {
                    "id": p.id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "source": p.source,
                    "received_at": p.received_at.isoformat() if p.received_at else None,
                }
                for p in payments
            ],
        )

        return {
            "expired_count": summary["counts_by_status"].get("EXPIRED", 0),
            "urgent_count": summary["counts_by_status"].get("URGENT", 0),
            "at_risk_count": summary["counts_by_status"].get("AT_RISK", 0),
            "ok_count": summary["counts_by_status"].get("OK", 0),
            "total_open_anomalies": summary["total_anomalies"],
            "top_urgent_items": urgent_items[:5],
            "deadline_risk": deadline_risk,
            "note": (
                "Act immediately on EXPIRED and URGENT items — missed SOL deadlines "
                "permanently forfeit the right to file a claim."
            ),
        }

    def _priority_actions_section(
        self, anomalies: list[Anomaly], claims: list[Claim]
    ) -> dict:
        """
        Top 10 ranked items from the recovery priority queue.

        Scores each open anomaly and active claim by
        (estimated_recoverable × confidence × SOL_urgency) / age_factor
        and returns the highest-ROI actions.  The artist's "do-this-now" list.
        """
        open_anomaly_dicts = [
            {
                "id": a.id,
                "category": str(a.category),
                "subtype": a.subtype,
                "severity": str(a.severity),
                "status": str(a.status),
                "estimated_recoverable": a.estimated_recoverable,
                "confidence_score": a.confidence_score,
                "territory": a.territory,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in anomalies
            if a.status != AnomalyStatus.CLOSED
        ]
        active_claim_dicts = [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "status": str(c.status),
                "estimated_recoverable": c.recovered_amount,
                # Claims don't carry a native ML confidence score — 0.7 is a
                # conservative prior reflecting that an open claim has already
                # passed initial validation (IDENTIFIED/PREPARED/SUBMITTED).
                "confidence_score": 0.7,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in claims
            if c.status in _ACTIVE_CLAIM_STATUSES
        ]

        # Enrich anomalies with SOL status before ranking
        classified_anomalies = classify_anomalies(open_anomaly_dicts)
        queue = build_action_queue(classified_anomalies, active_claim_dicts)

        top_items = queue[:10]
        total_recoverable = sum(
            item.get("estimated_recoverable") or 0.0 for item in top_items
        )

        return {
            "total_open_items": len(queue),
            "top_10_actions": top_items,
            "top_10_estimated_recoverable": round(total_recoverable, 2),
            "note": (
                "Items ranked by (estimated_value × confidence × SOL_urgency) / age. "
                "Work through this list top-to-bottom for maximum recovery ROI."
            ),
        }

    def _catalog_health_section(
        self,
        artist_id: str,
        works: list[Work],
        payments: list[Payment],
        anomalies: list[Anomaly],
        claims: list[Claim],
    ) -> dict:
        """
        ML-derived catalog health score (0–100) with letter grade (A–F).

        Combines metadata completeness, payment regularity, anomaly density,
        recovery rate, and earnings accuracy into a single composite signal.
        Useful as a dashboard KPI — artists aim to increase this score over
        time as their catalog is cleaned up and claims are resolved.
        """
        works_dicts = [{"id": w.id, "isrc": w.isrc, "iswc": w.iswc} for w in works]
        payments_dicts = [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "received_at": p.received_at.isoformat(),
            }
            for p in payments
        ]
        anomaly_dicts = [{"id": a.id, "status": a.status} for a in anomalies]
        claim_dicts = [
            {"id": c.id, "status": c.status, "recovered_amount": c.recovered_amount}
            for c in claims
        ]

        rg = RightsGraph()
        engine = EarningsEngine(rg)
        earnings_summary = engine.get_earnings_summary(artist_id, self.db)

        scorer = CatalogScorer()
        report = scorer.score(
            artist_id=artist_id,
            works=works_dicts,
            payments=payments_dicts,
            anomalies=anomaly_dicts,
            claims=claim_dicts,
            earnings_summary=earnings_summary,
        )

        result = report.to_dict()
        # Expose the key fields at the top level for easy dashboard display
        return {
            "health_score": result.get("health_score"),
            "grade": result.get("grade"),
            "signals": result.get("signals", {}),
            "recommendations": result.get("recommendations", []),
        }

    def _calibration_health_section(self, artist_id: str) -> dict:
        """
        Model calibration readiness for expected utility ranking.

        Exposes global and subtype-level posterior success rates and whether
        there is enough labeled feedback to trust scoped calibration.
        """
        calibrator = SuccessProbabilityCalibrator()
        summary = calibrator.calibration_summary(artist_id, self.db)
        return {
            "overall": summary.get("overall", {}),
            "by_subtype": summary.get("by_subtype", {}),
            "minimum_scope_samples": summary.get("minimum_scope_samples"),
            "method": summary.get("method"),
        }

    def _earnings_trend_section(self, artist_id: str) -> dict:
        """
        90-day earnings forecast with trend direction and predicted range.

        Uses a linear-regression model over historical earnings to classify
        the trend as GROWING, FLAT, or DECLINING and gives a predicted dollar
        range for the next quarter.

        Returns a compact summary suitable for a dashboard KPI card — artists
        can drill into the full forecast via GET /artists/{id}/ml/forecast.
        """
        from datetime import datetime as _dt, timezone as _tz

        rg = RightsGraph()
        engine = EarningsEngine(rg)
        historical_start = _dt(2000, 1, 1)
        end = _dt.now(_tz.utc)
        historical = engine.reconstruct_historical(artist_id, historical_start, end, self.db)

        if not historical:
            return {
                "trend": "INSUFFICIENT_DATA",
                "horizon_days": 90,
                "predicted_total": None,
                "predicted_low": None,
                "predicted_high": None,
                "note": "Upload royalty statements to enable earnings trend forecasting.",
            }

        forecaster = EarningsForecaster()
        result = forecaster.forecast(historical, horizon_days=90, confidence=0.95)

        return {
            "trend": result.get("trend", "UNKNOWN"),
            "horizon_days": 90,
            "predicted_total": result.get("predicted_total"),
            "predicted_low": result.get("lower_bound"),
            "predicted_high": result.get("upper_bound"),
            "slope_per_day": result.get("slope_per_day"),
            "note": (
                "Forecast uses linear-regression trend model over all historical earnings. "
                "See GET /artists/{id}/ml/forecast for the full breakdown."
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
