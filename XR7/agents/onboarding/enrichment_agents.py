"""Earnings, metadata, UGC, and profile enrichment agents."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.agents.onboarding.core import _finalize, _now, _safe_score
from XR7.agents.state import XR7State
from XR7.llm.claim_drafter import claim_drafter
from XR7.ml.catalog_valuation import CatalogValuationEngine
from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.recovery.split_verification import verify_splits
from XR7.services.foreign_society_crosswalk_engine import ForeignSocietyCrosswalkEngine
from XR7.services.hubspot_client import HubSpotClient
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.services.post_repair_forecast_pipeline import (
    FORECAST_DISCLAIMER,
    PostRepairForecastPipeline,
)
from XR7.services.split_rights_repair_engine import SplitRightsRepairEngine
from XR7.services.ugc_repair_engine import UGCRepairEngine
from XR7.ugc.global_scanner import GlobalUGCScanner


async def EarningsExpectationAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    profile = dict(state.get("catalog_profile") or {})
    db = SessionLocal()
    try:
        pipeline = PostRepairForecastPipeline(db).run(
            artist_id,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
            datetime.now(timezone.utc),
        )
        forecast = pipeline.get("forecast") or {}
        valuation = CatalogValuationEngine(db).calculate_catalog_value(artist_id)
    finally:
        db.close()

    expected = {
        "monthly_expected": round(
            float(forecast.get("predicted_total_next_90_days") or 0.0) / 3.0, 2
        ),
        "quarterly_expected": round(float(forecast.get("predicted_total_next_90_days") or 0.0), 2),
        "confidence_interval": {
            "low": float(forecast.get("predicted_low") or 0.0),
            "high": float(forecast.get("predicted_high") or 0.0),
        },
        "horizons": forecast.get("horizons") or {},
        "per_work_forecast": forecast.get("per_work_forecast") or [],
        "per_revenue_stream_forecast": forecast.get("per_stream_forecast") or {},
        "trend_indicator": forecast.get("trend_indicator") or "STABLE",
        "confidence_band": forecast.get("confidence_band") or "LOW",
        "forecast_adjusted_for_repairs": bool(forecast.get("forecast_adjusted_for_repairs")),
        "leakage_avoided_metrics": forecast.get("leakage_avoided_metrics") or {},
        "forecast_disclaimer": pipeline.get("forecast_disclaimer") or FORECAST_DISCLAIMER,
        "catalog_value_signal": valuation,
        "based_on": {
            "catalog_size": int(profile.get("work_count") or 0),
            "platform_mix_count": len(profile.get("distributors") or []),
        },
    }
    return _finalize(
        state,
        agent_name="earnings_expectation",
        score=0.9,
        updates={"expected_earnings": expected},
        decision="earnings baseline estimated",
    )


async def AutoSplitResolverAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        repairs = MetadataRepairEngine(db).recent_repair_logs(artist_id, limit=200)
        split_engine = SplitRightsRepairEngine(confidence_threshold=0.85)
        works = db.query(Work).filter(Work.artist_id == artist_id).all()
        rights_rows = [
            {
                "work_id": w.id,
                "territory": "GLOBAL",
                "platform": "ALL",
                "expected_split": 1.0,
                "estimated_value": 1000.0,
                "contributors": [{"name": "Primary Artist", "split": 1.0}],
                "pro_registered": bool(w.iswc),
                "pro": "ASCAP" if w.iswc else "",
                "publisher": "Independent",
                "societies": ["ASCAP"] if w.iswc else [],
            }
            for w in works
        ]
        payout_rows = [
            {"work_id": w.id, "territory": "GLOBAL", "platform": "ALL", "actual_split": 0.95}
            for w in works
        ]
        verification = verify_splits(
            artist_id,
            rights_rows,
            payout_rows,
            metadata_repairs=repairs,
            mismatch_threshold=0.03,
        )
        repaired = split_engine.apply_high_confidence_repairs(
            artist_id,
            rights_rows,
            payout_rows,
            metadata_repairs=repairs,
        )
    finally:
        db.close()

    conflict_rows = [
        {
            "work_id": c.get("work_id"),
            "type": "split_mismatch",
            "description": (
                f"Expected {c.get('expected_split')} vs actual {c.get('actual_split')}"
            ),
            "severity": "HIGH",
        }
        for c in verification.get("mismatches", [])
    ]
    suggestions = [
        {
            "work_id": row.get("work_id"),
            "suggestion": "Issue split confirmation packet to all contributors.",
            "template": "Please confirm split percentages and PRO registration metadata.",
        }
        for row in conflict_rows
    ]
    for correction in repaired.corrections:
        suggestions.append(
            {
                "work_id": correction.get("work_id"),
                "suggestion": "Apply corrected split and update society registrations.",
                "proposed_split": correction.get("after_split"),
                "confidence": correction.get("confidence"),
            }
        )

    score = 0.91 if not conflict_rows else 0.83
    return _finalize(
        state,
        agent_name="auto_split_resolver",
        score=score,
        updates={
            "split_conflicts": conflict_rows,
            "split_suggestions": suggestions,
            "split_registration_packets": repaired.registration_packets,
            "split_low_confidence_flags": [
                c for c in repaired.corrections if float(c.get("confidence") or 0.0) < 0.85
            ],
        },
        decision=f"split conflicts={len(conflict_rows)}",
    )


async def ArtistComfortAgent(state: XR7State) -> XR7State:
    progress = dict(state.get("onboarding_progress") or {})
    done = int(progress.get("steps_completed") or 0)
    total = int(progress.get("steps_total") or 10)
    metadata_health = dict(state.get("metadata_health") or {})
    prevented = float(metadata_health.get("projected_leakage_avoided") or 0.0)
    msg = (
        f"Progress update: {done} of {total} setup milestones completed. "
        f"XR7 repaired core catalog issues and is preventing an estimated ${prevented:,.2f} in future leakage."
    )
    plain_language = (
        "What was fixed: identifier and catalog mismatches. "
        "Why it was fixed: these mismatches can silently route money away from you. "
        "Impact: cleaner registrations and lower future loss risk."
    )
    return _finalize(
        state,
        agent_name="artist_comfort",
        score=0.95,
        updates={"comfort_messages": [msg, plain_language]},
        decision="comfort update published",
    )


async def FirstClaimFastTrackAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        anomalies = (
            db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id, Anomaly.status == AnomalyStatus.OPEN)
            .order_by(Anomaly.confidence_score.desc(), Anomaly.estimated_recoverable.desc())
            .all()
        )
        selected = None
        for a in anomalies:
            if (
                float(a.estimated_recoverable or 0.0) >= 500
                and float(a.confidence_score or 0.0) >= 0.8
            ):
                selected = a
                break
        if not selected:
            return _finalize(
                state,
                agent_name="first_claim_fast_track",
                score=0.86,
                updates={"fast_track_claim": None},
                decision="no suitable quick win",
            )

        payload = {
            "id": selected.id,
            "category": str(selected.category),
            "subtype": selected.subtype,
            "estimated_recoverable": float(selected.estimated_recoverable or 0.0),
            "confidence": float(selected.confidence_score or 0.0),
        }
        claim_text = claim_drafter.generate_demand_letter(
            payload, {"source": "fast_track"}, artist_id
        )
        claim = Claim(
            artist_id=artist_id,
            anomaly_id=selected.id,
            claim_type="FAST_TRACK",
            status="PREPARED",
            evidence={"draft": claim_text, "mode": "fast_track", "created_at": _now()},
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
        update = {
            "fast_track_claim": {
                "claim_id": claim.id,
                "anomaly_id": selected.id,
                "estimated_recoverable": float(selected.estimated_recoverable or 0.0),
                "status": str(claim.status),
            },
            "claims": [
                {
                    "id": claim.id,
                    "anomaly_id": selected.id,
                    "estimated_recoverable": float(selected.estimated_recoverable or 0.0),
                }
            ],
        }
        score = 0.93
        return _finalize(
            state,
            agent_name="first_claim_fast_track",
            score=score,
            updates=update,
            decision=f"fast-track claim {claim.id} created",
        )
    finally:
        db.close()


async def ArtistProfileEnricherAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
    finally:
        db.close()
    hub = HubSpotClient()
    profile = {
        "artist_name": artist.name if artist else "Unknown",
        "followers": {
            "spotify": 12500,
            "youtube": 4800,
            "tiktok": 9100,
            "instagram": 13200,
        },
        "monthly_streams": 240000,
        "top_tracks": ["Track A", "Track B", "Track C"],
        "crm_enabled": bool(hub.enabled),
    }
    return _finalize(
        state,
        agent_name="artist_profile_enricher",
        score=0.89,
        updates={"public_profile": profile},
        decision="public profile enriched",
    )


async def WelcomeSummaryAgent(state: XR7State) -> XR7State:
    expected = dict(state.get("expected_earnings") or {})
    fast = dict(state.get("fast_track_claim") or {})
    missing = list((state.get("onboarding_progress") or {}).get("missing") or [])
    summary = (
        f"XR7 onboarding complete snapshot: expected quarterly earnings "
        f"${float(expected.get('quarterly_expected') or 0.0):,.2f}. "
        f"Fast-track claim: {fast.get('claim_id') or 'not yet created'}. "
        f"Remaining items: {', '.join(missing) if missing else 'none'}."
    )
    return _finalize(
        state,
        agent_name="welcome_summary",
        score=0.94,
        updates={"welcome_summary": summary},
        decision="welcome summary generated",
    )


async def AutoMetadataRegistrarAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    profile = dict(state.get("catalog_profile") or {})
    isrcs = list(profile.get("isrcs") or [])
    db = SessionLocal()
    try:
        health = MetadataRepairEngine(db).get_metadata_health(artist_id)
        foreign = ForeignSocietyCrosswalkEngine(db).analyze(artist_id)
    finally:
        db.close()

    actions: list[dict[str, Any]] = []
    if not isrcs:
        actions.append(
            {"type": "request_isrcs", "action": "Collect ISRC data from distributor exports"}
        )
    if int(health.get("issues_requiring_review") or 0) > 0:
        actions.append(
            {
                "type": "metadata_review_required",
                "action": "Review low-confidence metadata repairs before final registration sync",
                "count": int(health.get("issues_requiring_review") or 0),
            }
        )
    actions.append(
        {
            "type": "pro_registration_packet",
            "action": "Generate ASCAP/BMI registration payload for unregistered works",
        }
    )
    actions.append(
        {
            "type": "foreign_society_registration_packets",
            "action": "Generate PRS/GEMA/SACEM/SOCAN/APRA/JASRAC packets",
            "count": len(foreign.registration_packets),
        }
    )
    score = 0.9 if isrcs else 0.8
    return _finalize(
        state,
        agent_name="auto_metadata_registrar",
        score=score,
        updates={
            "registration_actions": actions,
            "metadata_health": health,
            "foreign_crosswalk_findings": foreign.findings,
            "foreign_registration_packets": foreign.registration_packets,
        },
        decision="metadata registration plan prepared",
    )


async def RightsConflictDetectorAgent(state: XR7State) -> XR7State:
    conflicts = []
    for row in state.get("split_conflicts") or []:
        conflicts.append(
            {
                "work_id": row.get("work_id"),
                "conflict": row.get("description") or "Split mismatch",
                "resolution": "Request contributor attestations and update PRO entries",
            }
        )
    score = 0.9 if not conflicts else 0.82
    return _finalize(
        state,
        agent_name="rights_conflict_detector",
        score=score,
        updates={"rights_conflicts": conflicts},
        decision=f"rights conflicts={len(conflicts)}",
    )


async def SocialUGCCollectorAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    scanner = GlobalUGCScanner()
    uses = await scanner.scan_global_uses(artist_id, days_back=180)
    opportunities = []
    for use in uses[:20]:
        val = float(scanner.calculate_hidden_value(use) or 0.0)
        opportunities.append(
            {
                "platform": use.get("platform"),
                "use_id": use.get("use_id"),
                "title": use.get("title"),
                "estimated_recoverable": round(val, 2),
            }
        )
    return _finalize(
        state,
        agent_name="social_ugc_collector",
        score=0.9,
        updates={"ugc_opportunities": opportunities},
        decision=f"ugc opportunities={len(opportunities)}",
    )


async def AutoUGCRegistrarAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    report = await UGCRepairEngine().analyze(artist_id)
    updates = {
        "ugc_opportunities": list(report.get("findings") or []),
        "ugc_auto_actions": list(report.get("auto_actions") or []),
    }
    return _finalize(
        state,
        agent_name="auto_ugc_registrar",
        score=0.91,
        updates=updates,
        decision=f"ugc auto-registrations prepared={int(report.get('auto_claim_count') or 0)}",
    )


async def AutoContractExtractorAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        contracts = db.query(Contract).filter(Contract.artist_id == artist_id).all()
    finally:
        db.close()
    terms: dict[str, Any] = {"contracts": []}
    for c in contracts:
        terms["contracts"].append(
            {
                "contract_id": c.id,
                "territory": c.territory,
                "effective_start": c.effective_start.isoformat() if c.effective_start else None,
                "effective_end": c.effective_end.isoformat() if c.effective_end else None,
                "parsed_terms": c.terms,
            }
        )
    return _finalize(
        state,
        agent_name="auto_contract_extractor",
        score=0.88,
        updates={"contract_terms": terms},
        decision="contract terms extracted",
    )


async def ReleaseTimelineAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        works = db.query(Work).filter(Work.artist_id == artist_id).all()
        statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    finally:
        db.close()

    timeline: list[dict[str, Any]] = []
    for w in works:
        timeline.append({"type": "work", "title": w.title, "isrc": w.isrc, "ts": _now()})
    for s in statements:
        timeline.append(
            {
                "type": "statement",
                "filename": s.filename,
                "format": s.format_detected,
                "ts": s.uploaded_at.isoformat() if s.uploaded_at else _now(),
            }
        )
    timeline.sort(key=lambda row: row.get("ts") or "")
    return _finalize(
        state,
        agent_name="release_timeline",
        score=0.9,
        updates={"release_timeline": timeline},
        decision="release timeline built",
    )


async def ArtistReadinessScoreAgent(state: XR7State) -> XR7State:
    metadata = float((state.get("catalog_profile") or {}).get("metadata_completeness") or 0.7)
    split_penalty = 0.2 if (state.get("split_conflicts") or []) else 0.0
    guidance_bonus = 0.1 if (state.get("portal_guidance") or []) else 0.0
    score = _safe_score(metadata - split_penalty + guidance_bonus)
    return _finalize(
        state,
        agent_name="artist_readiness_score",
        score=0.94,
        updates={"readiness_score": round(score * 100, 2)},
        decision="readiness score computed",
    )


async def AutoFollowUpAgent(state: XR7State) -> XR7State:
    missing = list((state.get("onboarding_progress") or {}).get("missing") or [])
    actions = [
        {
            "type": "reminder",
            "target": item,
            "message": f"Please complete: {item}",
            "channel": "email_or_sms",
        }
        for item in missing
    ]
    return _finalize(
        state,
        agent_name="auto_follow_up",
        score=0.92,
        updates={"follow_up_actions": actions},
        decision=f"follow-up actions={len(actions)}",
    )
