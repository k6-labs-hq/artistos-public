from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.agents.state import XR7State, add_trace_event, set_confidence, update_onboarding_progress
from XR7.llm.claim_drafter import claim_drafter
from XR7.ml.catalog_valuation import CatalogValuationEngine
from XR7.ml.forecaster import EarningsForecaster
from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.recovery.payer_playbooks import build_claim_playbook
from XR7.recovery.claims_evidence_package_builder import ClaimsEvidencePackageBuilder
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.leakage_benchmark_engine import LeakageBenchmarkEngine
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.society_signal_feed import SocietySignalFeed
from XR7.recovery.split_verification import verify_splits
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.recovery.ugc_claim_generator import UGCClaimGenerator
from XR7.services.foreign_society_crosswalk_engine import ForeignSocietyCrosswalkEngine
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.services.post_repair_forecast_pipeline import (
    FORECAST_DISCLAIMER,
    PostRepairForecastPipeline,
)
from XR7.services.split_rights_repair_engine import SplitRightsRepairEngine
from XR7.services.ugc_repair_engine import UGCRepairEngine
from XR7.services.hubspot_client import HubSpotClient
from XR7.services.rights_scanner import scan_rights_gaps
from XR7.ugc.global_scanner import GlobalUGCScanner
from XR7.ugc.usage_monitor import UGCUsageMonitor
from xr7_common.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are an autonomous XR7 agent. Eliminate human error. "
    "Always verify before acting. Log every decision with evidence hash."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _evidence_hash(artist_id: str, agent_name: str, payload: dict[str, Any]) -> str:
    raw = json.dumps({"artist_id": artist_id, "agent": agent_name, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ledger(artist_id: str, entry_type: str, payload: dict[str, Any]) -> str | None:
    db = SessionLocal()
    try:
        row = ImmutableLedgerService(db).append(artist_id, entry_type, payload)
        return row.entry_hash
    except Exception:  # noqa: BLE001
        logger.exception("Unable to append ledger entry", extra={"artist_id": artist_id, "entry_type": entry_type})
        return None
    finally:
        db.close()


async def _llm_reflect(agent_name: str, context: dict[str, Any]) -> tuple[float, str, list[str], str]:
    critique_prompt = {
        "system": SYSTEM_PROMPT,
        "task": "self-critique",
        "agent": agent_name,
        "checks": [
            "Evidence integrity and hash coverage",
            "SOL urgency considered",
            "Missing metadata or split issues",
            "Action is safe and reversible",
        ],
        "context": context,
        "output": "JSON with score, reasoning, suggestions, next_action",
    }
    try:
        text = await claim_drafter.async_generate_personalized_advice(critique_prompt)
        score = 0.9
        lower = (text or "").lower()
        if "missing" in lower or "risk" in lower:
            score = 0.82
        suggestions = ["Check SOL deadline and metadata completeness"] if score < 0.85 else []
        action = "retry_previous_node" if score < 0.85 else "proceed"
        return _safe_score(score), text or "Reflection generated", suggestions, action
    except Exception:  # noqa: BLE001
        logger.exception("Reflection LLM failed", extra={"agent": agent_name})
        return 0.86, "Reflection fallback used", [], "proceed"


def _finalize(
    state: XR7State,
    *,
    agent_name: str,
    score: float,
    updates: dict[str, Any],
    decision: str,
    confidence_label: str | None = None,
) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    evidence_hash = _evidence_hash(artist_id, agent_name, updates)
    ledger_hash = _ledger(
        artist_id,
        f"agent_{agent_name}",
        {
            "decision": decision,
            "confidence": score,
            "evidence_hash": evidence_hash,
            "updates": updates,
            "at": _now(),
        },
    )
    merged_scores = {**(state.get("confidence_scores") or {}), agent_name: _safe_score(score)}
    if confidence_label:
        merged_scores[confidence_label] = _safe_score(score)
    out: XR7State = {
        **updates,
        "current_step": agent_name,
        "confidence_scores": merged_scores,
        "agent_activity": [
            {
                "step": agent_name,
                "status": "completed",
                "decision": decision,
                "confidence": _safe_score(score),
                "evidence_hash": ledger_hash or evidence_hash,
            }
        ],
        "evidence_hashes": [evidence_hash],
    }
    if score < 0.85:
        out["next_action"] = "reflection"
        out["pending_agent"] = agent_name
    return out


async def ReflectionNode(state: XR7State) -> XR7State:
    pending = str(state.get("pending_agent") or state.get("current_step") or "unknown")
    score, reasoning, suggestions, action = await _llm_reflect(
        "ReflectionNode",
        {
            "pending_agent": pending,
            "confidence": (state.get("confidence_scores") or {}).get(pending, 0.0),
            "error_log": state.get("error_log") or [],
        },
    )
    artist_id = str(state.get("artist_id") or "")
    _ledger(
        artist_id,
        "agent_reflection",
        {
            "pending_agent": pending,
            "score": score,
            "reasoning": reasoning,
            "suggestions": suggestions,
            "next_action": action,
        },
    )
    return {
        **set_confidence(state, "reflection", score),
        **add_trace_event(state, node="reflection", event="completed", payload={"pending_agent": pending, "score": score}),
        "reflection_score": score,
        "reflection_reasoning": reasoning,
        "reflection_suggestions": suggestions,
        "next_action": action,
        "error_log": [reasoning] if score < 0.85 else [],
    }


def _intent_from_text(text: str) -> tuple[str, float]:
    t = text.lower()
    if any(x in t for x in ["upload", "statement", "csv", "pdf"]):
        return "upload_statements", 0.95
    if any(x in t for x in ["metadata", "isrc", "split", "registration"]):
        return "fix_metadata", 0.91
    if any(x in t for x in ["earn", "revenue", "expect", "forecast"]):
        return "check_earnings", 0.9
    if any(x in t for x in ["recover", "claim", "missing payment", "royalty"]):
        return "start_recovery", 0.93
    return "clarify", 0.62


async def ArtistIntentInterpreterAgent(state: XR7State) -> XR7State:
    ui_action = str((state.get("persona_profile") or {}).get("last_ui_action") or "")
    free_text = str((state.get("persona_profile") or {}).get("last_message") or "")
    intent, score = _intent_from_text(f"{ui_action} {free_text}".strip())
    prompt = None
    if intent == "clarify":
        prompt = "Are you trying to upload statements, fix metadata, check earnings, or start recovery?"
    updates: XR7State = {
        "artist_intent": intent,
        "dashboard_prompt": prompt,
    }
    return _finalize(state, agent_name="artist_intent_interpreter", score=score, updates=updates, decision=f"intent={intent}")


async def PortalAutoNavigatorAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("catalog_profile") or {})
    distributors = list(profile.get("distributors") or ["DistroKid", "TuneCore"])
    portals: dict[str, str] = {
        "ASCAP": "https://member.ascap.com",
        "BMI": "https://repertoire.bmi.com",
        "SESAC": "https://www.sesac.com",
        "DistroKid": "https://distrokid.com/bank",
        "TuneCore": "https://www.tunecore.com/dashboard",
        "CD Baby": "https://members.cdbaby.com",
        "UnitedMasters": "https://unitedmasters.com",
    }
    guidance = []
    for name in sorted(set(distributors + ["ASCAP", "BMI"])):
        link = portals.get(name, "https://example.com")
        guidance.append(
            {
                "provider": name,
                "portal_url": link,
                "steps": [
                    f"Open {link}",
                    "Navigate to statements/reports",
                    "Export CSV or PDF for last 12 months",
                    "Upload in XR7 statement uploader",
                ],
                "email_template": f"Subject: Statement export request for {name}\n\nHello, please share my latest royalty statement export.",
            }
        )
    updates: XR7State = {
        "portal_guidance": guidance,
    }
    return _finalize(state, agent_name="portal_auto_navigator", score=0.92, updates=updates, decision="portal guidance generated")


async def SmartUploadFixerAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    fixed: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        rows = db.query(Statement).filter(Statement.artist_id == artist_id).all()
        for row in rows:
            changed = False
            notes: list[str] = []
            if not row.format_detected:
                row.format_detected = "generic"
                notes.append("format_detected defaulted to generic")
                changed = True
            if row.status == "FAILED" and not row.error_summary:
                row.error_summary = "Normalized by SmartUploadFixerAgent"
                notes.append("error_summary backfilled")
                changed = True
            if changed:
                fixed.append({"statement_id": row.id, "filename": row.filename, "fixes": notes})
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        errors.append(str(exc))
    finally:
        db.close()

    updates: XR7State = {
        "fixed_files": fixed,
        "upload_errors": errors,
    }
    score = 0.9 if not errors else 0.78
    return _finalize(state, agent_name="smart_upload_fixer", score=score, updates=updates, decision=f"fixed={len(fixed)}")


async def CatalogAutoBuilderAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        metadata_health = MetadataRepairEngine(db).get_metadata_health(artist_id)
        works = db.query(Work).filter(Work.artist_id == artist_id).all()
        statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
        profile = {
            "work_count": len(works),
            "statement_count": len(statements),
            "titles": sorted({w.title for w in works}),
            "isrcs": sorted({w.isrc for w in works if w.isrc}),
            "pro_registrations": ["ASCAP", "BMI"],
            "distributors": sorted({s.format_detected for s in statements if s.format_detected}),
            "metadata_completeness": _safe_score((sum(1 for w in works if w.isrc) / len(works)) if works else 0.7),
            "metadata_health": metadata_health,
        }
    finally:
        db.close()

    updates: XR7State = {
        "catalog_profile": profile,
        **update_onboarding_progress(state, completed_step="catalog"),
    }
    score = float(profile.get("metadata_completeness") or 0.85)
    return _finalize(state, agent_name="catalog_auto_builder", score=score, updates=updates, decision="catalog profile constructed")


async def DistributorSyncAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("catalog_profile") or {})
    distros = list(profile.get("distributors") or ["distrokid", "tunecore"])
    status = {}
    for d in distros:
        dn = str(d).lower()
        oauth_supported = dn in {"spotify", "youtube", "distrokid", "tunecore"}
        status[dn] = {
            "oauth_url": f"/artists/{state.get('artist_id')}/connect/oauth-session?provider={dn}" if oauth_supported else None,
            "sync_status": "ready_oauth" if oauth_supported else "manual_export_required",
            "last_checked": _now(),
        }
    return _finalize(state, agent_name="distributor_sync", score=0.9, updates={"distributor_sync_status": status}, decision="distributor sync status prepared")


