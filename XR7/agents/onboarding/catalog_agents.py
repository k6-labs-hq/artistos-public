"""Catalog, upload, and portal-navigation agents for onboarding."""

from __future__ import annotations

from typing import Any

from XR7.agents.onboarding.core import _finalize, _now, _safe_score
from XR7.agents.state import XR7State, update_onboarding_progress
from XR7.models.base import SessionLocal
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.services.post_repair_forecast_pipeline import FORECAST_DISCLAIMER


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
        prompt = (
            "Are you trying to upload statements, fix metadata, check earnings, or start recovery?"
        )
    updates: XR7State = {
        "artist_intent": intent,
        "dashboard_prompt": prompt,
    }
    return _finalize(
        state,
        agent_name="artist_intent_interpreter",
        score=score,
        updates=updates,
        decision=f"intent={intent}",
    )


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
                "email_template": (
                    f"Subject: Statement export request for {name}\n\n"
                    "Hello, please share my latest royalty statement export."
                ),
            }
        )
    return _finalize(
        state,
        agent_name="portal_auto_navigator",
        score=0.92,
        updates={"portal_guidance": guidance},
        decision="portal guidance generated",
    )


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
    return _finalize(
        state,
        agent_name="smart_upload_fixer",
        score=score,
        updates=updates,
        decision=f"fixed={len(fixed)}",
    )


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
            "metadata_completeness": _safe_score(
                (sum(1 for w in works if w.isrc) / len(works)) if works else 0.7
            ),
            "metadata_health": metadata_health,
        }
    finally:
        db.close()

    updates: XR7State = {
        "catalog_profile": profile,
        **update_onboarding_progress(state, completed_step="catalog"),
    }
    score = float(profile.get("metadata_completeness") or 0.85)
    return _finalize(
        state,
        agent_name="catalog_auto_builder",
        score=score,
        updates=updates,
        decision="catalog profile constructed",
    )


async def DistributorSyncAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("catalog_profile") or {})
    distros = list(profile.get("distributors") or ["distrokid", "tunecore"])
    status = {}
    for d in distros:
        dn = str(d).lower()
        oauth_supported = dn in {"spotify", "youtube", "distrokid", "tunecore"}
        status[dn] = {
            "oauth_url": (
                f"/artists/{state.get('artist_id')}/connect/oauth-session?provider={dn}"
                if oauth_supported
                else None
            ),
            "sync_status": "ready_oauth" if oauth_supported else "manual_export_required",
            "last_checked": _now(),
        }
    return _finalize(
        state,
        agent_name="distributor_sync",
        score=0.9,
        updates={"distributor_sync_status": status},
        decision="distributor sync status prepared",
    )


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
        "comfort_messages": [
            "You are on track. XR7 is handling the heavy lifting while you stay in control."
        ],
    }
    return _finalize(
        state,
        agent_name="artist_explainer",
        score=0.93,
        updates=updates,
        decision="artist explanation generated",
    )


async def OnboardingWizardAgent(state: XR7State) -> XR7State:
    progress = update_onboarding_progress(state, completed_step="terms")
    updates: XR7State = {
        **progress,
        "explanations": [
            "Welcome to XR7. Start by uploading your statements; XR7 will auto-classify and recover missed revenue."
        ],
    }
    return _finalize(
        state,
        agent_name="onboarding_wizard",
        score=0.95,
        updates=updates,
        decision="onboarding wizard initiated",
    )


async def FileClassifierAgent(state: XR7State) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    db = SessionLocal()
    try:
        rows = db.query(Statement).filter(Statement.artist_id == artist_id).all()
    finally:
        db.close()
    classified = [
        {"statement_id": s.id, "filename": s.filename, "detected_format": s.format_detected}
        for s in rows
    ]
    updates: XR7State = {
        "fixed_files": classified,
        **update_onboarding_progress(state, completed_step="files"),
    }
    return _finalize(
        state,
        agent_name="file_classifier",
        score=0.9,
        updates=updates,
        decision=f"classified files={len(classified)}",
    )


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
    return _finalize(
        state,
        agent_name="missing_statement_hunter",
        score=score,
        updates=updates,
        decision=f"missing statements={len(missing)}",
    )


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
    return _finalize(
        state,
        agent_name="auto_terms_acceptor",
        score=0.97,
        updates=updates,
        decision="terms accepted",
    )


async def InitialScanOrchestratorAgent(state: XR7State) -> XR7State:
    from XR7.models.anomaly import Anomaly

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
    return _finalize(
        state,
        agent_name="initial_scan_orchestrator",
        score=0.9,
        updates=updates,
        decision=f"initial scan anomalies={len(anomalies)}",
    )


async def ArtistPersonaAdapterAgent(state: XR7State) -> XR7State:
    profile = dict(state.get("persona_profile") or {})
    msg = str(profile.get("last_message") or "").lower()
    style = "simple"
    if any(x in msg for x in ["detail", "explain deeply", "full breakdown"]):
        style = "detailed"
    if any(x in msg for x in ["chart", "visual", "graph"]):
        style = "visual"
    updated = {**profile, "style": style, "updated_at": _now()}
    return _finalize(
        state,
        agent_name="artist_persona_adapter",
        score=0.91,
        updates={"persona_profile": updated},
        decision=f"persona style={style}",
    )
