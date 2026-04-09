"""
XR7 Engine 2 — Recovery Credit Score
========================================
Produces a single proprietary score (0–850) estimating how recoverable
the artist's catalog is right now. Used for advance qualification and
displayed to the artist as a progress benchmark.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Score structure
# ---------------------------------------------------------------------------
SCORE_MAX = 850

COMPONENT_WEIGHTS = {
    "catalog_health": {"max": 150, "weight": 0.18},
    "anomaly_recoverability": {"max": 150, "weight": 0.18},
    "sol_safety": {"max": 120, "weight": 0.14},
    "contract_clarity": {"max": 120, "weight": 0.14},
    "payer_reliability": {"max": 110, "weight": 0.13},
    "territory_coverage": {"max": 100, "weight": 0.12},
    "platform_diversification": {"max": 100, "weight": 0.11},
}

TIERS = {
    (750, 850): "EXCEPTIONAL",
    (650, 749): "STRONG",
    (550, 649): "GOOD",
    (450, 549): "FAIR",
    (300, 449): "DEVELOPING",
    (0, 299): "LIMITED",
}


def _tier(score: int) -> str:
    for (lo, hi), label in TIERS.items():
        if lo <= score <= hi:
            return label
    return "LIMITED"


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


from shared.utils.dates import ensure_utc as _ensure_utc
class RecoveryCreditScore:
    def __init__(self, db: Session):
        self.db = db

    def calculate(
        self,
        artist_id: str,
        # Optional inputs from other modules (if available)
        catalog_health_score: float | None = None,
        payer_health_avg: float | None = None,
        territory_coverage_ratio: float | None = None,
        concentration_score: float | None = None,
        prior_score: int | None = None,
    ) -> dict[str, Any]:
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        contracts = self.db.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()

        # -- Component 1: Catalog Health (0–150) ---------------------------------
        cat_health = self._catalog_health_component(works, catalog_health_score)

        # -- Component 2: Anomaly Recoverability (0–150) -------------------------
        anom_recover = self._anomaly_recoverability_component(anomalies)

        # -- Component 3: SOL Safety (0–120) -------------------------------------
        sol_safety = self._sol_safety_component(anomalies)

        # -- Component 4: Contract Clarity (0–120) --------------------------------
        contract_clarity = self._contract_clarity_component(contracts, anomalies)

        # -- Component 5: Payer Reliability (0–110) ------------------------------
        payer_reliability = self._payer_reliability_component(payments, payer_health_avg)

        # -- Component 6: Territory Coverage (0–100) -----------------------------
        territory_cov = self._territory_coverage_component(payments, territory_coverage_ratio)

        # -- Component 7: Platform Diversification (0–100) -----------------------
        platform_div = self._platform_diversification_component(payments, concentration_score)

        # -- Aggregate score -------------------------------------------------------
        raw_total = (
            cat_health["score"]
            + anom_recover["score"]
            + sol_safety["score"]
            + contract_clarity["score"]
            + payer_reliability["score"]
            + territory_cov["score"]
            + platform_div["score"]
        )
        # Scale to 0–850
        max_possible = sum(c["max"] for c in COMPONENT_WEIGHTS.values())
        composite = round((raw_total / max_possible) * SCORE_MAX)
        composite = max(0, min(SCORE_MAX, composite))

        tier = _tier(composite)
        delta = composite - prior_score if prior_score is not None else 0
        trend = "IMPROVING" if delta > 0 else ("DECLINING" if delta < 0 else "STABLE")

        # -- Actions ---------------------------------------------------------------
        actions = _generate_actions(
            cat_health=cat_health,
            anom_recover=anom_recover,
            sol_safety=sol_safety,
            contract_clarity=contract_clarity,
            payer_reliability=payer_reliability,
            territory_cov=territory_cov,
            platform_div=platform_div,
        )

        # -- ArtistComfortAgent narrative -----------------------------------------
        narrative = _generate_narrative(
            score=composite,
            tier=tier,
            delta=delta,
            components={
                "catalog_health": cat_health,
                "anomaly_recoverability": anom_recover,
                "sol_safety": sol_safety,
                "contract_clarity": contract_clarity,
                "payer_reliability": payer_reliability,
                "territory_coverage": territory_cov,
                "platform_diversification": platform_div,
            },
        )

        # -- Chain-of-custody -----------------------------------------------------
        payload_for_hash = {
            "artist_id": artist_id,
            "score": composite,
            "tier": tier,
            "components": {k: v["score"] for k, v in {
                "catalog_health": cat_health,
                "anomaly_recoverability": anom_recover,
                "sol_safety": sol_safety,
                "contract_clarity": contract_clarity,
                "payer_reliability": payer_reliability,
                "territory_coverage": territory_cov,
                "platform_diversification": platform_div,
            }.items()},
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "recovery_credit_score_calculated", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for recovery_credit_score")

        return {
            "artist_id": artist_id,
            "score": composite,
            "tier": tier,
            "score_delta": delta,
            "trend": trend,
            "components": {
                "catalog_health": cat_health,
                "anomaly_recoverability": anom_recover,
                "sol_safety": sol_safety,
                "contract_clarity": contract_clarity,
                "payer_reliability": payer_reliability,
                "territory_coverage": territory_cov,
                "platform_diversification": platform_div,
            },
            "actions": actions,
            "narrative": narrative,
            "chain_of_custody_hash": chain_hash,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    # -----------------------------------------------------------------------
    # Component calculations
    # -----------------------------------------------------------------------

    def _catalog_health_component(self, works: list[Work], override: float | None) -> dict[str, Any]:
        max_score = 150
        if override is not None:
            score = round(override * max_score)
        else:
            if not works:
                score = 60
            else:
                isrc_pct = sum(1 for w in works if w.isrc) / len(works)
                iswc_pct = sum(1 for w in works if w.iswc) / len(works)
                score = round(((isrc_pct + iswc_pct) / 2.0) * max_score)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Catalog Health",
            "explanation": "Based on ISRC/ISWC coverage and metadata completeness.",
            "data_source": "catalog_health_scorer",
        }

    def _anomaly_recoverability_component(self, anomalies: list[Anomaly]) -> dict[str, Any]:
        max_score = 150
        if not anomalies:
            score = 90  # neutral with no data
        else:
            open_anoms = [a for a in anomalies if a.status != AnomalyStatus.CLOSED]
            recoverable_value = sum(float(a.estimated_recoverable or 0.0) for a in open_anoms)
            expired_value = sum(
                float(a.estimated_recoverable or 0.0)
                for a in anomalies
                if a.status == AnomalyStatus.CLOSED and float(a.estimated_recoverable or 0.0) <= 0
            )
            total_value = recoverable_value + expired_value + 1.0
            ratio = recoverable_value / total_value
            score = round(ratio * max_score)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Anomaly Recoverability",
            "explanation": "Ratio of recoverable open anomalies vs. expired, weighted by value.",
            "data_source": "anomaly_pipeline",
        }

    def _sol_safety_component(self, anomalies: list[Anomaly]) -> dict[str, Any]:
        max_score = 120
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        critical_count = 0
        safe_count = 0
        for a in anomalies:
            if a.status == AnomalyStatus.CLOSED:
                continue
            created = _ensure_utc(a.created_at)
            days_old = (now - created).days
            if days_old > 700:  # likely near SOL expiry
                critical_count += 1
            else:
                safe_count += 1
        total = critical_count + safe_count + 1
        safe_ratio = safe_count / total
        score = round(safe_ratio * max_score)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "SOL Safety",
            "explanation": "Proportion of open anomalies safely within statute of limitations windows.",
            "data_source": "sol_tracker",
        }

    def _contract_clarity_component(self, contracts: list[Contract], anomalies: list[Anomaly]) -> dict[str, Any]:
        max_score = 120
        if not contracts:
            score = 40  # no contracts uploaded
        else:
            # Check for BREACH_RISK anomalies
            breach_count = sum(
                1 for a in anomalies
                if "BREACH_RISK" in (a.description or "")
            )
            base = min(1.0, len(contracts) / 3.0) * 100
            penalty = min(base, breach_count * 15)
            score = round((base - penalty) / 100 * max_score)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Contract Clarity",
            "explanation": "Based on contract upload count, audit right status, and drift findings.",
            "data_source": "contract_drift_monitor",
            "prompt": None if contracts else "Upload your distributor contracts to improve this component.",
        }

    def _payer_reliability_component(self, payments: list[Payment], override: float | None) -> dict[str, Any]:
        max_score = 110
        if override is not None:
            score = round(override / 100.0 * max_score)
        else:
            # Derive from payment volume diversity
            sources = {str(getattr(p, "source", "Unknown")) for p in payments}
            score = min(max_score, 50 + len(sources) * 10)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Payer Reliability",
            "explanation": "Average Payer Health Score across your payer ecosystem, weighted by volume.",
            "data_source": "payer_health_scorer",
            "prompt": None if override else "Run Payer Health Score to improve this component.",
        }

    def _territory_coverage_component(self, payments: list[Payment], override: float | None) -> dict[str, Any]:
        max_score = 100
        if override is not None:
            score = round(override * max_score)
        else:
            territories = {str(getattr(p, "territory", "US")) for p in payments}
            score = min(max_score, len(territories) * 12)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Territory Coverage",
            "explanation": "Ratio of territories earning vs. territories registered.",
            "data_source": "royalty_dna_profile",
            "prompt": None if override else "Generate your Royalty DNA Profile to improve this component.",
        }

    def _platform_diversification_component(self, payments: list[Payment], concentration_score: float | None) -> dict[str, Any]:
        max_score = 100
        if concentration_score is not None:
            # Low HHI = high diversification = high score
            score = round((1 - concentration_score) * max_score)
        else:
            sources = {str(getattr(p, "source", "Unknown")) for p in payments}
            score = min(max_score, len(sources) * 15)
        score = max(0, min(max_score, score))
        return {
            "score": score,
            "max": max_score,
            "label": "Platform Diversification",
            "explanation": "Revenue concentration index — well-diversified catalog scores higher.",
            "data_source": "royalty_dna_profile",
            "prompt": None if concentration_score else "Generate your Royalty DNA Profile to improve this component.",
        }


# ---------------------------------------------------------------------------
# Narrative & action generation
# ---------------------------------------------------------------------------

def _generate_actions(
    cat_health: dict,
    anom_recover: dict,
    sol_safety: dict,
    contract_clarity: dict,
    payer_reliability: dict,
    territory_cov: dict,
    platform_div: dict,
) -> list[dict[str, Any]]:
    components = [
        ("catalog_health", cat_health, "Fix metadata gaps and add missing ISRCs/ISWCs.", "+35 points"),
        ("anomaly_recoverability", anom_recover, "Resolve high-value open anomalies before they expire.", "+30 points"),
        ("sol_safety", sol_safety, "Resolve CRITICAL anomalies in the Black Box Countdown.", "+25 points"),
        ("contract_clarity", contract_clarity, "Upload your distributor contracts for audit rights extraction.", "+20 points"),
        ("payer_reliability", payer_reliability, "Run Payer Health Score to identify unreliable payers.", "+15 points"),
        ("territory_coverage", territory_cov, "Register catalog in missing territories (Royalty DNA Profile).", "+15 points"),
        ("platform_diversification", platform_div, "Diversify distribution to reduce single-platform exposure.", "+10 points"),
    ]
    actions = []
    for key, comp, description, impact in sorted(components, key=lambda x: x[1]["score"]):
        if comp["score"] < comp["max"] * 0.75:
            actions.append(
                {
                    "component": key,
                    "action": description,
                    "estimated_impact": impact,
                    "navigate_to": _action_navigation(key),
                }
            )
    return actions[:5]


def _action_navigation(component: str) -> str:
    nav_map = {
        "catalog_health": "/catalog/fixes",
        "anomaly_recoverability": "/anomalies",
        "sol_safety": "/anomalies/countdown?tier=CRITICAL",
        "contract_clarity": "/contracts/upload",
        "payer_reliability": "/payers/health",
        "territory_coverage": "/profile/dna",
        "platform_diversification": "/profile/dna",
    }
    return nav_map.get(component, "/dashboard")


def _generate_narrative(
    score: int,
    tier: str,
    delta: int,
    components: dict[str, dict],
) -> str:
    helping = sorted(
        [(k, v) for k, v in components.items()],
        key=lambda x: x[1]["score"] / x[1]["max"],
        reverse=True,
    )[:3]
    hurting = sorted(
        [(k, v) for k, v in components.items()],
        key=lambda x: x[1]["score"] / x[1]["max"],
    )[:3]

    trend_str = f"up {delta}" if delta > 0 else (f"down {abs(delta)}" if delta < 0 else "unchanged")
    helping_labels = ", ".join(v["label"] for _, v in helping)
    hurting_labels = ", ".join(v["label"] for _, v in hurting)

    return (
        f"Your Recovery Credit Score is {score}/850 ({tier}), {trend_str} since last calculation. "
        f"Your strongest factors are: {helping_labels}. "
        f"The factors most holding your score back are: {hurting_labels}. "
        "Improving your catalog metadata, resolving open anomalies quickly, and uploading contracts "
        "are the highest-impact actions you can take right now."
    )


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def recalculate(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.recovery_score.recalculate"""
    db = SessionLocal()
    try:
        scorer = RecoveryCreditScore(db)
        return scorer.calculate(artist_id)
    finally:
        db.close()