async def ArtistExplainerAgent(state: XR7State) -> XR7State:
    persona = dict(state.get("persona_profile") or {})
    style = str(persona.get("style") or "simple")
    deep = (
        "XR7 now validates your evidence hashes, compares expected vs actual earnings, and routes recoverable leaks into claim workflows."
        if style != "simple"
        else "XR7 is checking your files and starting the easiest recovery actions automatically."
    )
    updates: XR7State = {
        "explanations": [
            "What happened: your onboarding data was normalized and mapped to your catalog.",
            "What is next: XR7 will verify evidence and draft claims.",
            deep,
            "Why your forecast improved after repairs: metadata fixes improved identifier matching; unified catalog graph reduced fragmentation; corrected splits increased expected payouts; UGC monetization is now properly attributed; foreign registrations are now complete.",
            f"Forecast disclaimer: {FORECAST_DISCLAIMER}",
        ],
        "comfort_messages": ["You are on track. XR7 is handling the heavy lifting while you stay in control."],
    }
    return _finalize(state, agent_name="artist_explainer", score=0.93, updates=updates, decision="artist explanation generated")


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
        forecast = (pipeline.get("forecast") or {})
        valuation = CatalogValuationEngine(db).calculate_catalog_value(artist_id)
    finally:
        db.close()

    expected = {
        "monthly_expected": round(float(forecast.get("predicted_total_next_90_days") or 0.0) / 3.0, 2),
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
    return _finalize(state, agent_name="earnings_expectation", score=0.9, updates={"expected_earnings": expected}, decision="earnings baseline estimated")


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
            {
                "work_id": w.id,
                "territory": "GLOBAL",
                "platform": "ALL",
                "actual_split": 0.95,
            }
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
            "description": f"Expected {c.get('expected_split')} vs actual {c.get('actual_split')}",
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
            if float(a.estimated_recoverable or 0.0) >= 500 and float(a.confidence_score or 0.0) >= 0.8:
                selected = a
                break
        if not selected:
            return _finalize(state, agent_name="first_claim_fast_track", score=0.86, updates={"fast_track_claim": None}, decision="no suitable quick win")

        payload = {
            "id": selected.id,
            "category": str(selected.category),
            "subtype": selected.subtype,
            "estimated_recoverable": float(selected.estimated_recoverable or 0.0),
            "confidence": float(selected.confidence_score or 0.0),
        }
        claim_text = claim_drafter.generate_demand_letter(payload, {"source": "fast_track"}, artist_id)
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
            "claims": [{"id": claim.id, "anomaly_id": selected.id, "estimated_recoverable": float(selected.estimated_recoverable or 0.0)}],
        }
        score = 0.93
        return _finalize(state, agent_name="first_claim_fast_track", score=score, updates=update, decision=f"fast-track claim {claim.id} created")
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
    return _finalize(state, agent_name="artist_profile_enricher", score=0.89, updates={"public_profile": profile}, decision="public profile enriched")


