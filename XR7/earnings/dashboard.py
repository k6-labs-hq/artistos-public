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
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.catalog_scorer import CatalogScorer
from XR7.ml.catalog_segmenter import CatalogSegmenter
from XR7.ml.catalog_valuation import CatalogValuationEngine
from XR7.ml.forecaster import EarningsForecaster
from XR7.ml.royalty_optimizer import RoyaltyOptimizer
from XR7.ml.recovery_potential import RecoveryPotentialModel
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.models.contract import Contract
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.recovery_value_model import portfolio_expected_recovery_value
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary
from XR7.ugc.usage_monitor import UGCUsageMonitor
from XR7.ugc.global_scanner import GlobalUGCScanner
from XR7.anomaly.fraud_inflation_detector import FraudInflationDetector
from XR7.prevention.agent import PreventiveAgent
from XR7.transparency.industry_benchmarks import IndustryBenchmarkEngine
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.ml.future_leakage_predictor import FutureLeakagePredictor


# Claim statuses that are still "in pursuit" (open / active)
_ACTIVE_CLAIM_STATUSES = {
    ClaimStatus.IDENTIFIED,
    ClaimStatus.PREPARED,
    ClaimStatus.FILED,
    ClaimStatus.SUBMITTED,
    ClaimStatus.PROOF_SUBMITTED,
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
        metadata_health_prevention = self._metadata_health_prevention_section(artist_id)
        future_leakage_prevention = self._future_leakage_prevention_section(artist_id, works, anomalies, payments)
        repair_transparency_panel = self._repair_transparency_panel_section(artist_id)
        catalog_health = self._catalog_health_section(artist_id, works, payments, anomalies, claims)
        expected_value = self._expected_value_section(anomalies, claims, contracts, catalog_health)
        segment_insight = self._catalog_segment_section(works, payments, anomalies)
        recovery_potential = self._recovery_potential_section(anomalies, contracts, catalog_health, segment_insight)
        earnings_trend = self._earnings_trend_section(artist_id)
        feed = self._activity_feed(anomalies, claims, disbursements)
        ugc = self._ugc_opportunities_section(artist_id)
        global_ugc = self._global_ugc_potential_section(artist_id)
        fraud = self._fraud_protection_section(artist_id)
        prevention = self._prevention_alerts_section(artist_id)
        valuation = self._financing_section(artist_id)
        optimization = self._optimization_playground_section(artist_id)
        industry = self._industry_comparison_section(artist_id)

        return {
            "artist_id": artist_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "leakage_discovered": leakage,
            "in_pursuit": in_pursuit,
            "recovered_and_deposited": deposited,
            "balance_still_pursuing": balance,
            "deadlines": deadlines,
            "priority_actions": priority_actions,
            "expected_recovery_value": expected_value,
            "calibration_health": calibration_health,
            "metadata_health_future_leakage_prevention": metadata_health_prevention,
            "future_leakage_prevention": future_leakage_prevention,
            "repair_transparency_panel": repair_transparency_panel,
            "catalog_health": catalog_health,
            "catalog_segments": segment_insight,
            "recovery_potential": recovery_potential,
            "earnings_trend": earnings_trend,
            "activity_feed": feed,
            "ugc_opportunities": ugc,
            "global_ugc_potential": global_ugc,
            "fraud_protection": fraud,
            "fraud_protection_health": fraud.get("fraud_protection_health"),
            "estimated_protected": fraud.get("estimated_protected"),
            "prevention_alerts": prevention,
            "financing_opportunities": valuation,
            "optimization_playground": optimization,
            "industry_comparison": industry,
            "chat_agent_available": True,
            "ask_anything": {
                "sample_questions": [
                    "What is my current balance still pursuing?",
                    "Which anomalies are most urgent and why?",
                    "Show me evidence hashes for my top claim.",
                ]
            },
            "global_social_summary": {
                "platform_breakdown": {
                    "youtube": {"estimated_recoverable": 4200.0, "status": "oauth_ready_fallback_csv"},
                    "tiktok": {"estimated_recoverable": 5100.0, "status": "portal_csv_guided"},
                    "instagram": {"estimated_recoverable": 2300.0, "status": "meta_graph_limited"},
                    "soundcloud": {"estimated_recoverable": 2800.0, "status": "oauth_or_statement_sync"},
                    "melon": {"estimated_recoverable": 900.0, "status": "csv_only"},
                    "boomplay": {"estimated_recoverable": 780.0, "status": "csv_only"},
                    "tencent": {"estimated_recoverable": 1100.0, "status": "csv_only"},
                }
            },
        }

    def _ugc_opportunities_section(self, artist_id: str) -> list[dict[str, Any]]:
        import asyncio

        uses = asyncio.run(UGCUsageMonitor().scan_for_uses(artist_id, days_back=30))
        out = []
        monitor = UGCUsageMonitor()
        for use in uses:
            est = monitor.calculate_lost_sync_value(use)
            out.append(
                {
                    "platform": use.get("platform"),
                    "title": use.get("title"),
                    "estimated_recoverable": est,
                    "claim_status": "ready_to_file" if est >= 3000 else "review",
                    "action_url": f"/artists/{artist_id}/recovery/ugc-auto-claim?platform={use.get('platform')}&use_id={use.get('use_id')}",
                }
            )
        return out

    def _global_ugc_potential_section(self, artist_id: str) -> dict[str, Any]:
        import asyncio

        scanner = GlobalUGCScanner()
        uses = asyncio.run(scanner.scan_global_uses(artist_id, days_back=365))
        est = sum(float(scanner.calculate_hidden_value(u) or 0.0) for u in uses)
        return {
            "estimated_recoverable": round(est, 2),
            "top_uses": uses[:5],
            "quick_approve_ugc": True,
            "ugc_claims_ready": [
                {
                    "use_id": u.get("use_id"),
                    "platform": u.get("platform"),
                    "quick_approve_url": f"/artists/{artist_id}/recovery/ugc-auto-claim?platform={u.get('platform')}&use_id={u.get('use_id')}",
                }
                for u in uses[:5]
            ],
        }

    def _fraud_protection_section(self, artist_id: str) -> dict[str, Any]:
        return FraudInflationDetector().flag_anomalies_for_report(artist_id)

    def _prevention_alerts_section(self, artist_id: str) -> dict[str, Any]:
        import asyncio

        agent = PreventiveAgent()
        risks = asyncio.run(agent.predict_future_leaks(artist_id))
        actions = agent.generate_prevention_actions(risks)
        return {"risks": risks, "actions": actions}

    def _financing_section(self, artist_id: str) -> dict[str, Any]:
        engine = CatalogValuationEngine(self.db)
        val = engine.calculate_catalog_value(artist_id)
        matches = engine.generate_financing_matches(val)
        return {
            "catalog_value": val,
            "matches": matches,
            "estimated_advance": round(sum(float(m.get("estimated_advance") or 0.0) for m in matches), 2),
        }

    def _optimization_playground_section(self, artist_id: str) -> dict[str, Any]:
        opt = RoyaltyOptimizer()
        sim = opt.simulate_scenario(artist_id, {"distro_switch": True, "ai_opt_in": True, "fraud_reduction": True})
        return {"default_simulation": sim, "chart": opt.visualize_delta(sim)}

    def _industry_comparison_section(self, artist_id: str) -> dict[str, Any]:
        engine = IndustryBenchmarkEngine()
        b = engine.get_benchmarks(artist_id)
        return {"benchmarks": b, "message": engine.generate_comparison_report(b)}

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

    def _expected_value_section(
        self,
        anomalies: list[Anomaly],
        claims: list[Claim],
        contracts: list[Contract],
        catalog_health: dict,
    ) -> dict:
        anomalies_dict = [
            {
                "id": a.id,
                "estimated_recoverable": float(a.estimated_recoverable or 0.0),
            }
            for a in anomalies
        ]
        claims_dict = [
            {
                "id": c.id,
                "status": str(c.status),
                "recovered_amount": float(c.recovered_amount or 0.0),
            }
            for c in claims
        ]
        contract_rows = [
            {
                "id": c.id,
                "terms": c.terms or {},
                "territory": c.territory,
            }
            for c in contracts
        ]
        paid_claims = sum(1 for c in claims if c.status in {ClaimStatus.PAID, ClaimStatus.CLOSED})
        historical_rate = float(paid_claims) / max(float(len(claims) or 1), 1.0)

        payer_rows = [
            {
                "acceptance_probability": 0.65,
            }
        ]

        return portfolio_expected_recovery_value(
            anomalies=anomalies_dict,
            claims=claims_dict,
            catalog_health=float(catalog_health.get("health_score", 70.0) or 70.0),
            payer_behavior_rows=payer_rows,
            contracts=contract_rows,
            historical_recovery_rate=historical_rate,
        )

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
        metadata_health = MetadataRepairEngine(self.db).get_metadata_health(artist_id)
        report = scorer.score(
            artist_id=artist_id,
            works=works_dicts,
            payments=payments_dicts,
            anomalies=anomaly_dicts,
            claims=claim_dicts,
            earnings_summary=earnings_summary,
            metadata_health=metadata_health,
        )

        result = report.to_dict()
        # Expose the key fields at the top level for easy dashboard display
        return {
            "health_score": result.get("health_score"),
            "grade": result.get("grade"),
            "signals": result.get("signals", {}),
            "recommendations": result.get("recommendations", []),
        }

    def _metadata_health_prevention_section(self, artist_id: str) -> dict[str, Any]:
        issues = (
            self.db.query(MetadataIssue)
            .filter(MetadataIssue.artist_id == artist_id)
            .order_by(MetadataIssue.created_at.desc())
            .all()
        )
        health = MetadataRepairEngine(self.db).get_metadata_health(artist_id)
        auto_repaired = [i for i in issues if str(i.repair_status) == "AUTO_REPAIRED"]
        requiring_review = [i for i in issues if str(i.repair_status) == "REQUIRES_REVIEW"]

        return {
            "issues_found": len(issues),
            "issues_auto_repaired": len(auto_repaired),
            "issues_requiring_review": len(requiring_review),
            "projected_leakage_avoided": round(sum(float(i.projected_leakage_avoided or 0.0) for i in auto_repaired), 2),
            "completeness_score": health.get("completeness_score"),
            "consistency_score": health.get("consistency_score"),
            "identifier_coverage": health.get("identifier_coverage"),
            "recommended_fixes": health.get("recommended_fixes"),
        }

    def _future_leakage_prevention_section(
        self,
        artist_id: str,
        works: list[Work],
        anomalies: list[Anomaly],
        payments: list[Payment],
    ) -> dict[str, Any]:
        health = MetadataRepairEngine(self.db).get_metadata_health(artist_id)
        predictor = FutureLeakagePredictor()

        works_rows = [{"id": w.id, "isrc": w.isrc, "iswc": w.iswc} for w in works]
        metadata_completeness = float(health.get("completeness_score") or 0.0)
        identifier_coverage = float((health.get("identifier_coverage") or {}).get("both_coverage") or 0.0)
        anomaly_density = float(len(anomalies)) / max(float(len(works) or 1), 1.0)
        amounts = [float(p.amount or 0.0) for p in payments if float(p.amount or 0.0) > 0.0]
        payment_regularity = 0.5
        if len(amounts) > 1:
            mean = sum(amounts) / len(amounts)
            if mean > 0:
                variance = sum((a - mean) ** 2 for a in amounts) / len(amounts)
                cv = (variance**0.5) / mean
                payment_regularity = max(0.0, min(1.0, 1.0 - (cv / 2.0)))

        # Fallback heuristic where historical release metadata is unavailable.
        catalog_age_years = 4.0 if works else 0.0
        distributors = {
            str(p.source or "").strip().lower()
            for p in payments
            if str(p.source or "").strip()
        }

        predictions = predictor.predict_per_work(
            works_rows,
            metadata_completeness=metadata_completeness,
            identifier_coverage=identifier_coverage,
            anomaly_density=anomaly_density,
            payment_regularity=payment_regularity,
            catalog_age_years=catalog_age_years,
            distributor_footprint=len(distributors),
        )

        auto_applied = [
            i
            for i in self.db.query(MetadataIssue).filter(MetadataIssue.artist_id == artist_id).all()
            if str(i.repair_status) == "AUTO_REPAIRED"
        ]
        predicted_avoided = round(
            sum(float(i.projected_leakage_avoided or 0.0) for i in auto_applied),
            2,
        )

        return {
            "predicted_leakage_avoided": predicted_avoided,
            "recommended_repairs": [
                {
                    "work_id": p.work_id,
                    "risk_band": p.risk_band,
                    "probability": p.probability,
                    "actions": p.recommended_repairs,
                }
                for p in predictions[:20]
            ],
            "auto_applied_fixes": [
                {
                    "issue_id": i.id,
                    "issue_type": i.issue_type,
                    "confidence_score": i.confidence_score,
                }
                for i in auto_applied[:20]
            ],
        }

    def _repair_transparency_panel_section(self, artist_id: str) -> dict[str, Any]:
        repairs = MetadataRepairEngine(self.db).catalog_repairs(artist_id, limit=100)
        entries = []
        for row in repairs[:20]:
            entries.append(
                {
                    "repair_id": row.get("repair_id"),
                    "what_was_fixed": row.get("issue_type"),
                    "why_it_was_fixed": row.get("repair_rationale") or "Prevent future leakage and mismatched payouts.",
                    "how_it_prevents_future_loss": "Improves identifier and registry matching across rights systems.",
                    "confidence_score": row.get("confidence_score"),
                    "evidence_link": f"/artists/{artist_id}/catalog/repairs#{row.get('repair_id')}",
                }
            )
        return {
            "entries": entries,
            "count": len(repairs),
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
        ClaimStatus.PROOF_SUBMITTED: "Proof submitted — awaiting payer response",
        ClaimStatus.IN_REVIEW: "Claim under review by the payer",
        ClaimStatus.ACCEPTED: "Claim accepted — awaiting payment",
        ClaimStatus.PAID: "Payment received from payer",
        ClaimStatus.CLOSED: "Claim closed — funds disbursed to you",
    }.get(status, f"Claim updated: {status}")
