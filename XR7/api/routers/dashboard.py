"""
Artist Recovery Dashboard API endpoint.

``GET /artists/{id}/dashboard``

Returns a single, comprehensive JSON document that gives the artist a
complete picture of their recovery status:

- **leakage_discovered** — every anomaly XR7 has detected and its
  estimated dollar value, broken down by category and severity.

- **in_pursuit** — currently active claims (IDENTIFIED → ACCEPTED),
  the total dollar amount being chased, and closed-claim totals.

- **recovered_and_deposited** — Trolley disbursement transactions that
  have already landed in the artist's bank account, with a per-deposit
  log so they can reconcile against their bank statement.

- **balance_still_pursuing** — the headline number: how much are we
  still trying to recover?  Broken down as active-claim pipeline minus
  pending disbursements.

- **activity_feed** — reverse-chronological event log (up to 50 entries)
  combining anomaly discoveries, claim status changes, and payments
  received so the artist can see exactly what happened and when.
"""

from pathlib import Path
import json
import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from sqlalchemy.orm import Session

from XR7.earnings.dashboard import DashboardEngine
from XR7.api.routers.auth import require_artist_access
from XR7.agents.orchestrator import get_latest_artist_state, get_run_trace, list_handoffs_for_artist
from XR7.llm.claim_drafter import royalty_chat_agent
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.support_message import SupportMessage, SupportMessageRole
from XR7.models.catalog_fix_issue import CatalogFixIssue, CatalogFixStatus
from XR7.transparency.data_flow_visualizer import DataFlowVisualizer
from XR7.transparency.immutable_ledger_viewer import ImmutableLedgerViewer
from XR7.transparency.industry_benchmarks import IndustryBenchmarkEngine
from XR7.services.branding import (
  apply_brand_placeholders,
  branding_metadata,
  get_branding_for_artist,
  get_branding_profile,
  inject_branding_metadata,
)

router = APIRouter(tags=["dashboard"])

_DASHBOARD_UI_PATH = Path(__file__).resolve().parents[2] / "widget" / "recovery_dashboard.html"
_MOBILE_UI_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "ui" / "mobile.html"


def _support_proactive_tip(dashboard: dict) -> str:
  deadlines = dashboard.get("deadlines") or {}
  urgent = int(deadlines.get("urgent_count") or 0)
  if urgent > 0:
    return f"You have {urgent} urgent SOL items. Ask Support to prioritize your next best move."

  payers = dashboard.get("payers_owing") or []
  if isinstance(payers, list) and payers:
    top = sorted(payers, key=lambda r: float((r or {}).get("recoverable_estimate") or 0.0), reverse=True)[0]
    return (
      f"Your top payer is {top.get('payer_name')} at "
      f"${float(top.get('recoverable_estimate') or 0.0):,.2f}."
    )

  return "Ask Support for a quick summary of your highest-value recovery opportunities."


def _catalog_health_card(artist_id: str, db: Session) -> dict:
  """Build the lightweight catalog_health dashboard card (no heavy ML recompute)."""
  from XR7.models.catalog_fix_issue import CatalogFixIssue, CatalogFixStatus, FixPriority

  # Pull existing pending/requested fix issues
  issues = (
    db.query(CatalogFixIssue)
    .filter(
      CatalogFixIssue.artist_id == artist_id,
      CatalogFixIssue.status.in_([
        CatalogFixStatus.PENDING.value,
        CatalogFixStatus.REQUESTED.value,
      ]),
    )
    .order_by(CatalogFixIssue.estimated_recoverable_usd.desc())
    .limit(3)
    .all()
  )

  top_issues_summary = [
    {
      "id": iss.id,
      "category": iss.category,
      "priority": iss.priority,
      "description": iss.description[:120],
      "estimated_recoverable_usd": iss.estimated_recoverable_usd,
      "suggested_action": iss.suggested_action,
      "status": iss.status,
    }
    for iss in issues
  ]

  total_recoverable = sum(float(i.estimated_recoverable_usd) for i in issues)

  return {
    "top_issues_summary": top_issues_summary,
    "total_estimated_recoverable_from_fixes": round(total_recoverable, 2),
    "open_fix_count": len(issues),
    "full_health_url": f"/artists/{artist_id}/catalog/health",
    "fixes_url": f"/artists/{artist_id}/catalog/fixes",
  }