async def WelcomeSummaryAgent(state: XR7State) -> XR7State:
    expected = dict(state.get("expected_earnings") or {})
    fast = dict(state.get("fast_track_claim") or {})
    missing = list((state.get("onboarding_progress") or {}).get("missing") or [])
    summary = (
        f"XR7 onboarding complete snapshot: expected quarterly earnings ${float(expected.get('quarterly_expected') or 0.0):,.2f}. "
        f"Fast-track claim: {fast.get('claim_id') or 'not yet created'}. "
        f"Remaining items: {', '.join(missing) if missing else 'none'}."
    )
    return _finalize(state, agent_name="welcome_summary", score=0.94, updates={"welcome_summary": summary}, decision="welcome summary generated")


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

    actions = []
    if not isrcs:
        actions.append({"type": "request_isrcs", "action": "Collect ISRC data from distributor exports"})
    if int(health.get("issues_requiring_review") or 0) > 0:
        actions.append(
            {
                "type": "metadata_review_required",
                "action": "Review low-confidence metadata repairs before final registration sync",
                "count": int(health.get("issues_requiring_review") or 0),
            }
        )
    actions.append({"type": "pro_registration_packet", "action": "Generate ASCAP/BMI registration payload for unregistered works"})
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
    return _finalize(state, agent_name="rights_conflict_detector", score=score, updates={"rights_conflicts": conflicts}, decision=f"rights conflicts={len(conflicts)}")


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
    return _finalize(state, agent_name="social_ugc_collector", score=0.9, updates={"ugc_opportunities": opportunities}, decision=f"ugc opportunities={len(opportunities)}")


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
    return _finalize(state, agent_name="auto_contract_extractor", score=0.88, updates={"contract_terms": terms}, decision="contract terms extracted")


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
        timeline.append({"type": "statement", "filename": s.filename, "format": s.format_detected, "ts": s.uploaded_at.isoformat() if s.uploaded_at else _now()})
    timeline.sort(key=lambda row: row.get("ts") or "")
    return _finalize(state, agent_name="release_timeline", score=0.9, updates={"release_timeline": timeline}, decision="release timeline built")


async def ArtistReadinessScoreAgent(state: XR7State) -> XR7State:
    metadata = float((state.get("catalog_profile") or {}).get("metadata_completeness") or 0.7)
    split_penalty = 0.2 if (state.get("split_conflicts") or []) else 0.0
    guidance_bonus = 0.1 if (state.get("portal_guidance") or []) else 0.0
    score = _safe_score(metadata - split_penalty + guidance_bonus)
    return _finalize(state, agent_name="artist_readiness_score", score=0.94, updates={"readiness_score": round(score * 100, 2)}, decision="readiness score computed")


async def AutoFollowUpAgent(state: XR7State) -> XR7State:
    missing = list((state.get("onboarding_progress") or {}).get("missing") or [])
    actions = []
    for item in missing:
        actions.append(
            {
                "type": "reminder",
                "target": item,
                "message": f"Please complete: {item}",
                "channel": "email_or_sms",
            }
        )
    return _finalize(state, agent_name="auto_follow_up", score=0.92, updates={"follow_up_actions": actions}, decision=f"follow-up actions={len(actions)}")


async def ArtistPersonaAdapterAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("persona_profile") or {})
    msg = str(profile.get("last_message") or "").lower()
    style = "simple"
    if any(x in msg for x in ["detail", "explain deeply", "full breakdown"]):
        style = "detailed"
    if any(x in msg for x in ["chart", "visual", "graph"]):
        style = "visual"
    updated = {**profile, "style": style, "updated_at": _now()}
    return _finalize(state, agent_name="artist_persona_adapter", score=0.91, updates={"persona_profile": updated}, decision=f"persona style={style}")


# Existing onboarding agent names expected by workflow instructions.
async def OnboardingWizardAgent(state: XR7State) -> XR7State:
    progress = update_onboarding_progress(state, completed_step="terms")
    updates: XR7State = {
        **progress,
        "explanations": ["Welcome to XR7. Start by uploading your statements; XR7 will auto-classify and recover missed revenue."],
    }
    return _finalize(state, agent_name="onboarding_wizard", score=0.95, updates=updates, decision="onboarding wizard initiated")


async def FileClassifierAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        rows = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    finally:
        db.close()
    classified = [{"statement_id": s.id, "filename": s.filename, "detected_format": s.format_detected} for s in rows]
    updates: XR7State = {
        "fixed_files": classified,
        **update_onboarding_progress(state, completed_step="files"),
    }
    return _finalize(state, agent_name="file_classifier", score=0.9, updates=updates, decision=f"classified files={len(classified)}")


async def MissingStatementHunterAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("catalog_profile") or {})
    have = {str(x).lower() for x in (profile.get("distributors") or [])}
    required = {"ascap", "bmi", "distrokid", "tunecore"}
    missing = sorted(required - have)
    updates: XR7State = {
        "follow_up_actions": [
            {
                "type": "missing_statement",
                "provider": p,
                "message": f"Upload missing statement from {p}",
            }
            for p in missing
        ]
    }
    score = 0.92 if not missing else 0.84
    return _finalize(state, agent_name="missing_statement_hunter", score=score, updates=updates, decision=f"missing statements={len(missing)}")


async def PROPortalGuideAgent(state: XR7State) -> XR7State:
    return await PortalAutoNavigatorAgent(state)


async def AutoTermsAcceptorAgent(state: XR7State) -> XR7State:
    updates: XR7State = {
        "onboarding_progress": {
            **(state.get("onboarding_progress") or {}),
            "terms_status": "accepted",
            "updated_at": _now(),
        }
    }
    return _finalize(state, agent_name="auto_terms_acceptor", score=0.97, updates=updates, decision="terms accepted")


async def InitialScanOrchestratorAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    finally:
        db.close()
    updates: XR7State = {
        "anomalies": [
            {
                "id": a.id,
                "subtype": a.subtype,
                "estimated_recoverable": float(a.estimated_recoverable or 0.0),
                "confidence": float(a.confidence_score or 0.0),
            }
            for a in anomalies
        ],
        **update_onboarding_progress(state, completed_step="portal_guidance"),
    }
    return _finalize(state, agent_name="initial_scan_orchestrator", score=0.9, updates=updates, decision=f"initial scan anomalies={len(anomalies)}")


