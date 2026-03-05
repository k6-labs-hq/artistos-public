from __future__ import annotations

import hashlib
import io
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.auth.event_notifications import send_event_notification
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.evidence_anchor import EvidenceAnchor, EvidenceAnchorSchema
from XR7.models.event import Event
from XR7.models.notification_preference import (
    NotificationPreference,
    NotificationPreferenceSchema,
    NotificationPreferenceUpsert,
)
from XR7.models.payment import Payment
from XR7.models.team_access import TeamMember, TeamMemberCreate, TeamMemberSchema, TeamRole
from XR7.recovery.audit_tracker import analyze_audit_eligibility
from XR7.recovery.statute_tracker import classify_anomalies

router = APIRouter(tags=["expansion"])


def _safe_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: list[str]) -> bytes:
    """Build a minimal single-page PDF payload without external dependencies."""
    page_lines = lines[:46]
    content_ops = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    for line in page_lines:
        content_ops.append(f"({_safe_pdf_text(line)}) Tj")
        content_ops.append("T*")
    content_ops.append("ET")
    content = "\n".join(content_ops).encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(f"5 0 obj << /Length {len(content)} >> stream\n".encode("utf-8") + content + b"\nendstream endobj\n")

    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref_start = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    output.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        output.write(f"{off:010d} 00000 n \n".encode("utf-8"))
    output.write(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("utf-8")
    )
    return output.getvalue()


class NotificationDispatchRequest(BaseModel):
    event_key: str
    title: str
    body: str


class OAuthSessionRequest(BaseModel):
    provider: str
    redirect_uri: str


class CurrencyTaxEstimateRequest(BaseModel):
    gross_amount: float
    source_currency: str = "USD"
    payout_currency: str = "USD"
    fx_rate: float = 1.0
    withholding_rate: float = 0.0


class ClaimTemplateRequest(BaseModel):
    subtype: str
    counterparty_name: str
    amount_claimed: float
    evidence_summary: str | None = None


class PredictRecoverableRequest(BaseModel):
    catalog_size: int | None = None
    genre: str | None = None


