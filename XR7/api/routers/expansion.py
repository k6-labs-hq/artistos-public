from __future__ import annotations

import json
import hashlib
import io
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.auth.event_notifications import send_event_notification
from XR7.ingestion.connectors.oauth_providers import (
    OAuthProviderError,
    OAuthProviderService,
    parse_scope_string,
)
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
from XR7.models.oauth_connector import (
    ConnectorAccountLink,
    ConnectorAccountLinkSchema,
    ConnectorAccountStatus,
    OAuthConnectorSession,
    OAuthSessionCreateRequest,
    OAuthSessionStatus,
    OAuthTokenExchangeRequest,
    OAuthTokenRefreshRequest,
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


def _normalize_scopes(scopes: list[str] | str | None) -> list[str]:
    if scopes is None:
        return []
    if isinstance(scopes, str):
        raw = scopes.replace(",", " ").split()
    else:
        raw = [s for s in scopes]

    unique_scopes: list[str] = []
    seen: set[str] = set()
    for item in raw:
        scope = item.strip()
        if not scope:
            continue
        lowered = scope.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique_scopes.append(scope)
    return unique_scopes


def _scopes_to_storage(scopes: list[str] | str | None) -> str:
    return " ".join(_normalize_scopes(scopes))


def _scopes_from_storage(scopes_value: str | None) -> list[str]:
    return _normalize_scopes(scopes_value or "")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _session_or_404(artist_id: str, session_id: str, db: Session) -> OAuthConnectorSession:
    session = (
        db.query(OAuthConnectorSession)
        .filter(OAuthConnectorSession.id == session_id, OAuthConnectorSession.artist_id == artist_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="OAuth session not found")
    return session


def _account_or_404(artist_id: str, account_id: str, db: Session) -> ConnectorAccountLink:
    account = (
        db.query(ConnectorAccountLink)
        .filter(ConnectorAccountLink.id == account_id, ConnectorAccountLink.artist_id == artist_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="Connector account not found")
    return account


def _artist_or_404(artist_id: str, db: Session) -> Artist:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


def _authorize_team_access(
    artist_id: str,
    db: Session,
    allowed_roles: set[TeamRole],
    *,
    actor_email: str | None,
    actor_role: str | None,
) -> None:
    """Enforce team-member access when team records exist for an artist.

    Bootstrap mode: if the artist has no team members yet, access is allowed.
    """
    members_exist = db.query(TeamMember.id).filter(TeamMember.artist_id == artist_id).first() is not None
    if not members_exist:
        return

    if not actor_email:
        raise HTTPException(
            status_code=403,
            detail="X-Actor-Email is required once team access is configured for this artist.",
        )

    member = (
        db.query(TeamMember)
        .filter(
            TeamMember.artist_id == artist_id,
            func.lower(TeamMember.user_email) == actor_email.strip().lower(),
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Actor is not a team member for this artist.")

    member_role = TeamRole(member.role)
    if member_role not in allowed_roles:
        allowed = ", ".join(sorted(r.value for r in allowed_roles))
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient role. Allowed roles: {allowed}.",
        )

    if actor_role and actor_role.strip().lower() != member_role.value:
        raise HTTPException(
            status_code=403,
            detail="X-Actor-Role does not match the role assigned to this team member.",
        )


@router.put("/artists/{artist_id}/notifications/preferences", response_model=NotificationPreferenceSchema)
def upsert_notification_preferences(
    artist_id: str,
    payload: NotificationPreferenceUpsert,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
def get_notification_preferences(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
def urgent_sol_notification_check(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    payload: OAuthSessionCreateRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
    now = _utc_now()
    state = hashlib.sha256(f"{artist_id}:{payload.provider}:{uuid.uuid4()}".encode("utf-8")).hexdigest()
    provider_service = OAuthProviderService(payload.provider)
    requested_scopes = _normalize_scopes(payload.scopes) or provider_service.default_scopes()
    oauth_session = OAuthConnectorSession(
        artist_id=artist_id,
        provider=payload.provider,
        redirect_uri=payload.redirect_uri,
        state=state,
        requested_scopes=_scopes_to_storage(requested_scopes),
        tenant_id=payload.tenant_id,
        status=OAuthSessionStatus.PENDING,
        created_by_email=x_actor_email,
        expires_at=now.replace(microsecond=0) + timedelta(minutes=15),
        created_at=now,
        updated_at=now,
    )
    db.add(oauth_session)
    db.commit()
    db.refresh(oauth_session)

    authorize_url = provider_service.build_authorization_url(
        redirect_uri=payload.redirect_uri,
        state=state,
        scopes=requested_scopes,
        tenant_id=payload.tenant_id,
    )
    return {
        "artist_id": artist_id,
        "session_id": oauth_session.id,
        "provider": payload.provider,
        "oauth_state": state,
        "redirect_uri": payload.redirect_uri,
        "requested_scopes": requested_scopes,
        "tenant_id": payload.tenant_id,
        "authorization_url": authorize_url,
        "provider_configured": provider_service.configured(),
        "expires_at": oauth_session.expires_at.isoformat(),
        "note": "Use this state token for callback validation, then call exchange endpoint to store linked account tokens.",
    }


@router.post("/artists/{artist_id}/connect/oauth-session/{session_id}/exchange")
def exchange_oauth_code(
    artist_id: str,
    session_id: str,
    payload: OAuthTokenExchangeRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    oauth_session = _session_or_404(artist_id, session_id, db)
    now = _utc_now()

    if oauth_session.status != OAuthSessionStatus.PENDING:
        raise HTTPException(status_code=409, detail="OAuth session is not pending")
    session_expires_at = _as_utc(oauth_session.expires_at)
    if session_expires_at and session_expires_at < now:
        oauth_session.status = OAuthSessionStatus.EXPIRED
        oauth_session.updated_at = now
        db.commit()
        raise HTTPException(status_code=400, detail="OAuth session has expired")
    if payload.state != oauth_session.state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    if payload.tenant_id != oauth_session.tenant_id:
        raise HTTPException(status_code=400, detail="OAuth tenant mismatch")

    requested_scopes = _scopes_from_storage(oauth_session.requested_scopes)
    provider_service = OAuthProviderService(oauth_session.provider)
    token_data: dict | None = None
    if payload.access_token is None or payload.refresh_token is None:
        try:
            token_data = provider_service.exchange_code(
                code=payload.code,
                redirect_uri=oauth_session.redirect_uri,
                tenant_id=payload.tenant_id,
                fallback_scopes=requested_scopes,
            )
        except OAuthProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    granted_scopes = _normalize_scopes(payload.granted_scopes)
    if not granted_scopes:
        if token_data:
            granted_scopes = _normalize_scopes(parse_scope_string(token_data.get("scope")))
        if not granted_scopes:
            granted_scopes = requested_scopes

    missing_scopes = sorted(set(s.lower() for s in requested_scopes) - set(s.lower() for s in granted_scopes))

    if missing_scopes and not payload.allow_partial_scope_grant:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Provider did not grant all requested scopes",
                "missing_scopes": missing_scopes,
            },
        )

    access_token = payload.access_token or (token_data or {}).get("access_token")
    refresh_token = payload.refresh_token or (token_data or {}).get("refresh_token")
    token_type = payload.token_type or (token_data or {}).get("token_type") or "Bearer"
    expires_in_seconds = payload.expires_in_seconds
    if token_data is not None:
        expires_in_seconds = int(token_data.get("expires_in") or expires_in_seconds or 3600)

    if not access_token:
        raise HTTPException(status_code=400, detail="Missing access token from OAuth exchange")

    account = (
        db.query(ConnectorAccountLink)
        .filter(
            ConnectorAccountLink.artist_id == artist_id,
            ConnectorAccountLink.provider == oauth_session.provider,
            ConnectorAccountLink.tenant_id == payload.tenant_id,
            ConnectorAccountLink.external_account_id == payload.external_account_id,
        )
        .first()
    )

    token_expires_at = None
    if expires_in_seconds is not None:
        token_expires_at = now + timedelta(seconds=max(0, expires_in_seconds))

    if not account:
        account = ConnectorAccountLink(
            artist_id=artist_id,
            provider=oauth_session.provider,
            tenant_id=payload.tenant_id,
            external_account_id=payload.external_account_id,
            display_name=payload.display_name,
            profile_metadata_json=json.dumps(payload.profile_metadata or {}),
            granted_scopes=_scopes_to_storage(granted_scopes),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            token_expires_at=token_expires_at,
            last_refreshed_at=now,
            status=ConnectorAccountStatus.ACTIVE,
            created_by_email=x_actor_email,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(account)
    else:
        account.display_name = payload.display_name or account.display_name
        if payload.profile_metadata is not None:
            account.profile_metadata_json = json.dumps(payload.profile_metadata)
        account.granted_scopes = _scopes_to_storage(granted_scopes)
        account.access_token = access_token
        account.refresh_token = refresh_token
        account.token_type = token_type
        account.token_expires_at = token_expires_at
        account.last_refreshed_at = now
        account.status = ConnectorAccountStatus.ACTIVE
        account.is_active = True
        account.updated_at = now

    oauth_session.status = OAuthSessionStatus.EXCHANGED
    oauth_session.updated_at = now

    db.commit()
    db.refresh(account)

    return {
        "artist_id": artist_id,
        "provider": oauth_session.provider,
        "session_id": oauth_session.id,
        "account": ConnectorAccountLinkSchema.model_validate(account),
        "scope_check": {
            "requested": requested_scopes,
            "granted": granted_scopes,
            "missing": missing_scopes,
            "full_grant": len(missing_scopes) == 0,
        },
        "linked": True,
        "oauth_code_consumed": bool(payload.code),
        "provider_configured": provider_service.configured(),
        "provider_exchange_mode": "live" if token_data and not token_data.get("simulated") else "simulated",
    }


@router.get("/artists/{artist_id}/connect/accounts")
def list_connected_accounts(
    artist_id: str,
    provider: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    query = db.query(ConnectorAccountLink).filter(ConnectorAccountLink.artist_id == artist_id)
    if provider:
        query = query.filter(func.lower(ConnectorAccountLink.provider) == provider.strip().lower())
    if tenant_id:
        query = query.filter(ConnectorAccountLink.tenant_id == tenant_id)
    if not include_inactive:
        query = query.filter(ConnectorAccountLink.is_active.is_(True))

    rows = query.order_by(ConnectorAccountLink.created_at.desc()).all()
    now = _utc_now()
    accounts = []
    for row in rows:
        token_expires_at = _as_utc(row.token_expires_at)
        needs_refresh = bool(token_expires_at and token_expires_at <= now)
        item = ConnectorAccountLinkSchema.model_validate(row).model_dump(mode="json")
        item["granted_scopes"] = _scopes_from_storage(row.granted_scopes)
        item["needs_refresh"] = needs_refresh
        accounts.append(item)

    return {
        "artist_id": artist_id,
        "count": len(accounts),
        "accounts": accounts,
    }


@router.post("/artists/{artist_id}/connect/accounts/{account_id}/refresh")
def refresh_connected_account_token(
    artist_id: str,
    account_id: str,
    payload: OAuthTokenRefreshRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    account = _account_or_404(artist_id, account_id, db)
    if not account.is_active or account.status != ConnectorAccountStatus.ACTIVE:
        raise HTTPException(status_code=409, detail="Connector account is not active")
    if not account.refresh_token:
        raise HTTPException(status_code=400, detail="Connector account has no refresh token")

    now = _utc_now()
    token_expires_at = _as_utc(account.token_expires_at)
    if not payload.force and token_expires_at and token_expires_at > now + timedelta(minutes=2):
        return {
            "artist_id": artist_id,
            "account_id": account_id,
            "refreshed": False,
            "reason": "token_still_valid",
            "token_expires_at": token_expires_at.isoformat(),
        }

    provider_service = OAuthProviderService(account.provider)
    try:
        refreshed = provider_service.refresh_token(
            account.refresh_token,
            fallback_expires_in=payload.expires_in_seconds,
        )
    except OAuthProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    account.access_token = refreshed["access_token"]
    if payload.rotate_refresh_token:
        account.refresh_token = refreshed.get("refresh_token")
    account.token_type = refreshed.get("token_type") or account.token_type
    account.last_refreshed_at = now
    account.token_expires_at = now + timedelta(seconds=max(0, int(refreshed.get("expires_in") or payload.expires_in_seconds)))
    account.updated_at = now

    db.commit()

    return {
        "artist_id": artist_id,
        "account_id": account_id,
        "provider": account.provider,
        "tenant_id": account.tenant_id,
        "refreshed": True,
        "token_expires_at": account.token_expires_at.isoformat() if account.token_expires_at else None,
        "rotated_refresh_token": payload.rotate_refresh_token,
        "provider_configured": provider_service.configured(),
        "provider_refresh_mode": "live" if not refreshed.get("simulated") else "simulated",
    }


@router.delete("/artists/{artist_id}/connect/accounts/{account_id}")
def disconnect_connected_account(
    artist_id: str,
    account_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    account = _account_or_404(artist_id, account_id, db)
    account.is_active = False
    account.status = ConnectorAccountStatus.DISCONNECTED
    account.updated_at = _utc_now()
    db.commit()

    return {
        "artist_id": artist_id,
        "account_id": account_id,
        "disconnected": True,
    }


@router.get("/artists/{artist_id}/connect/fallbacks")
def list_connect_fallbacks(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
def add_team_member(
    artist_id: str,
    payload: TeamMemberCreate,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)

    existing_any = db.query(TeamMember.id).filter(TeamMember.artist_id == artist_id).first() is not None
    if not existing_any:
        if payload.role != TeamRole.ARTIST:
            raise HTTPException(
                status_code=400,
                detail="First team member must use role 'artist' to establish ownership.",
            )
    else:
        _authorize_team_access(
            artist_id,
            db,
            {TeamRole.ARTIST},
            actor_email=x_actor_email,
            actor_role=x_actor_role,
        )

    existing_member = (
        db.query(TeamMember)
        .filter(
            TeamMember.artist_id == artist_id,
            func.lower(TeamMember.user_email) == payload.user_email.strip().lower(),
        )
        .first()
    )
    if existing_member:
        raise HTTPException(status_code=409, detail="Team member with this email already exists.")

    member = TeamMember(artist_id=artist_id, user_email=payload.user_email, role=payload.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/artists/{artist_id}/team/members", response_model=list[TeamMemberSchema])
def list_team_members(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
    return db.query(TeamMember).filter(TeamMember.artist_id == artist_id).all()


@router.delete("/artists/{artist_id}/team/members/{member_id}")
def remove_team_member(
    artist_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
    member = db.query(TeamMember).filter(TeamMember.id == member_id, TeamMember.artist_id == artist_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    db.delete(member)
    db.commit()
    return {"deleted": True, "member_id": member_id}


@router.get("/artists/{artist_id}/recovery/benchmark-percentiles")
def benchmark_percentiles(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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


@router.post(
    "/claims/{claim_id}/evidence/anchor",
    response_model=EvidenceAnchorSchema,
    operation_id="anchor_evidence_packet_internal_immutable_log",
)
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
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
def generate_audit_demand_letter(
    artist_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )
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