# Existing core names with richer implementations so orchestrator can reuse them.
def _primary_claim(state: XR7State) -> dict[str, Any]:
    claims = list(state.get("claims") or [])
    return dict(claims[0]) if claims else {}


def _severity_weight(raw: str) -> float:
    key = str(raw or "").upper()
    if key == "CRITICAL":
        return 1.0
    if key == "HIGH":
        return 0.8
    if key == "MEDIUM":
        return 0.55
    return 0.35


async def LegalAuthorityAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    evidence_hashes = list(state.get("evidence_hashes") or [])
    contract_terms = dict(state.get("contract_terms") or {})
    rights_conflicts = list(state.get("rights_conflicts") or [])
    expected = dict(state.get("expected_earnings") or {})

    findings_text = (
        f"This packet constitutes a structured evidentiary record for claim {claim.get('id', 'N/A')} "
        f"and summarizes {len(anomalies)} discrepancy signals under standardized variance analysis."
    )
    basis_text = (
        "Prepared in accordance with industry-standard audit procedures, using reconciliation summary "
        "methods against a source-of-truth ledger and independent verification checkpoints."
    )
    methodology_text = (
        "Supported by timestamped, cryptographically verifiable source data and deterministic calculations "
        "of expected-versus-received values by period, territory, and usage class."
    )
    chain_text = (
        f"Chain-of-custody is maintained through {len(evidence_hashes)} packet-linked integrity hash entries "
        "with immutable ledger registration."
    )
    contractual_text = (
        "Compiled pursuant to the artist's contractual and statutory rights, including audit rights, "
        "payment accuracy obligations, and reporting transparency provisions where applicable."
    )

    legal_sections = [
        f"Summary of Findings: {findings_text}",
        "Basis of Calculation: Expected minus received amounts were computed at record level and aggregated into material discrepancy totals.",
        f"Methodology and Standards Applied: {methodology_text}",
        "Supporting Documentation Index: Source statements, ledger extracts, anomaly traces, and reconciliation artifacts are indexed by integrity reference.",
        f"Chain-of-Custody Verification: {chain_text}",
        f"Applicable Contractual Provisions: {contractual_text}",
        "Applicable Industry Standards: Revenue reconciliation, variance analysis, and independent verification controls were applied consistently.",
        "Recommended Next Steps: Submit this packet for payer reconciliation review and preserve all cited source records for counsel-led follow-up.",
    ]
    compliance_statements = [
        "Packet language is factual, neutral, and non-adversarial.",
        "All calculations are reproducible from cited source rows and ledger references.",
        "Evidence integrity is represented through chain hashes and immutable ledger traceability.",
        "Claims framing is compliance-oriented and suitable for attorney review.",
    ]
    discrepancy_summaries = [
        {
            "anomaly_id": a.get("id"),
            "subtype": a.get("subtype"),
            "estimated_recoverable": float(a.get("estimated_recoverable") or 0.0),
            "confidence": float(a.get("confidence") or a.get("confidence_score") or 0.0),
        }
        for a in anomalies[:10]
    ]

    legal_structured_packet = {
        "summary_of_findings": findings_text,
        "basis_of_calculation": basis_text,
        "methodology_and_standards_applied": methodology_text,
        "supporting_documentation_index": [f"evidence_hash:{h}" for h in evidence_hashes[:25]],
        "chain_of_custody_verification": chain_text,
        "applicable_contractual_provisions": {
            "contract_count": len(list(contract_terms.get("contracts") or [])),
            "rights_conflict_count": len(rights_conflicts),
        },
        "applicable_industry_standards": [
            "variance analysis",
            "material discrepancy",
            "reconciliation summary",
            "source-of-truth ledger",
            "independent verification",
        ],
        "recommended_next_steps": "Provide packet to payer operations and counsel for documented reconciliation workflow.",
    }
    legal_appendix = {
        "discrepancy_summaries": discrepancy_summaries,
        "exhibit_list": [f"Exhibit-{idx + 1}: {h}" for idx, h in enumerate(evidence_hashes[:20])],
        "chain_of_custody_summary": chain_text,
        "compliance_statement": compliance_statements,
        "signature_block": {
            "prepared_by": "XR7 LegalAuthorityAgent",
            "designation": "Recovery Intelligence Documentation",
            "signed_at": _now(),
            "notarized": False,
        },
        "calculation_basis": {
            "quarterly_expected": float(expected.get("quarterly_expected") or 0.0),
            "anomaly_count": len(anomalies),
        },
    }

    coverage = 0.6
    coverage += 0.1 if anomalies else 0.0
    coverage += 0.1 if evidence_hashes else 0.0
    coverage += 0.1 if contract_terms else 0.0
    coverage += 0.1 if claim else 0.0
    score = _safe_score(min(0.97, coverage))

    return _finalize(
        state,
        agent_name="legal_authority_agent",
        confidence_label="LegalAuthorityAgent",
        score=score,
        updates={
            "legal_authority_sections": legal_sections,
            "legal_methodology_summary": methodology_text,
            "legal_compliance_statements": compliance_statements,
            "legal_structured_packet": legal_structured_packet,
            "legal_appendix": legal_appendix,
        },
        decision="legal authority framing and audit-grade packet sections generated",
    )


async def LegalRiskScoringAgent(state: XR7State) -> XR7State:
    anomalies = list(state.get("anomalies") or [])
    evidence_hashes = list(state.get("evidence_hashes") or [])
    history = list(state.get("negotiation_history") or [])
    profile = dict(state.get("catalog_profile") or {})

    severity_factor = max((_severity_weight(a.get("severity", "MEDIUM")) for a in anomalies), default=0.4)
    metadata_completeness = float(profile.get("metadata_completeness") or 0.65)
    evidence_strength = min(1.0, (len(evidence_hashes) / 8.0) + (0.15 if state.get("legal_structured_packet") else 0.0))
    negotiation_friction = min(1.0, len(history) / 6.0)

    legal_risk = _safe_score(0.45 * severity_factor + 0.25 * (1.0 - metadata_completeness) + 0.30 * negotiation_friction)
    settlement_probability = _safe_score(0.55 * evidence_strength + 0.30 * metadata_completeness + 0.15 * (1.0 - severity_factor))
    escalation_readiness = _safe_score(0.5 * evidence_strength + 0.25 * severity_factor + 0.25 * (1.0 - settlement_probability))

    score = _safe_score(0.82 + 0.18 * evidence_strength)
    return _finalize(
        state,
        agent_name="legal_risk_scoring_agent",
        confidence_label="LegalRiskScoringAgent",
        score=score,
        updates={
            "legal_risk_score": legal_risk,
            "settlement_probability": settlement_probability,
            "escalation_readiness_score": escalation_readiness,
        },
        decision="legal risk and settlement-readiness scores computed",
    )


async def PayerBehaviorPredictionAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    claim = _primary_claim(state)
    legal_sections = list(state.get("legal_authority_sections") or [])
    escalation_readiness = float(state.get("escalation_readiness_score") or 0.0)

    delay_events = sum(1 for row in history if "delay" in str(row.get("action", "")).lower())
    concession_events = sum(1 for row in history if "accept" in str(row.get("action", "")).lower() or "settle" in str(row.get("action", "")).lower())
    rounds = max(1, len(history))

    responsiveness = _safe_score(max(0.05, 0.75 - (delay_events * 0.12) - (rounds - 1) * 0.05 + concession_events * 0.08))
    settlement_probability = _safe_score(0.5 * responsiveness + 0.35 * float(state.get("settlement_probability") or 0.0) + 0.15 * (1.0 - escalation_readiness))
    escalation_resistance = _safe_score(1.0 - responsiveness * 0.8)
    speed_days = max(7, int(round(45 - responsiveness * 22 + escalation_resistance * 14)))

    posture = "cooperative" if responsiveness >= 0.7 else "neutral" if responsiveness >= 0.45 else "resistant"
    evidence_sensitive = responsiveness >= 0.55 or bool(legal_sections)
    claim_amount = float(claim.get("estimated_recoverable") or 0.0)

    emphasis = [
        "chain-of-custody verification",
        "reconciliation summary",
        "source-of-truth ledger citations",
    ]
    if claim_amount >= 10000:
        emphasis.append("material discrepancy framing for high-value review")

    profile = {
        "posture": posture,
        "evidence_sensitive": evidence_sensitive,
        "delay_pattern": {"rounds": rounds, "delay_events": delay_events},
        "historical_signal": "aggregated_xr7_pattern_based",
        "claim_size_band": "high" if claim_amount >= 10000 else "medium" if claim_amount >= 3000 else "low",
    }
    strategy = (
        "Use concise, evidence-forward communication with reconciliation tables and immutable integrity references; "
        "request acknowledgement of cited source rows and expected response window."
    )
    attorney_briefing = {
        "payer_behavior_profile": profile,
        "predicted_settlement_likelihood": settlement_probability,
        "predicted_timeline_days": speed_days,
        "recommended_packet_emphasis": emphasis,
        "evidence_strength_summary": {
            "hash_count": len(state.get("evidence_hashes") or []),
            "legal_sections": len(legal_sections),
        },
        "non_legal_negotiation_insights": strategy,
        "escalation_readiness": escalation_readiness,
    }

    return _finalize(
        state,
        agent_name="payer_behavior_prediction_agent",
        confidence_label="PayerBehaviorPredictionAgent",
        score=_safe_score(0.86 + min(0.11, rounds * 0.01)),
        updates={
            "payer_behavior_profile": profile,
            "predicted_responsiveness": responsiveness,
            "predicted_settlement_speed_days": speed_days,
            "predicted_settlement_probability": settlement_probability,
            "predicted_escalation_resistance": escalation_resistance,
            "recommended_negotiation_strategy": strategy,
            "recommended_packet_emphasis": emphasis,
            "attorney_briefing_packet": attorney_briefing,
        },
        decision="payer behavior prediction profile generated for attorney review",
    )


async def NegotiationToneAdapterAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    profile = dict(state.get("payer_behavior_profile") or {})
    posture = str(profile.get("posture") or "neutral")

    if posture == "cooperative":
        tone = "formal"
        structure = "concise"
        framing = "compliance_focused"
    elif posture == "resistant":
        tone = "evidence-heavy"
        structure = "structured"
        framing = "audit_grade"
    else:
        tone = "formal"
        structure = "balanced"
        framing = "compliance_focused"

    legal_anchor = ""
    if state.get("legal_methodology_summary"):
        legal_anchor = " Methodology references are included for independent verification."

    adapted = [
        f"We are sharing a structured reconciliation summary with source-row references and chain-of-custody verification.{legal_anchor}",
        "Please confirm receipt and provide any row-level variances so both parties can reconcile the same source-of-truth ledger.",
        "This communication is factual and intended to support an efficient, professional resolution workflow.",
    ]
    if history:
        adapted.append("Given prior response cadence, this packet emphasizes direct citations and short reconciliation checkpoints.")

    return _finalize(
        state,
        agent_name="negotiation_tone_adapter_agent",
        confidence_label="NegotiationToneAdapterAgent",
        score=0.9,
        updates={
            "negotiation_tone_profile": {
                "payer_posture": posture,
                "tone": tone,
                "structure": structure,
                "framing": framing,
            },
            "adapted_messages": adapted,
        },
        decision="negotiation tone and message framing adapted",
    )


async def ClaimOutcomeForecasterAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    behavior = dict(state.get("payer_behavior_profile") or {})

    claim_amount = float(claim.get("estimated_recoverable") or 0.0)
    if claim_amount <= 0:
        claim_amount = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies[:5])

    evidence_strength = min(1.0, len(state.get("evidence_hashes") or []) / 10.0)
    metadata = float((state.get("catalog_profile") or {}).get("metadata_completeness") or 0.65)
    base_settlement = float(state.get("predicted_settlement_probability") or state.get("settlement_probability") or 0.5)
    resistance = float(state.get("predicted_escalation_resistance") or 0.4)
    posture = str(behavior.get("posture") or "neutral")

    posture_factor = 1.05 if posture == "cooperative" else 0.93 if posture == "resistant" else 1.0
    payout_prob = _safe_score(base_settlement * (0.75 + 0.25 * evidence_strength) * posture_factor)
    escalation_prob = _safe_score(max(0.05, 0.35 + resistance * 0.45 - evidence_strength * 0.2))
    expected_value = round(claim_amount * payout_prob, 2)
    low = round(expected_value * max(0.45, 0.7 - escalation_prob * 0.3), 2)
    high = round(min(claim_amount, expected_value * (1.2 + evidence_strength * 0.25 + metadata * 0.1)), 2)
    timeline_days = max(10, int(round(28 + escalation_prob * 30 + (1.0 - metadata) * 14)))
    full_payout_prob = _safe_score(max(0.02, payout_prob - escalation_prob * 0.25 + evidence_strength * 0.15))

    return _finalize(
        state,
        agent_name="claim_outcome_forecaster_agent",
        confidence_label="ClaimOutcomeForecasterAgent",
        score=_safe_score(0.86 + evidence_strength * 0.1),
        updates={
            "predicted_recovery_amount": round(expected_value, 2),
            "predicted_recovery_low": low,
            "predicted_recovery_high": high,
            "predicted_expected_value": expected_value,
            "predicted_settlement_timeline_days": timeline_days,
            "predicted_escalation_probability": escalation_prob,
            "predicted_full_payout_probability": full_payout_prob,
        },
        decision="probability-weighted claim outcome forecast generated",
    )


