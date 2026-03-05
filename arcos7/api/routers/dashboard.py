"""
Artist Recovery Dashboard API endpoint.

``GET /artists/{id}/dashboard``

Returns a single, comprehensive JSON document that gives the artist a
complete picture of their recovery status:

- **leakage_discovered** — every anomaly ARCOS7 has detected and its
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

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from arcos7.earnings.dashboard import DashboardEngine
from arcos7.models.artist import Artist
from arcos7.models.base import get_db

router = APIRouter(tags=["dashboard"])

_DASHBOARD_UI_PATH = Path(__file__).resolve().parents[2] / "widget" / "recovery_dashboard.html"


@router.get("/dashboard/ui")
def get_dashboard_ui():
  """Serve the standalone artist recovery dashboard UI page."""
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
    - ``total_net_recovered`` — gross minus ARCOS7 contingency fees

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