def _predicted_recoverable_card(artist_id: str, db: Session) -> dict:
  """Build the 12-month predicted recoverable card for the dashboard."""
  try:
    from XR7.ml.predictive_recoverable import PredictiveRecoverableModel
    model = PredictiveRecoverableModel()
    result = model.predict(artist_id=artist_id, horizon_months=12, db=db)
    return {
      "horizon_months": 12,
      "low_usd": result["low_usd"],
      "mid_usd": result["mid_usd"],
      "high_usd": result["high_usd"],
      "confidence": result["confidence"],
      "key_drivers": result["key_drivers"][:3],
      "detail_url": f"/artists/{artist_id}/ml/predict-recoverable",
    }
  except Exception:
    return {
      "horizon_months": 12,
      "low_usd": None,
      "mid_usd": None,
      "high_usd": None,
      "confidence": None,
      "key_drivers": [],
      "detail_url": f"/artists/{artist_id}/ml/predict-recoverable",
    }


@router.get("/dashboard/ui")
def get_dashboard_ui(org_id: str | None = Query(default=None), db: Session = Depends(get_db)):
  """Serve the standalone artist recovery dashboard UI page."""
  if org_id:
    brand = get_branding_profile(db, org_id)
    ui_path = _MOBILE_UI_PATH if _MOBILE_UI_PATH.exists() else _DASHBOARD_UI_PATH
    if not ui_path.exists():
      raise HTTPException(status_code=404, detail="Dashboard UI not found")
    raw = ui_path.read_text(encoding="utf-8")
    branded = apply_brand_placeholders(
      raw,
      {
        **brand,
        "dashboard_header_text": brand.get("dashboard_header_text") or "{{BRAND.NAME}} Dashboard",
      },
    )
    return HTMLResponse(content=branded)
  if _MOBILE_UI_PATH.exists():
    return FileResponse(str(_MOBILE_UI_PATH), media_type="text/html")
  if not _DASHBOARD_UI_PATH.exists():
    raise HTTPException(status_code=404, detail="Dashboard UI not found")
  return FileResponse(str(_DASHBOARD_UI_PATH), media_type="text/html")