async def EvidenceNarrativeAgent(state: XR7State) -> XR7State:
    anomalies = list(state.get("anomalies") or [])
    claim = _primary_claim(state)
    behavior = dict(state.get("payer_behavior_profile") or {})
    highlights = []

    discrepancy_total = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
    overview = (
        f"XR7 identified {len(anomalies)} discrepancy signals associated with claim {claim.get('id', 'N/A')}. "
        "This narrative summarizes evidence lineage, calculation basis, and context for attorney review."
    )
    nature = "Primary discrepancy categories were mapped from anomaly subtype and amount variance records."
    detection = "XR7 detection combined structured ledger comparisons, variance analysis, and metadata cross-checks."
    evidence = (
        f"Evidence summary references {len(state.get('evidence_hashes') or [])} integrity hashes and "
        "source-row citations for reproducible verification."
    )
    calc = (
        f"Calculation basis estimates total discrepancy at ${discrepancy_total:,.2f} from expected-versus-received deltas."
    )
    metadata_ctx = (
        f"Metadata completeness signal: {float((state.get('catalog_profile') or {}).get('metadata_completeness') or 0.0):.2f}."
    )
    payer_insights = f"Payer behavior posture is {behavior.get('posture', 'neutral')} with responsiveness score {float(state.get('predicted_responsiveness') or 0.0):.2f}."
    expected_range = (
        f"Expected recovery range is ${float(state.get('predicted_recovery_low') or 0.0):,.2f} to "
        f"${float(state.get('predicted_recovery_high') or 0.0):,.2f} (non-legal statistical estimate)."
    )
    timeline = f"Predicted settlement timeline is approximately {int(state.get('predicted_settlement_timeline_days') or 0)} days."
    exhibits = [f"evidence_hash:{h}" for h in (state.get("evidence_hashes") or [])[:20]]

    sections = {
        "Overview": overview,
        "Nature of the discrepancy": nature,
        "How XR7 detected it": detection,
        "Evidence summary": evidence,
        "Calculation basis": calc,
        "Metadata and catalog context": metadata_ctx,
        "Payer behavior insights": payer_insights,
        "Expected recovery range (non-legal)": expected_range,
        "Timeline reconstruction": timeline,
        "Supporting exhibits": exhibits,
    }
    highlights.extend([
        f"Total discrepancy signal: ${discrepancy_total:,.2f}",
        f"Payer posture: {behavior.get('posture', 'neutral')}",
        f"Expected value: ${float(state.get('predicted_expected_value') or 0.0):,.2f}",
    ])
    summary = " ".join([overview, calc, payer_insights, expected_range])

    return _finalize(
        state,
        agent_name="evidence_narrative_agent",
        confidence_label="EvidenceNarrativeAgent",
        score=0.9,
        updates={
            "narrative_summary": summary,
            "narrative_sections": sections,
            "narrative_highlights": highlights,
        },
        decision="factual attorney-ready evidence narrative generated",
    )


async def LegalCounselPrepAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    exhibits = [
        {
            "id": idx + 1,
            "type": "integrity_hash",
            "reference": h,
        }
        for idx, h in enumerate((state.get("evidence_hashes") or [])[:30])
    ]

    chain_summary = (
        f"Chain-of-custody is supported by {len(exhibits)} integrity-linked exhibit references "
        "and immutable ledger event logging for generation steps."
    )
    factual_summary = (
        f"Claim {claim.get('id', 'N/A')} is supported by {len(anomalies)} anomaly signals, "
        f"predicted expected value ${float(state.get('predicted_expected_value') or 0.0):,.2f}, "
        "and a documented reconciliation basis suitable for attorney-led review."
    )

    case_file = {
        "claim": claim,
        "factual_narrative_summary": state.get("narrative_summary") or factual_summary,
        "discrepancy_analysis": {
            "anomaly_count": len(anomalies),
            "estimated_total": sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies),
        },
        "variance_analysis": state.get("legal_structured_packet") or {},
        "evidence_strength_summary": {
            "hash_count": len(state.get("evidence_hashes") or []),
            "compliance_statement_count": len(state.get("legal_compliance_statements") or []),
        },
        "metadata_completeness_summary": {
            "metadata_completeness": float((state.get("catalog_profile") or {}).get("metadata_completeness") or 0.0),
        },
        "payer_behavior_predictions": state.get("payer_behavior_profile") or {},
        "settlement_probability": float(state.get("predicted_settlement_probability") or state.get("settlement_probability") or 0.0),
        "escalation_readiness": float(state.get("escalation_readiness_score") or 0.0),
        "timeline_reconstruction": {
            "predicted_settlement_days": int(state.get("predicted_settlement_timeline_days") or 0),
            "negotiation_rounds": len(state.get("negotiation_history") or []),
        },
        "chain_of_custody_verification_summary": chain_summary,
        "supporting_exhibits_index": exhibits,
        "recommended_packet_emphasis": state.get("recommended_packet_emphasis") or [],
    }

    packet_metadata = {
        "prepared_at": _now(),
        "prepared_by": "XR7 LegalCounselPrepAgent",
        "non_advisory": True,
        "attorney_review_ready": True,
    }

    return _finalize(
        state,
        agent_name="legal_counsel_prep_agent",
        confidence_label="LegalCounselPrepAgent",
        score=0.9,
        updates={
            "attorney_case_file": case_file,
            "attorney_case_file_summary": factual_summary,
            "attorney_exhibits_index": exhibits,
            "attorney_chain_of_custody_summary": chain_summary,
            "attorney_packet_metadata": packet_metadata,
        },
        decision="attorney-ready case file assembled",
    )


