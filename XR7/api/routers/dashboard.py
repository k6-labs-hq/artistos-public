"""
Artist Recovery Dashboard API endpoint.

``GET /artists/{id}/dashboard``

Returns a single, comprehensive JSON document that gives the artist a
complete picture of their recovery status:

- **leakage_discovered** — every anomaly XR7 has detected and its
  estimated dollar value, broken down by category and severity.

- **in_pursuit** — currently active claims (IDENTIFIED → ACCEPTED),
  the total dollar amount being chased, and closed-claim totals.

- **recovered_and_deposited** — Celero DISBURSEMENT transactions that
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

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from XR7.earnings.dashboard import DashboardEngine
from XR7.llm.claim_drafter import royalty_chat_agent
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.transparency.data_flow_visualizer import DataFlowVisualizer
from XR7.transparency.immutable_ledger_viewer import ImmutableLedgerViewer
from XR7.transparency.industry_benchmarks import IndustryBenchmarkEngine

router = APIRouter(tags=["dashboard"])

_DASHBOARD_UI_PATH = Path(__file__).resolve().parents[2] / "widget" / "recovery_dashboard.html"
_MOBILE_UI_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "ui" / "mobile.html"


@router.get("/dashboard/ui")
def get_dashboard_ui():
  """Serve the standalone artist recovery dashboard UI page."""
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
    - ``total_deposited`` — sum of all Celero disbursements received
    - ``deposits`` — per-deposit log with Celero transaction IDs

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
    return engine.compute(artist_id)


  @router.get("/artists/{artist_id}/dashboard/flow")
  def dashboard_flow(artist_id: str):
    return DataFlowVisualizer().generate_pipeline_status(artist_id)


  @router.get("/artists/{artist_id}/benchmarks")
  def dashboard_benchmarks(artist_id: str):
    engine = IndustryBenchmarkEngine()
    b = engine.get_benchmarks(artist_id)
    return {"artist_id": artist_id, "benchmarks": b, "message": engine.generate_comparison_report(b)}


  @router.get("/artists/{artist_id}/dashboard/export-guidance")
  def export_guidance(artist_id: str, platform: str = "youtube"):
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
    return await royalty_chat_agent.handle_query(artist_id, question, context=dashboard)


  @router.get("/artists/{artist_id}/export/full-transparency")
  async def export_full_transparency(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
      raise HTTPException(status_code=404, detail="Artist not found")

    dashboard = DashboardEngine(db).compute(artist_id)
    ledger = ImmutableLedgerViewer(db).get_full_ledger(artist_id, include_raw_statements=True)
    summary = await royalty_chat_agent.handle_query(
      artist_id,
      "Here is everything XR7 knows about your royalties in plain English.",
      context=dashboard,
    )

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
      zf.writestr("summary.md", f"# Transparency Summary\n\n{summary.get('response')}")
      zf.writestr("dashboard.json", json.dumps(dashboard, indent=2, default=str))
      zf.writestr("full_ledger.json", json.dumps(ledger, indent=2, default=str))

    return Response(
      content=zip_buf.getvalue(),
      media_type="application/zip",
      headers={"Content-Disposition": f'attachment; filename="transparency_{artist_id}.zip"'},
    )