@router.get("/artists/{artist_id}/dashboard")
def get_artist_dashboard(artist_id: str, db: Session = Depends(get_db)):
    """
    Return the artist's full recovery dashboard.

    **leakage_discovered**
    - ``total_anomalies`` — total number of anomalies detected
    - ``total_estimated_recoverable`` — sum of estimated recoverable amounts
    - ``by_category`` — breakdown by revenue category (ROYALTY, TOURING, etc.)
    - ``by_severity`` — breakdown by severity (LOW / MEDIUM / HIGH / CRITICAL)
    - ``recent_discoveries`` — last 10 newly detected anomalies

    **in_pursuit**
    - ``active_claim_count`` — number of open claims
    - ``total_amount_in_pursuit`` — total dollar value of active claims
    - ``total_gross_recovered`` — total recovered across all closed/paid claims
    - ``total_net_recovered`` — gross minus XR7 contingency fees

    **recovered_and_deposited**
    - ``total_deposited`` — sum of all Trolley disbursements received
    - ``deposits`` — per-deposit log with Trolley payment IDs

    **balance_still_pursuing**
    - ``balance_still_pursuing`` — the key number: money we are still chasing
    - ``total_pending_deposit`` — approved but not yet ACH-settled

    **deadlines**
    - ``expired_count`` — anomalies whose SOL window has already closed
    - ``urgent_count`` — anomalies with <90 days remaining on their SOL window
    - ``at_risk_count`` — anomalies with 90–180 days remaining
    - ``top_urgent_items`` — up to 5 most time-sensitive anomalies with days_remaining

    **priority_actions**
    - ``top_10_actions`` — ranked action items (anomalies + claims) by ROI × urgency
    - ``total_open_items`` — total items in the priority queue

    **catalog_health**
    - ``health_score`` — ML composite score 0–100
    - ``grade`` — letter grade A–F
    - ``signals`` — per-signal breakdown (metadata, payment regularity, etc.)
    - ``recommendations`` — list of actionable improvement suggestions

    **earnings_trend**
    - ``trend`` — GROWING / FLAT / DECLINING / INSUFFICIENT_DATA
    - ``predicted_total`` — predicted earnings over next 90 days
    - ``predicted_low`` / ``predicted_high`` — 95% confidence interval

    **activity_feed**
    - Up to 50 timestamped events: leakage discoveries, claim updates,
      and payment deposits, newest first.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    engine = DashboardEngine(db)
    dashboard = engine.compute(artist_id)
    brand = get_branding_for_artist(db, artist_id)
    dashboard["branding"] = branding_metadata(brand)
    dashboard["dashboard_title"] = (
      f"{brand.get('display_name')} Dashboard"
      if bool(brand.get("white_label_enabled"))
      else "Artist Recovery Dashboard"
    )
    unread_support_messages = (
      db.query(SupportMessage)
      .filter(
        SupportMessage.artist_id == artist_id,
        SupportMessage.role == SupportMessageRole.ASSISTANT,
        SupportMessage.is_read.is_(False),
      )
      .count()
    )
    dashboard["support"] = {
      "agent_available": True,
      "unread_support_messages": unread_support_messages,
      "proactive_tip": _support_proactive_tip(dashboard),
    }
    fee_percent = float(artist.contingency_fee_percent or 0.0)
    dashboard["artist_pricing"] = {
      "fee_percent": fee_percent,
      "is_founder": bool(artist.is_founder),
      "founder_slot_number": artist.founder_slot_number,
      "founder_badge": (
        f"Founder #{int(artist.founder_slot_number)} - 12% for life"
        if artist.is_founder and artist.founder_slot_number is not None
        else None
      ),
      "payout_copy": (
        "Your founder rate: 12% - Locked permanently"
        if artist.is_founder
        else f"Platform fee: {fee_percent:.2f}%"
      ),
      "settings_copy": (
        "Contingency fee: 12% (Founder rate - permanent)"
        if artist.is_founder
        else f"Contingency fee: {fee_percent:.2f}%"
      ),
    }

    # ── New feature cards ──────────────────────────────────────────────────
    dashboard["catalog_health"] = _catalog_health_card(artist_id, db)
    dashboard["predicted_recoverable"] = _predicted_recoverable_card(artist_id, db)

    state = get_latest_artist_state(artist_id)
    if not state:
      dashboard.setdefault("agent_orchestra_status", {
        "current_step": None,
        "confidence": None,
        "trace_url": None,
      })
      dashboard.setdefault("onboarding_progress", {"steps_total": 0, "steps_completed": 0, "missing": []})
      dashboard.setdefault("comfort_messages", [])
      dashboard.setdefault("portal_guidance", [])
      dashboard.setdefault("fast_track_claim", None)
      dashboard.setdefault("expected_earnings", {})
      dashboard.setdefault("public_profile", {})
      dashboard.setdefault("readiness_score", None)
      dashboard.setdefault("ugc_opportunities", dashboard.get("ugc_opportunities") or [])
      dashboard.setdefault("catalog_profile", {})
      dashboard.setdefault("split_conflicts", [])
      dashboard.setdefault("registration_actions", [])
      dashboard.setdefault("follow_up_actions", [])
      dashboard.setdefault("agent_activity", [])
      dashboard.setdefault("legal_risk_indicators", {})
      dashboard.setdefault("negotiation_insights", {})
      dashboard.setdefault("escalation_indicators", {})
      dashboard.setdefault("attorney_export_status", {})
      return dashboard

    run_id = str(state.get("run_id") or "")
    current_step = str(state.get("current_step") or "")
    conf = (state.get("confidence_scores") or {}).get(current_step)
    dashboard["agent_orchestra_status"] = {
      "current_step": current_step,
      "confidence": conf,
      "trace_url": f"/artists/{artist_id}/agent-trace/{run_id}" if run_id else None,
    }
    dashboard["onboarding_progress"] = state.get("onboarding_progress") or {}
    dashboard["comfort_messages"] = state.get("comfort_messages") or []
    dashboard["portal_guidance"] = state.get("portal_guidance") or []
    dashboard["fast_track_claim"] = state.get("fast_track_claim")
    dashboard["expected_earnings"] = state.get("expected_earnings") or {}
    dashboard["public_profile"] = state.get("public_profile") or {}
    dashboard["readiness_score"] = state.get("readiness_score")
    dashboard["ugc_opportunities"] = state.get("ugc_opportunities") or dashboard.get("ugc_opportunities") or []
    dashboard["catalog_profile"] = state.get("catalog_profile") or {}
    dashboard["split_conflicts"] = state.get("split_conflicts") or []
    dashboard["registration_actions"] = state.get("registration_actions") or []
    dashboard["follow_up_actions"] = state.get("follow_up_actions") or []
    dashboard["agent_activity"] = state.get("agent_activity") or []
    dashboard["legal_risk_indicators"] = {
      "legal_risk_score": state.get("legal_risk_score"),
      "settlement_probability": state.get("settlement_probability"),
      "escalation_readiness_score": state.get("escalation_readiness_score"),
      "predicted_escalation_probability": state.get("predicted_escalation_probability"),
    }
    dashboard["negotiation_insights"] = {
      "tone_profile": state.get("negotiation_tone_profile") or {},
      "adapted_messages": state.get("adapted_messages") or [],
      "payer_behavior_profile": state.get("payer_behavior_profile") or {},
      "predicted_responsiveness": state.get("predicted_responsiveness"),
      "predicted_settlement_speed_days": state.get("predicted_settlement_speed_days"),
    }
    dashboard["escalation_indicators"] = {
      "escalation_prepared_packet": state.get("escalation_prepared_packet") or {},
      "recommended_packet_emphasis": state.get("recommended_packet_emphasis") or [],
    }
    dashboard["attorney_export_status"] = {
      "attorney_export_summary": state.get("attorney_export_summary") or "",
      "manifest": state.get("attorney_export_manifest") or {},
      "narrative_highlights": state.get("narrative_highlights") or [],
    }
    handoffs = list_handoffs_for_artist(artist_id, limit=1)
    dashboard["agent_handoff_status"] = {
      "latest_handoff": handoffs[0] if handoffs else None,
      "handoff_history_url": f"/artists/{artist_id}/workflow/handoffs",
    }
    return dashboard


@router.get("/artists/{artist_id}/agents/status")
def get_agents_status(
  artist_id: str,
  db: Session = Depends(get_db),
  _: dict = Depends(require_artist_access),
):
  artist = db.query(Artist).filter(Artist.id == artist_id).first()
  if not artist:
    raise HTTPException(status_code=404, detail="Artist not found")

  state = get_latest_artist_state(artist_id) or {}
  run_id = str(state.get("run_id") or "")
  current_step = str(state.get("current_step") or "")
  confidence_scores = state.get("confidence_scores") or {}

  return inject_branding_metadata(db, {
    "artist_id": artist_id,
    "agent_orchestra_status": {
      "current_step": current_step or None,
      "confidence": confidence_scores.get(current_step) if current_step else None,
      "trace_url": f"/artists/{artist_id}/agent-trace/{run_id}" if run_id else None,
      "run_id": run_id or None,
    },
    "onboarding_progress": state.get("onboarding_progress") or {"steps_total": 0, "steps_completed": 0, "missing": []},
    "comfort_messages": state.get("comfort_messages") or [],
    "portal_guidance": state.get("portal_guidance") or [],
    "fast_track_claim": state.get("fast_track_claim"),
    "expected_earnings": state.get("expected_earnings") or {},
    "public_profile": state.get("public_profile") or {},
    "readiness_score": state.get("readiness_score"),
    "ugc_opportunities": state.get("ugc_opportunities") or [],
    "catalog_profile": state.get("catalog_profile") or {},
    "split_conflicts": state.get("split_conflicts") or [],
    "registration_actions": state.get("registration_actions") or [],
    "follow_up_actions": state.get("follow_up_actions") or [],
    "agent_handoff_status": {
      "latest_handoff": (list_handoffs_for_artist(artist_id, limit=1) or [None])[0],
      "handoff_history_url": f"/artists/{artist_id}/workflow/handoffs",
    },
  })


@router.get("/artists/{artist_id}/agent-trace/{run_id}")
def agent_trace(artist_id: str, run_id: str, db: Session = Depends(get_db)):
  trace = get_run_trace(artist_id, run_id)
  if isinstance(trace, dict):
    return inject_branding_metadata(db, {"artist_id": artist_id, **trace})
  return inject_branding_metadata(db, {"artist_id": artist_id, "trace": trace})


@router.get("/artists/{artist_id}/dashboard/flow")
def dashboard_flow(artist_id: str, db: Session = Depends(get_db)):
    flow = DataFlowVisualizer().generate_pipeline_status(artist_id)
    flow["branding"] = branding_metadata(get_branding_for_artist(db, artist_id))
    return flow


@router.get("/artists/{artist_id}/benchmarks")
def dashboard_benchmarks(artist_id: str, db: Session = Depends(get_db)):
    engine = IndustryBenchmarkEngine()
    b = engine.get_benchmarks(artist_id)
    return {
        "artist_id": artist_id,
        "benchmarks": b,
        "message": engine.generate_comparison_report(b),
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
    }


@router.get("/artists/{artist_id}/dashboard/export-guidance")
def export_guidance(artist_id: str, platform: str = "youtube", db: Session = Depends(get_db)):
    links = {
        "youtube": "https://studio.youtube.com/",
        "tiktok": "https://www.tiktok.com/tiktokstudio/",
        "instagram": "https://business.facebook.com/",
        "melon": "https://artist.melon.com/",
        "boomplay": "https://creators.boomplay.com/",
        "tencent": "https://y.tencentmusic.com/",
    }
    link = links.get(platform.lower(), "https://example.com/export")
    return {
        "artist_id": artist_id,
        "platform": platform,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "steps": [
            "Login to platform portal",
            "Open analytics/reports",
            "Export CSV for selected time window",
            f"Upload to /artists/{artist_id}/statements/upload",
        ],
        "export_link": link,
        "upload_link": f"/artists/{artist_id}/statements/upload",
    }


@router.post("/artists/{artist_id}/chat/royalties")
async def chat_royalties(artist_id: str, question: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    dashboard = DashboardEngine(db).compute(artist_id)
    result = await royalty_chat_agent.handle_query(artist_id, question, context=dashboard)
    if isinstance(result, dict):
      return inject_branding_metadata(db, {"artist_id": artist_id, **result})
    return inject_branding_metadata(db, {"artist_id": artist_id, "response": result})


@router.get("/artists/{artist_id}/export/full-transparency")
async def export_full_transparency(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    dashboard = DashboardEngine(db).compute(artist_id)
    brand = get_branding_for_artist(db, artist_id)
    dashboard["branding"] = branding_metadata(brand)
    ledger = ImmutableLedgerViewer(db).get_full_ledger(artist_id, include_raw_statements=True)
    summary = await royalty_chat_agent.handle_query(
        artist_id,
        "Here is everything XR7 knows about your royalties in plain English.",
        context=dashboard,
    )

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "summary.md",
            apply_brand_placeholders(
                f"# {{BRAND.NAME}} Transparency Summary\n\n{summary.get('response')}\n\n{{BRAND.LEGAL_DISCLAIMER}}",
                brand,
            ),
        )
        zf.writestr("dashboard.json", json.dumps(dashboard, indent=2, default=str))
        zf.writestr("full_ledger.json", json.dumps(ledger, indent=2, default=str))
        zf.writestr("branding_manifest.json", json.dumps(branding_metadata(brand), indent=2, default=str))

    return Response(
        content=zip_buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="transparency_{artist_id}.zip"'},
    )