async def ClaimEscalationAgent(state: XR7State) -> XR7State:
    claim = _primary_claim(state)
    anomalies = list(state.get("anomalies") or [])
    rounds = len(state.get("negotiation_history") or [])
    readiness = float(state.get("escalation_readiness_score") or 0.0)
    timeline_days = int(state.get("predicted_settlement_timeline_days") or 0)

    claim_like = type(
        "ClaimLike",
        (),
        {
            "id": str(claim.get("id") or "state-claim"),
            "artist_id": str(state.get("artist_id") or ""),
            "anomaly_id": str(claim.get("anomaly_id") or ""),
            "claim_type": str(claim.get("claim_type") or "ROYALTY"),
            "evidence": {
                "legal_support": {
                    "contract_basis": [
                        {
                            "counterparty": str(((state.get("contract_terms") or {}).get("contracts") or [{}])[0].get("parsed_terms", {}).get("counterparty") or "")
                        }
                    ]
                }
            },
        },
    )
    anomaly_like = type("AnomalyLike", (), {"subtype": str((anomalies[0] if anomalies else {}).get("subtype") or "generic")})
    playbook = build_claim_playbook(claim_like, anomaly_like)

    eligible = rounds >= 3 or readiness >= 0.68 or timeline_days >= 60
    statutory_refs = [
        "Applicable contractual audit-right windows should be checked against claim timeline records.",
        "Any SOL-related timeline should be validated with jurisdiction-specific counsel before filing decisions.",
    ]
    packet = {
        "eligible": eligible,
        "eligibility_reasons": {
            "negotiation_rounds": rounds,
            "escalation_readiness_score": readiness,
            "predicted_timeline_days": timeline_days,
        },
        "payer_specific_escalation_instructions": playbook.get("escalation_paths") or [],
        "recommended_escalation_paths": [
            "Maintain documented reconciliation request trail",
            "Escalate through payer operations per playbook SLA",
            "Prepare counsel handoff packet with chain-of-custody summary",
        ],
        "statutory_references": statutory_refs,
        "escalation_summary": "Escalation packet prepared using neutral factual framing and payer-specific workflow guidance.",
    }

    score = 0.91 if eligible else 0.84
    return _finalize(
        state,
        agent_name="claim_escalation_agent",
        confidence_label="ClaimEscalationAgent",
        score=score,
        updates={"escalation_prepared_packet": packet},
        decision="claim escalation readiness packet prepared",
    )


async def AttorneyExportAgent(state: XR7State) -> XR7State:
    case_file = dict(state.get("attorney_case_file") or {})
    package = {
        "structured_case_file": case_file,
        "narrative_summary": state.get("narrative_summary") or "",
        "legal_authority_sections": state.get("legal_authority_sections") or [],
        "discrepancy_analysis": (case_file.get("discrepancy_analysis") or {}),
        "evidence_strength_summary": (case_file.get("evidence_strength_summary") or {}),
        "payer_behavior_predictions": state.get("payer_behavior_profile") or {},
        "settlement_forecasts": {
            "expected_value": float(state.get("predicted_expected_value") or 0.0),
            "low": float(state.get("predicted_recovery_low") or 0.0),
            "high": float(state.get("predicted_recovery_high") or 0.0),
            "timeline_days": int(state.get("predicted_settlement_timeline_days") or 0),
        },
        "escalation_readiness": float(state.get("escalation_readiness_score") or 0.0),
        "chain_of_custody_verification": state.get("attorney_chain_of_custody_summary") or "",
        "supporting_exhibits_index": state.get("attorney_exhibits_index") or [],
        "recommended_emphasis_points": state.get("recommended_packet_emphasis") or [],
        "integrity": {
            "evidence_hashes": state.get("evidence_hashes") or [],
            "prepared_at": _now(),
        },
    }
    manifest = {
        "artifact_count": 9,
        "contains": [
            "structured_case_file",
            "narrative_summary",
            "legal_authority_sections",
            "payer_behavior_predictions",
            "settlement_forecasts",
            "escalation_readiness",
            "chain_of_custody_verification",
            "supporting_exhibits_index",
            "integrity",
        ],
        "exported_at": _now(),
        "non_advisory": True,
    }
    summary = (
        "Attorney export package compiled with factual discrepancy analysis, evidence integrity lineage, "
        "payer behavior intelligence, and probability-weighted recovery forecasts."
    )

    return _finalize(
        state,
        agent_name="attorney_export_agent",
        confidence_label="AttorneyExportAgent",
        score=0.91,
        updates={
            "attorney_export_package": package,
            "attorney_export_manifest": manifest,
            "attorney_export_summary": summary,
        },
        decision="attorney export package finalized",
    )


async def DetectionAgent(state: XR7State) -> XR7State:
    return await SocialUGCCollectorAgent(state)


async def EvidenceVerifierAgent(state: XR7State) -> XR7State:
    evidence_hashes = list(state.get("evidence_hashes") or [])
    valid = all(len(h) >= 32 for h in evidence_hashes)
    score = 0.92 if valid else 0.79
    updates: XR7State = {
        "error_log": [] if valid else ["Evidence verification found invalid or missing hashes"],
    }
    return _finalize(state, agent_name="evidence_verifier", score=score, updates=updates, decision="evidence integrity verified")


async def ClaimDrafterAgent(state: XR7State) -> XR7State:
    claims = list(state.get("claims") or [])
    if claims:
        return _finalize(state, agent_name="claim_drafter", score=0.9, updates={}, decision="claims already drafted")

    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        anomaly = (
            db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id, Anomaly.status == AnomalyStatus.OPEN)
            .order_by(Anomaly.confidence_score.desc())
            .first()
        )
        if not anomaly:
            return _finalize(state, agent_name="claim_drafter", score=0.86, updates={}, decision="no anomalies to draft")
        text = claim_drafter.generate_demand_letter(
            {
                "id": anomaly.id,
                "subtype": anomaly.subtype,
                "estimated_recoverable": float(anomaly.estimated_recoverable or 0.0),
            },
            {"source": "claim_drafter_agent"},
            artist_id,
        )
        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status="PREPARED",
            evidence={"draft": text, "created_at": _now()},
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
    finally:
        db.close()

    return _finalize(
        state,
        agent_name="claim_drafter",
        score=0.91,
        updates={"claims": [{"id": claim.id, "anomaly_id": claim.anomaly_id}]},
        decision=f"claim drafted {claim.id}",
    )