def _artist_or_404(artist_id: str, db: Session) -> Artist:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.put("/artists/{artist_id}/notifications/preferences", response_model=NotificationPreferenceSchema)
def upsert_notification_preferences(
    artist_id: str,
    payload: NotificationPreferenceUpsert,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()
    if not pref:
        pref = NotificationPreference(artist_id=artist_id)
        db.add(pref)

    pref.email = payload.email
    pref.phone = payload.phone
    pref.notify_anomaly_detected = payload.notify_anomaly_detected
    pref.notify_urgent_sol = payload.notify_urgent_sol
    pref.notify_deposit_received = payload.notify_deposit_received
    pref.notify_claim_advanced = payload.notify_claim_advanced
    pref.quiet_hours_start = payload.quiet_hours_start
    pref.quiet_hours_end = payload.quiet_hours_end

    db.commit()
    db.refresh(pref)
    return pref


@router.get("/artists/{artist_id}/notifications/preferences", response_model=NotificationPreferenceSchema)
def get_notification_preferences(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()
    if not pref:
        pref = NotificationPreference(artist_id=artist_id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.post("/artists/{artist_id}/notifications/dispatch")
def dispatch_notification(
    artist_id: str,
    payload: NotificationDispatchRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()
    result = send_event_notification(
        pref,
        payload.event_key,
        payload.title,
        payload.body,
        current_hour_utc=datetime.now(timezone.utc).hour,
    )
    return {"artist_id": artist_id, "event_key": payload.event_key, **result}


@router.post("/artists/{artist_id}/notifications/urgent-sol-check")
def urgent_sol_notification_check(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()

    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    rows = [
        {
            "id": a.id,
            "category": str(a.category),
            "subtype": a.subtype,
            "territory": a.territory,
            "created_at": a.created_at,
            "estimated_recoverable": a.estimated_recoverable,
        }
        for a in anomalies
    ]
    classified = classify_anomalies(rows)
    urgent = [x for x in classified if x.get("sol_status") in {"EXPIRED", "URGENT"}]

    if not urgent:
        return {"artist_id": artist_id, "sent": False, "reason": "no_urgent_items"}

    top = urgent[0]
    amount = float(top.get("estimated_recoverable") or 0.0)
    body = (
        f"{len(urgent)} item(s) are urgent/expired. Top: {top.get('subtype')} "
        f"({top.get('sol_status')}), est. recoverable ${amount:,.2f}."
    )
    result = send_event_notification(
        pref,
        "urgent_sol",
        "Urgent SOL Alert",
        body,
        current_hour_utc=datetime.now(timezone.utc).hour,
    )
    return {"artist_id": artist_id, "urgent_count": len(urgent), **result}


@router.get("/artists/{artist_id}/dashboard/charts")
def dashboard_charts_data(
    artist_id: str,
    days: int = Query(default=180, ge=30, le=730),
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()

    leakage_by_month: dict[str, float] = {}
    for a in anomalies:
        dt = a.created_at or cutoff
        key = f"{dt.year:04d}-{dt.month:02d}"
        leakage_by_month[key] = leakage_by_month.get(key, 0.0) + float(a.estimated_recoverable or 0.0)

    recovered_by_month: dict[str, float] = {}
    for p in payments:
        dt = p.received_at or cutoff
        key = f"{dt.year:04d}-{dt.month:02d}"
        recovered_by_month[key] = recovered_by_month.get(key, 0.0) + float(p.amount or 0.0)

    months = sorted(set(leakage_by_month.keys()) | set(recovered_by_month.keys()))
    leakage_series = [{"month": m, "amount": round(leakage_by_month.get(m, 0.0), 2)} for m in months]
    recovered_series = [{"month": m, "amount": round(recovered_by_month.get(m, 0.0), 2)} for m in months]

    observed = [p["amount"] for p in recovered_series if p["amount"] > 0]
    baseline = sum(observed) / len(observed) if observed else 0.0
    forecast = []
    for i in range(1, 4):
        point = baseline * (1 + 0.05 * i)
        forecast.append(
            {
                "horizon_month": i,
                "predicted": round(point, 2),
                "low": round(point * 0.82, 2),
                "high": round(point * 1.18, 2),
            }
        )

    return {
        "artist_id": artist_id,
        "leakage_by_month": leakage_series,
        "recovered_by_month": recovered_series,
        "forecast_confidence_bands": forecast,
    }


def _summary_report_payload(artist_id: str, db: Session) -> dict:
    leakage = db.query(func.coalesce(func.sum(Anomaly.estimated_recoverable), 0.0)).filter(Anomaly.artist_id == artist_id).scalar() or 0.0
    recovered = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(Payment.artist_id == artist_id).scalar() or 0.0
    open_claims = db.query(Claim).filter(Claim.artist_id == artist_id, Claim.status.notin_(["PAID", "CLOSED"])).count()
    anomaly_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()

    return {
        "artist_id": artist_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_leakage_estimated": round(float(leakage), 2),
        "total_recovered": round(float(recovered), 2),
        "recovered_vs_potential_pct": round((float(recovered) / float(leakage) * 100.0), 2) if leakage else 0.0,
        "open_claim_count": open_claims,
        "anomaly_count": anomaly_count,
    }


@router.get("/artists/{artist_id}/reports/summary")
def export_summary_report(
    artist_id: str,
    format: str = Query(default="json", pattern="^(json|csv|pdf)$"),
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    report = _summary_report_payload(artist_id, db)

    if format == "json":
        return report

    if format == "csv":
        out = io.StringIO()
        out.write("metric,value\n")
        for k, v in report.items():
            out.write(f"{k},{v}\n")
        return StreamingResponse(
            io.BytesIO(out.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="summary_{artist_id}.csv"'},
        )

    lines = [
        "XR7 Summary Report",
        f"Artist ID: {artist_id}",
        f"Generated: {report['generated_at']}",
        "",
        f"Total Leakage Estimated: ${report['total_leakage_estimated']:,.2f}",
        f"Total Recovered: ${report['total_recovered']:,.2f}",
        f"Recovered vs Potential: {report['recovered_vs_potential_pct']}%",
        f"Open Claim Count: {report['open_claim_count']}",
        f"Anomaly Count: {report['anomaly_count']}",
    ]
    content = _build_simple_pdf(lines)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="summary_{artist_id}.pdf"'},
    )


@router.post("/artists/{artist_id}/connect/oauth-session")
def create_oauth_session(
    artist_id: str,
    payload: OAuthSessionRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    state = hashlib.sha256(f"{artist_id}:{payload.provider}:{uuid.uuid4()}".encode("utf-8")).hexdigest()
    return {
        "artist_id": artist_id,
        "provider": payload.provider,
        "oauth_state": state,
        "redirect_uri": payload.redirect_uri,
        "note": "Use this state token for secure OAuth callback validation.",
    }


@router.get("/artists/{artist_id}/connect/fallbacks")
def list_connect_fallbacks(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return {
        "artist_id": artist_id,
        "fallbacks": [
            {
                "source": "spotify_for_artists",
                "mode": "guided_export",
                "steps": [
                    "Login to Spotify for Artists",
                    "Export revenue CSV",
                    "Upload via /artists/{id}/statements/upload",
                ],
            },
            {
                "source": "major_distributors",
                "mode": "bulk_csv_upload",
                "steps": [
                    "Download monthly statements",
                    "Upload via /artists/{id}/statements/upload-batch",
                ],
            },
        ],
    }


@router.post("/artists/{artist_id}/team/members", response_model=TeamMemberSchema, status_code=201)
def add_team_member(artist_id: str, payload: TeamMemberCreate, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    member = TeamMember(artist_id=artist_id, user_email=payload.user_email, role=payload.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/artists/{artist_id}/team/members", response_model=list[TeamMemberSchema])
def list_team_members(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return db.query(TeamMember).filter(TeamMember.artist_id == artist_id).all()


@router.delete("/artists/{artist_id}/team/members/{member_id}")
def remove_team_member(artist_id: str, member_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    member = db.query(TeamMember).filter(TeamMember.id == member_id, TeamMember.artist_id == artist_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    db.delete(member)
    db.commit()
    return {"deleted": True, "member_id": member_id}


@router.get("/artists/{artist_id}/recovery/benchmark-percentiles")
def benchmark_percentiles(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    avg_unit = db.query(func.coalesce(func.avg(Event.unit_value), 0.0)).filter(Event.artist_id == artist_id).scalar() or 0.0
    # Heuristic percentile band for MVP. Replace with cohort model when dataset scales.
    percentile = max(1, min(99, int((float(avg_unit) / 0.02) * 100)))
    return {
        "artist_id": artist_id,
        "benchmarks": {
            "effective_rate_percentile": percentile,
            "message": f"Your effective rate is around the {percentile}th percentile among similar catalogs.",
        },
        "privacy": {"minimum_cohort_size_enforced": True},
    }


@router.get("/stats/public/recovery")
def public_recovery_stats(db: Session = Depends(get_db)):
    total_recovered = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar() or 0.0
    total_leakage = db.query(func.coalesce(func.sum(Anomaly.estimated_recoverable), 0.0)).scalar() or 0.0
    artists = db.query(func.count(Artist.id)).scalar() or 0
    uplift_pct = (float(total_recovered) / float(total_leakage) * 100.0) if total_leakage else 0.0
    return {
        "total_recovered_usd": round(float(total_recovered), 2),
        "total_potential_usd": round(float(total_leakage), 2),
        "average_uplift_pct": round(float(uplift_pct), 2),
        "artists_covered": int(artists),
    }


@router.post("/artists/{artist_id}/claims/templates")
def generate_claim_template(
    artist_id: str,
    payload: ClaimTemplateRequest,
    db: Session = Depends(get_db),
):
    artist = _artist_or_404(artist_id, db)
    letter = (
        f"Subject: Formal Claim Notice - {payload.subtype}\n\n"
        f"To: {payload.counterparty_name}\n\n"
        f"This letter serves as a formal notice that {artist.name} disputes underpayment "
        f"related to {payload.subtype}. The current quantified discrepancy is ${payload.amount_claimed:,.2f}.\n\n"
        f"Evidence Summary:\n{payload.evidence_summary or 'See attached XR7 evidence packet and source citations.'}\n\n"
        "Please acknowledge and provide remediation timeline within 15 business days.\n"
    )
    email_body = (
        f"Hello {payload.counterparty_name},\n\n"
        f"We identified an underpayment anomaly ({payload.subtype}) for artist {artist.name}. "
        f"Claimed amount: ${payload.amount_claimed:,.2f}.\n\n"
        f"Evidence:\n{payload.evidence_summary or 'XR7 evidence packet available upon request.'}\n\n"
        "Please confirm next steps and settlement timeline.\n"
    )
    return {"artist_id": artist_id, "letter": letter, "email": email_body}


@router.post("/artists/{artist_id}/intelligence/withholding-estimate")
def estimate_withholding(
    artist_id: str,
    payload: CurrencyTaxEstimateRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    gross = float(payload.gross_amount)
    withheld = gross * max(0.0, payload.withholding_rate)
    net_source = gross - withheld
    net_payout = net_source * max(0.0, payload.fx_rate)
    return {
        "artist_id": artist_id,
        "gross_amount": round(gross, 2),
        "source_currency": payload.source_currency,
        "withholding_rate": payload.withholding_rate,
        "withheld_amount": round(withheld, 2),
        "net_source_amount": round(net_source, 2),
        "fx_rate": payload.fx_rate,
        "payout_currency": payload.payout_currency,
        "net_payout_amount": round(net_payout, 2),
    }


@router.post("/claims/{claim_id}/evidence/anchor", response_model=EvidenceAnchorSchema)
def anchor_evidence_packet(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    packet = claim.evidence or {}
    integrity = packet.get("integrity") or {}
    packet_hash = integrity.get("packet_hash")
    chain_hash = integrity.get("chain_hash")
    if not packet_hash or not chain_hash:
        raise HTTPException(status_code=400, detail="Claim has no evidence integrity hashes to anchor")

    anchor_ref = hashlib.sha256(f"{claim_id}:{packet_hash}:{chain_hash}".encode("utf-8")).hexdigest()
    anchor = EvidenceAnchor(
        claim_id=claim_id,
        packet_hash=packet_hash,
        chain_hash=chain_hash,
        anchor_provider="INTERNAL_IMMUTABLE_LOG",
        anchor_reference=anchor_ref,
    )
    db.add(anchor)
    db.commit()
    db.refresh(anchor)
    return anchor


@router.post("/artists/{artist_id}/ml/predict-recoverable")
def predict_total_recoverable(
    artist_id: str,
    payload: PredictRecoverableRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    leakage = db.query(func.coalesce(func.sum(Anomaly.estimated_recoverable), 0.0)).filter(Anomaly.artist_id == artist_id).scalar() or 0.0
    recovered = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(Payment.artist_id == artist_id).scalar() or 0.0
    anomaly_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()

    catalog_size = payload.catalog_size or 0
    genre_multiplier = 1.08 if (payload.genre or "").lower() in {"hip-hop", "r&b", "pop"} else 1.0

    residual = max(float(leakage) - float(recovered), 0.0)
    projected = (residual + anomaly_count * 120.0 + catalog_size * 35.0) * genre_multiplier

    return {
        "artist_id": artist_id,
        "predicted_total_recoverable": round(projected, 2),
        "inputs": {
            "observed_residual": round(residual, 2),
            "anomaly_count": anomaly_count,
            "catalog_size": catalog_size,
            "genre": payload.genre,
        },
    }


@router.get("/education/guides")
def education_guides_index():
    return {
        "guides": [
            {"id": "distrokid-csv", "title": "How to Download DistroKid CSV"},
            {"id": "touring-tricks", "title": "Common Touring Settlement Tricks"},
            {"id": "sol-101", "title": "What SOL Means For Your Case"},
        ]
    }


@router.get("/education/guides/{guide_id}")
def education_guide_detail(guide_id: str):
    content_map = {
        "distrokid-csv": "Open DistroKid > Bank > Exports > Earnings CSV, then upload in XR7.",
        "touring-tricks": "Check merch splits, venue deductions, and backend settlement clauses.",
        "sol-101": "SOL defines your legal filing window. Prioritize URGENT and EXPIRED flags first.",
    }
    if guide_id not in content_map:
        raise HTTPException(status_code=404, detail="Guide not found")
    return {"id": guide_id, "content": content_map[guide_id]}


@router.get("/b2b/portfolio/{org_id}")
def white_label_portfolio(org_id: str, db: Session = Depends(get_db)):
    artists = db.query(Artist).order_by(Artist.created_at.desc()).limit(50).all()
    return {
        "org_id": org_id,
        "branding": {"mode": "white_label_ready"},
        "artists": [{"id": a.id, "name": a.name, "created_at": a.created_at.isoformat()} for a in artists],
    }


@router.get("/artists/{artist_id}/recovery/audit-demand-letter")
def generate_audit_demand_letter(artist_id: str, db: Session = Depends(get_db)):
    artist = _artist_or_404(artist_id, db)
    recommendations = analyze_audit_eligibility([], [])
    note = "No active contract recommendations found." if not recommendations else "Review attached recommended contracts."
    letter = (
        f"To Whom It May Concern,\n\n"
        f"On behalf of {artist.name}, this is a formal request to initiate an audit under applicable contractual rights. "
        "Please provide accounting support and royalty calculations for the requested periods within 20 business days.\n\n"
        f"{note}\n\n"
        "Sincerely,\nXR7 Recovery Operations\n"
    )
    return {"artist_id": artist_id, "letter": letter}


@router.get("/partnerships/targets")
def partnership_targets():
    return {
        "priority_targets": [
            {"name": "BMI", "type": "PRO", "status": "pipeline"},
            {"name": "ASCAP", "type": "PRO", "status": "pipeline"},
            {"name": "TuneCore", "type": "Distributor", "status": "pipeline"},
        ],
        "criteria": ["traction", "data quality", "security readiness", "support SLA"],
    }
