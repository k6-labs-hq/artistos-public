"""SOL guardian, settlement tracking, and evidence recovery agents."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from XR7.agents.onboarding.core import _finalize, _now, _safe_score
from XR7.agents.state import XR7State
from XR7.models.base import SessionLocal
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.models.statement import Statement
from XR7.recovery.claims_evidence_package_builder import ClaimsEvidencePackageBuilder
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.leakage_benchmark_engine import LeakageBenchmarkEngine
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.society_signal_feed import SocietySignalFeed
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.services.rights_scanner import scan_rights_gaps


def _open_session(state: XR7State) -> tuple[Session, bool]:
    """Return (db, owns_session). Caller must close if owns_session."""
    db = state.get("_db_session")
    if isinstance(db, Session):
        return db, False
    return SessionLocal(), True


async def AutoPayerChaserAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db, owns = _open_session(state)
    try:
        claims = (
            db.query(Claim)
            .filter(Claim.artist_id == artist_id)
            .order_by(Claim.created_at.desc())
            .all()
        )
    finally:
        if owns:
            db.close()

    chase_actions = [
        {
            "claim_id": c.id,
            "status": str(c.status),
            "action": (
                "send_follow_up"
                if str(c.status) not in {"PAID", "CLOSED"}
                else "monitor_only"
            ),
            "priority": (
                "high" if str(c.status) in {"DRAFTED", "SENT", "PREPARED"} else "normal"
            ),
        }
        for c in claims
    ]
    score = 0.9 if chase_actions else 0.84
    return _finalize(
        state,
        agent_name="auto_payer_chaser",
        score=score,
        updates={"payer_chase_actions": chase_actions},
        decision=f"prepared chase actions={len(chase_actions)}",
    )


async def AutoEvidenceBuilderAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db, owns = _open_session(state)
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    finally:
        if owns:
            db.close()

    packet = {
        "artist_id": artist_id,
        "generated_at": _now(),
        "anomaly_count": len(anomalies),
        "statement_count": len(statements),
        "anomalies": [
            {
                "id": a.id,
                "category": str(a.category),
                "subtype": a.subtype,
                "estimated_recoverable": float(a.estimated_recoverable or 0.0),
                "confidence": float(a.confidence_score or 0.0),
            }
            for a in anomalies[:25]
        ],
        "source_files": [
            {"statement_id": s.id, "filename": s.filename, "rows": int(s.row_count or 0)}
            for s in statements[:25]
        ],
    }
    return _finalize(
        state,
        agent_name="auto_evidence_builder",
        score=0.91,
        updates={"recovery_evidence_packet": packet},
        decision="evidence packet prepared",
    )


async def AutoSOLGuardianAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db, owns = _open_session(state)
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    finally:
        if owns:
            db.close()

    urgent: list[dict[str, Any]] = []
    for a in anomalies:
        if not a.time_window_end:
            continue
        try:
            now_dt = (
                datetime.now(a.time_window_end.tzinfo)
                if a.time_window_end.tzinfo
                else datetime.now()
            )
            days_left = int((a.time_window_end - now_dt).days)
        except Exception:  # noqa: BLE001
            continue
        if days_left <= 180:
            urgent.append(
                {
                    "anomaly_id": a.id,
                    "subtype": a.subtype,
                    "days_to_sol": days_left,
                    "urgency": "critical" if days_left <= 90 else "high",
                }
            )

    score = 0.92 if not urgent else 0.83
    return _finalize(
        state,
        agent_name="auto_sol_guardian",
        score=score,
        updates={"sol_guardian_alerts": urgent},
        decision=f"sol alerts={len(urgent)}",
    )


async def AutoSettlementTrackerAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db, owns = _open_session(state)
    try:
        claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    finally:
        if owns:
            db.close()

    by_status: dict[str, int] = {}
    for claim in claims:
        key = str(claim.status)
        by_status[key] = by_status.get(key, 0) + 1

    return _finalize(
        state,
        agent_name="auto_settlement_tracker",
        score=0.9,
        updates={
            "settlement_tracker": {
                "total_claims": len(claims),
                "status_breakdown": by_status,
            }
        },
        decision="settlement tracker updated",
    )


async def RightsRegistrationAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db, owns = _open_session(state)
    try:
        gaps = scan_rights_gaps(db, artist_id)
    finally:
        if owns:
            db.close()

    return _finalize(
        state,
        agent_name="rights_registration",
        score=0.9 if gaps else 0.86,
        updates={
            "rights_registration_plan": {
                "gaps_found": len(gaps),
                "gaps": gaps[:50],
            }
        },
        decision=f"rights gaps={len(gaps)}",
    )


async def BlackBoxExpirationAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    recoverability_results: list[dict[str, Any]] = []
    for anomaly in anomalies:
        payload = build_recoverability_payload(anomaly)
        recoverability_results.append(
            {
                "anomaly_id": anomaly.get("id"),
                "subtype": anomaly.get("subtype"),
                "black_box_expiration": payload.get("black_box_expiration"),
                "claim_draft_allowed": payload.get("claim_draft_allowed"),
            }
        )

    score = 0.92 if recoverability_results else 0.84
    return _finalize(
        state,
        agent_name="black_box_expiration_agent",
        score=score,
        updates={"recoverability_results": recoverability_results},
        decision=f"black-box windows evaluated for anomalies={len(recoverability_results)}",
    )


async def RecoverabilityClassificationAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    existing = {
        str(r.get("anomaly_id")): r
        for r in (state.get("recoverability_results") or [])
        if isinstance(r, dict)
    }
    classified: list[dict[str, Any]] = []
    for anomaly in anomalies:
        anomaly_id = str(anomaly.get("id") or "")
        payload = build_recoverability_payload(anomaly)
        cls = (payload.get("recoverability") or {}).get("recoverability_class")
        merged: dict[str, Any] = {
            "anomaly_id": anomaly.get("id"),
            "subtype": anomaly.get("subtype"),
            "estimated_recoverable": anomaly.get("estimated_recoverable"),
            "recoverability": payload.get("recoverability"),
            "black_box_expiration": payload.get("black_box_expiration"),
            "legal_basis": payload.get("legal_basis"),
            "claim_draft_allowed": payload.get("claim_draft_allowed"),
        }
        if anomaly_id in existing and isinstance(existing[anomaly_id], dict):
            merged = {**existing[anomaly_id], **merged}
        merged["recoverability_class"] = cls
        classified.append(merged)

    score = 0.93 if classified else 0.84
    return _finalize(
        state,
        agent_name="recoverability_classification_agent",
        score=score,
        updates={"recoverability_results": classified},
        decision=f"recoverability classification completed for anomalies={len(classified)}",
    )


async def RecoverabilityExplainerAgent(state: XR7State) -> XR7State:
    results = [r for r in (state.get("recoverability_results") or []) if isinstance(r, dict)]
    totals: dict[str, float] = {}
    for row in results:
        cls = str(
            row.get("recoverability_class")
            or (row.get("recoverability") or {}).get("recoverability_class")
            or "Unclassified"
        )
        amount = float((row.get("estimated_recoverable") or 0.0) or 0.0)
        totals[cls] = round(float(totals.get(cls, 0.0)) + amount, 2)

    recoverable_amount = round(
        sum(v for k, v in totals.items() if k != "Expired (Black-Box Redistributed)"), 2
    )
    expired_amount = round(float(totals.get("Expired (Black-Box Redistributed)") or 0.0), 2)

    explainer = {
        "here_is_what_you_can_still_recover": {
            "amount": recoverable_amount,
            "category": "Recoverable and legally actionable classes",
            "why": "Within claim window or recoverable through contract/copyright damages paths.",
            "what_xr7_will_do_next": "XR7 will draft claims, attach evidence hashes, and prepare negotiation workflows.",
        },
        "here_is_what_expired": {
            "amount": expired_amount,
            "category": "Expired black-box redistributed funds",
            "why_it_expired": "Redistribution windows elapsed based on society/union rules.",
            "which_rule_applied": "ASCAP/BMI/SESAC 2-3 years; MLC 3 years; foreign societies often 6-18 months.",
        },
        "here_is_why": [
            "ASCAP redistributes unmatched royalties after 2-3 years.",
            "MLC redistributes unmatched digital mechanicals after 3 years.",
            "Foreign societies often redistribute after 6-18 months.",
        ],
        "here_is_what_xr7_prevents_going_forward": [
            "Metadata repair",
            "Identifier normalization",
            "Cross-system linking",
            "Future leakage prevention scoring",
            "UGC fingerprinting",
            "Foreign society crosswalks",
        ],
        "by_class_amount": totals,
    }

    score = 0.91 if results else 0.83
    return _finalize(
        state,
        agent_name="recoverability_explainer_agent",
        score=score,
        updates={"recoverability_explainer": explainer},
        decision="recoverability explainer synthesized for trust layer and dashboard",
    )


async def DiscoveryRuleAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    engine = DiscoveryRuleEngine()
    analyses: list[dict[str, Any]] = []
    urgent = 0
    for anomaly in anomalies:
        result = engine.evaluate(anomaly)
        if bool(result.get("urgent_flag")):
            urgent += 1
        analyses.append(
            {
                "anomaly_id": anomaly.get("id"),
                "urgent_flag": bool(result.get("urgent_flag")),
                "days_remaining": result.get("days_remaining"),
                "deadline": result.get("statute_of_limitations_deadline"),
                "discovery_memo": result.get("discovery_memo"),
            }
        )

    score = 0.92 if analyses else 0.82
    return _finalize(
        state,
        agent_name="discovery_rule_agent",
        score=score,
        updates={
            "discovery_rule_results": analyses,
            "sol_guardian_alerts": [a for a in analyses if a.get("urgent_flag")],
        },
        decision=f"discovery rule analysis complete; urgent={urgent}",
    )


async def ContractRecoverabilityAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    rows: list[dict[str, Any]] = []
    low_confidence = 0
    for anomaly in anomalies:
        payload = build_recoverability_payload(
            anomaly, contract_metadata=anomaly.get("contract_metadata") or {}
        )
        contract = payload.get("contract_recoverability") or {}
        if float(contract.get("contract_recoverability_score") or 0.0) < 0.40:
            low_confidence += 1
        rows.append(
            {
                "anomaly_id": anomaly.get("id"),
                "contract_recoverability": contract,
                "recoverability_class": (payload.get("recoverability") or {}).get(
                    "recoverability_class"
                ),
            }
        )

    score = 0.9 if rows else 0.8
    out = _finalize(
        state,
        agent_name="contract_recoverability_agent",
        score=score,
        updates={"contract_recoverability_results": rows},
        decision=f"contract recoverability analyzed; low_confidence={low_confidence}",
    )
    if low_confidence > 0:
        out["next_action"] = "human_review"
    return out


async def LeakageBenchmarkAgent(state: XR7State) -> XR7State:
    engine = LeakageBenchmarkEngine()
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    claims = [c for c in (state.get("claims") or []) if isinstance(c, dict)]
    leaked = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
    recovered = sum(float(c.get("recovered_amount") or 0.0) for c in claims)
    expired = sum(
        float(a.get("estimated_recoverable") or 0.0)
        for a in anomalies
        if str(a.get("recoverability_class") or "") == "Expired (Black-Box Redistributed)"
    )
    profile = {
        "estimated_leaked": leaked,
        "recovered": recovered,
        "expired": expired,
        "total_estimated_earnings": max(leaked * 3.5, 1.0),
    }
    result = engine.compare_against_cohort(profile, [])
    return _finalize(
        state,
        agent_name="leakage_benchmark_agent",
        score=0.9,
        updates={"catalog_health_vs_industry": result},
        decision="leakage benchmark narrative generated",
    )


async def EvidencePackageAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    claims = [c for c in (state.get("claims") or []) if isinstance(c, dict)]
    if not anomalies or not claims:
        return _finalize(
            state,
            agent_name="evidence_package_agent",
            score=0.7,
            updates={"evidence_package_agent": {"status": "no_input"}},
            decision="insufficient claims/anomalies for package build",
        )

    anomaly = anomalies[0]
    claim = claims[0]
    recoverability = build_recoverability_payload(anomaly)
    trust = TrustDefensibilityService().trust_score(
        data_completeness=0.85 if anomaly.get("description") else 0.6,
        model_confidence=float(anomaly.get("confidence_score") or 0.0),
        contract_evidence_quality=0.7 if recoverability.get("contract_recoverability") else 0.45,
        sol_risk=0.25,
    )
    package = ClaimsEvidencePackageBuilder().build(
        claim=claim,
        anomaly=anomaly,
        recoverability_payload=recoverability,
        trust_score=float(trust.get("trust_score") or 0.0),
    )
    return _finalize(
        state,
        agent_name="evidence_package_agent",
        score=0.91,
        updates={"claims_evidence_package": package},
        decision=f"evidence package built rating={package.get('claim_strength_rating')}",
    )


async def SocietySignalAgent(state: XR7State) -> XR7State:
    feed = SocietySignalFeed()
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    from datetime import timezone

    signal = {
        "signal_type": "redistribution_pause",
        "payer_or_society": "MLC",
        "royalty_type": "digital_mechanicals",
        "effective_at": datetime.now(timezone.utc).isoformat(),
        "source": "agent_simulation",
    }
    result = feed.apply_signal(signal, anomalies)
    return _finalize(
        state,
        agent_name="society_signal_agent",
        score=0.88,
        updates={
            "society_signal_updates": result,
            "society_activity_feed": feed.dashboard_feed(),
        },
        decision=f"society signal applied affected={result.get('affected_anomaly_count')}",
    )