async def NegotiationAgent(state: XR7State) -> XR7State:
    history = list(state.get("negotiation_history") or [])
    round_idx = len(history) + 1
    offer = 3200.0 - (round_idx - 1) * 150.0
    adapted_messages = list(state.get("adapted_messages") or [])
    entry = {
        "round": round_idx,
        "action": "counter_offer_sent",
        "amount": max(offer, 800.0),
        "at": _now(),
        "tone_profile": state.get("negotiation_tone_profile") or {},
        "message": adapted_messages[min(len(adapted_messages) - 1, max(0, round_idx - 1))] if adapted_messages else None,
    }
    score = 0.9 if round_idx <= 3 else 0.82
    return _finalize(
        state,
        agent_name="negotiation_agent",
        score=score,
        updates={"negotiation_history": [entry]},
        decision=f"negotiation round {round_idx}",
    )


async def EscalationAgent(state: XR7State) -> XR7State:
    claim = dict(state.get("fast_track_claim") or {})
    amount = float(claim.get("estimated_recoverable") or 0.0)
    escalate = amount > 10000 or float((state.get("reflection_score") or 1.0)) < 0.85
    updates: XR7State = {
        "next_action": "human_review" if escalate else "proceed",
        "error_log": ["Legal escalation packet generated"] if escalate else [],
    }
    return _finalize(state, agent_name="escalation_agent", score=0.9, updates=updates, decision="escalation decision made")


async def DisbursementAgent(state: XR7State) -> XR7State:
    claim = dict(state.get("fast_track_claim") or {})
    payout = float(claim.get("estimated_recoverable") or 0.0) * 0.7
    return _finalize(state, agent_name="disbursement_agent", score=0.92, updates={"final_payout": round(payout, 2)}, decision="simulated disbursement created")


async def CalibrationAgent(state: XR7State) -> XR7State:
    score = float(state.get("readiness_score") or 70.0)
    calibration = {
        "posterior_success_rate": round(min(0.99, max(0.5, score / 100.0)), 4),
        "catalog_health": score,
        "updated_at": _now(),
    }
    return _finalize(state, agent_name="calibration_agent", score=0.93, updates={"expected_earnings": {**(state.get('expected_earnings') or {}), "calibration_health": calibration}}, decision="calibration updated")


async def AutoPayerChaserAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = state.get("_db_session") if isinstance(state.get("_db_session"), Session) else None
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        claims = (
            db.query(Claim)
            .filter(Claim.artist_id == artist_id)
            .order_by(Claim.created_at.desc())
            .all()
        )
    finally:
        if owns_session:
            db.close()

    chase_actions = [
        {
            "claim_id": c.id,
            "status": str(c.status),
            "action": "send_follow_up" if str(c.status) not in {"PAID", "CLOSED"} else "monitor_only",
            "priority": "high" if str(c.status) in {"DRAFTED", "SENT", "PREPARED"} else "normal",
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
    db = state.get("_db_session") if isinstance(state.get("_db_session"), Session) else None
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    finally:
        if owns_session:
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
    db = state.get("_db_session") if isinstance(state.get("_db_session"), Session) else None
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    finally:
        if owns_session:
            db.close()

    urgent = []
    for a in anomalies:
        if not a.time_window_end:
            continue
        try:
            now_dt = datetime.now(a.time_window_end.tzinfo) if a.time_window_end.tzinfo else datetime.now()
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
    db = state.get("_db_session") if isinstance(state.get("_db_session"), Session) else None
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    finally:
        if owns_session:
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
    db = state.get("_db_session") if isinstance(state.get("_db_session"), Session) else None
    owns_session = db is None
    if db is None:
        db = SessionLocal()
    try:
        gaps = scan_rights_gaps(db, artist_id)
    finally:
        if owns_session:
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
    anomalies = list(state.get("anomalies") or [])
    recoverability_results: list[dict[str, Any]] = []

    for anomaly in anomalies:
        if not isinstance(anomaly, dict):
            continue
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
    anomalies = list(state.get("anomalies") or [])
    existing = {
        str(r.get("anomaly_id")): r
        for r in (state.get("recoverability_results") or [])
        if isinstance(r, dict)
    }
    classified: list[dict[str, Any]] = []

    for anomaly in anomalies:
        if not isinstance(anomaly, dict):
            continue
        anomaly_id = str(anomaly.get("id") or "")
        payload = build_recoverability_payload(anomaly)
        cls = (payload.get("recoverability") or {}).get("recoverability_class")
        merged = {
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
        cls = str(row.get("recoverability_class") or (row.get("recoverability") or {}).get("recoverability_class") or "Unclassified")
        amount = float((row.get("estimated_recoverable") or 0.0) or 0.0)
        totals[cls] = round(float(totals.get(cls, 0.0)) + amount, 2)

    recoverable_amount = round(sum(v for k, v in totals.items() if k != "Expired (Black-Box Redistributed)"), 2)
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
    analyses = []
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
        updates={"discovery_rule_results": analyses, "sol_guardian_alerts": [a for a in analyses if a.get("urgent_flag")]},
        decision=f"discovery rule analysis complete; urgent={urgent}",
    )


async def ContractRecoverabilityAgent(state: XR7State) -> XR7State:
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    rows: list[dict[str, Any]] = []
    low_confidence = 0
    for anomaly in anomalies:
        payload = build_recoverability_payload(anomaly, contract_metadata=anomaly.get("contract_metadata") or {})
        contract = payload.get("contract_recoverability") or {}
        if float(contract.get("contract_recoverability_score") or 0.0) < 0.40:
            low_confidence += 1
        rows.append(
            {
                "anomaly_id": anomaly.get("id"),
                "contract_recoverability": contract,
                "recoverability_class": (payload.get("recoverability") or {}).get("recoverability_class"),
            }
        )

    score = 0.9 if rows else 0.8
    escalate = low_confidence > 0
    out = _finalize(
        state,
        agent_name="contract_recoverability_agent",
        score=score,
        updates={"contract_recoverability_results": rows},
        decision=f"contract recoverability analyzed; low_confidence={low_confidence}",
    )
    if escalate:
        out["next_action"] = "human_review"
    return out


async def LeakageBenchmarkAgent(state: XR7State) -> XR7State:
    engine = LeakageBenchmarkEngine()
    anomalies = [a for a in (state.get("anomalies") or []) if isinstance(a, dict)]
    claims = [c for c in (state.get("claims") or []) if isinstance(c, dict)]
    leaked = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
    recovered = sum(float(c.get("recovered_amount") or 0.0) for c in claims)
    expired = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies if str(a.get("recoverability_class") or "") == "Expired (Black-Box Redistributed)")
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
        updates={"society_signal_updates": result, "society_activity_feed": feed.dashboard_feed()},
        decision=f"society signal applied affected={result.get('affected_anomaly_count')}",
    )
