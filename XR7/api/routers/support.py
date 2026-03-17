from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.agents.orchestrator import run_support_agent_turn_sync
from XR7.api.authz import artist_or_404 as _artist_or_404
from XR7.api.authz import authorize_team_access as _authorize_team_access
from XR7.earnings.dashboard import DashboardEngine
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.models.support_message import SupportMessage, SupportMessageRole
from XR7.models.team_access import TeamRole
from XR7.models.work import Work
from XR7.recovery.weekly_digest import build_weekly_digest
from XR7.agents.onboarding_agents import ArtistReadinessScoreAgent


router = APIRouter(tags=["support"])


class SupportChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str | None = None


class SupportChatResponse(BaseModel):
    artist_id: str
    thread_id: str
    response: str
    confidence: float
    suggested_quick_replies: list[str]
    escalate_recommended: bool


class SupportMessageView(BaseModel):
    id: str
    thread_id: str
    role: str
    message: str
    confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class SupportHistoryResponse(BaseModel):
    total: int
    page: int
    page_size: int
    next_cursor: str | None = None
    items: list[SupportMessageView]


class SupportActionRequest(BaseModel):
    action: str = Field(description="one_of_safe_actions")
    payload: dict[str, Any] = Field(default_factory=dict)


class SupportActionResponse(BaseModel):
    artist_id: str
    action: str
    result: dict[str, Any]
    formatted_message: str


class SupportSuggestionResponse(BaseModel):
    artist_id: str
    suggestions: list[str]


def _parse_metadata(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _build_top_payers_snapshot(dashboard: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    rows = dashboard.get("payers_owing") or []
    if not isinstance(rows, list):
        return []
    sorted_rows = sorted(rows, key=lambda r: float((r or {}).get("recoverable_estimate") or 0.0), reverse=True)
    return [
        {
            "payer_id": r.get("payer_id"),
            "payer_name": r.get("payer_name"),
            "payer_type": r.get("payer_type"),
            "recoverable_estimate": float(r.get("recoverable_estimate") or 0.0),
            "claim_count": int(r.get("claim_count") or 0),
            "friction_level": r.get("friction_level"),
        }
        for r in sorted_rows[:limit]
    ]


def _build_proactive_suggestions(dashboard: dict[str, Any]) -> list[str]:
    tips: list[str] = []
    deadlines = dashboard.get("deadlines") or {}
    urgent = int(deadlines.get("urgent_count") or 0)
    if urgent > 0:
        tips.append(f"You have {urgent} urgent SOL items. Prioritize those claims to avoid deadline loss.")

    payers = _build_top_payers_snapshot(dashboard, limit=1)
    if payers:
        p = payers[0]
        tips.append(
            f"{p.get('payer_name')} is your top payer at ${float(p.get('recoverable_estimate') or 0.0):,.2f}. "
            "Review this payer first for faster recovery impact."
        )

    readiness = dashboard.get("readiness_score")
    if readiness is not None and float(readiness) < 70:
        tips.append("Your readiness score is below 70. Run catalog readiness checks before filing additional claims.")

    leakage = (dashboard.get("leakage_discovered") or {}).get("total_estimated_recoverable")
    if leakage and float(leakage) > 0:
        tips.append(f"Estimated leakage is ${float(leakage):,.2f}. Use priority actions to convert this into active claims.")

    if not tips:
        tips.append("No urgent blockers detected. Keep uploading new statements to surface additional recoverable anomalies.")

    return tips[:5]


@router.post("/artists/{artist_id}/support/chat", response_model=SupportChatResponse)
def support_chat(
    artist_id: str,
    payload: SupportChatRequest,
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

    thread_id = (payload.thread_id or str(uuid.uuid4())).strip()
    dashboard = DashboardEngine(db).compute(artist_id)
    agent_state = run_support_agent_turn_sync(
        artist_id,
        message=payload.message,
        thread_id=thread_id,
        dashboard_context=dashboard,
    )

    response_text = str(agent_state.get("support_response") or "I can help with dashboard context and safe actions.")
    confidence = float(agent_state.get("support_confidence") or 0.0)
    quick_replies = list(agent_state.get("support_suggested_replies") or [])[:5]
    escalate = bool(agent_state.get("support_escalation_recommended") or confidence < 0.75)

    user_row = SupportMessage(
        artist_id=artist_id,
        thread_id=thread_id,
        role=SupportMessageRole.USER,
        message=payload.message,
        confidence=None,
        metadata_json=json.dumps({"actor_email": (x_actor_email or "").strip().lower()}),
        is_read=True,
    )
    assistant_row = SupportMessage(
        artist_id=artist_id,
        thread_id=thread_id,
        role=SupportMessageRole.ASSISTANT,
        message=response_text,
        confidence=confidence,
        metadata_json=json.dumps(
            {
                "suggested_quick_replies": quick_replies,
                "escalate_recommended": escalate,
            }
        ),
        is_read=False,
    )
    db.add(user_row)
    db.add(assistant_row)
    db.commit()

    return SupportChatResponse(
        artist_id=artist_id,
        thread_id=thread_id,
        response=response_text,
        confidence=round(confidence, 4),
        suggested_quick_replies=quick_replies,
        escalate_recommended=escalate,
    )


@router.get("/artists/{artist_id}/support/history", response_model=SupportHistoryResponse)
def support_history(
    artist_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    thread_id: str | None = Query(default=None),
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

    base = db.query(SupportMessage).filter(SupportMessage.artist_id == artist_id)
    if thread_id:
        base = base.filter(SupportMessage.thread_id == thread_id)

    if cursor:
        try:
            cursor_ts = datetime.fromisoformat(cursor)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor format. Use ISO8601 timestamp.") from exc
        base = base.filter(SupportMessage.created_at < cursor_ts)

    total = base.count()
    rows = (
        base.order_by(SupportMessage.created_at.desc())
        .offset((page - 1) * page_size if not cursor else 0)
        .limit(page_size)
        .all()
    )

    for row in rows:
        if row.role == SupportMessageRole.ASSISTANT and not row.is_read:
            row.is_read = True
    db.commit()

    next_cursor = rows[-1].created_at.isoformat() if rows else None
    items = [
        SupportMessageView(
            id=row.id,
            thread_id=row.thread_id,
            role=row.role.value if hasattr(row.role, "value") else str(row.role),
            message=row.message,
            confidence=row.confidence,
            metadata=_parse_metadata(row.metadata_json),
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]

    return SupportHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        next_cursor=next_cursor,
        items=items,
    )


@router.post("/artists/{artist_id}/support/action", response_model=SupportActionResponse)
def support_action(
    artist_id: str,
    payload: SupportActionRequest,
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

    action = (payload.action or "").strip().lower()
    dashboard = DashboardEngine(db).compute(artist_id)

    result: dict[str, Any]
    formatted_message: str
    if action == "show_top_payers":
        top = _build_top_payers_snapshot(dashboard, limit=5)
        result = {"top_payers": top}
        formatted_message = (
            "Top payer insights are ready. "
            + (f"Highest recoverable payer is {top[0].get('payer_name')}." if top else "No payer data available yet.")
        )
    elif action == "explain_anomaly":
        anomaly_id = str((payload.payload or {}).get("anomaly_id") or "").strip()
        if not anomaly_id:
            raise HTTPException(status_code=400, detail="payload.anomaly_id is required for explain_anomaly")
        anomaly = (
            db.query(Anomaly)
            .filter(Anomaly.id == anomaly_id, Anomaly.artist_id == artist_id)
            .first()
        )
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        result = {
            "anomaly_id": anomaly.id,
            "category": str(anomaly.category),
            "subtype": anomaly.subtype,
            "severity": str(anomaly.severity),
            "estimated_recoverable": float(anomaly.estimated_recoverable or 0.0),
            "description": anomaly.description,
            "explanation": (
                f"{anomaly.subtype} in {anomaly.category} indicates a mismatch between expected and reported payouts. "
                "Priority depends on severity, confidence, and deadline risk."
            ),
        }
        formatted_message = f"Explained anomaly {anomaly.id} with severity {anomaly.severity}."
    elif action == "generate_weekly_digest_now":
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
        contracts = db.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
        digest = build_weekly_digest(
            artist_id=artist_id,
            anomalies=anomalies,
            claims=claims,
            contracts=[{"id": c.id, "terms": c.terms or {}, "territory": c.territory} for c in contracts],
            payments=[{"id": p.id, "amount": p.amount, "source": p.source} for p in payments],
        )
        result = {"digest_preview": digest}
        formatted_message = "Weekly digest preview generated successfully."
    elif action == "run_catalog_readiness_check":
        works = db.query(Work).filter(Work.artist_id == artist_id).all()
        state = {
            "artist_id": artist_id,
            "catalog_profile": {
                "works_count": len(works),
            },
            "split_conflicts": [],
            "upload_errors": [],
            "rights_conflicts": [],
        }
        readiness = ArtistReadinessScoreAgent(state)
        try:
            import asyncio

            loop = asyncio.get_running_loop()
            if loop.is_running():
                readiness_output = {"readiness_score": dashboard.get("readiness_score")}
            else:
                readiness_output = asyncio.run(readiness)
        except RuntimeError:
            import asyncio

            readiness_output = asyncio.run(readiness)
        result = {
            "readiness_score": readiness_output.get("readiness_score", dashboard.get("readiness_score")),
            "dashboard_readiness_score": dashboard.get("readiness_score"),
        }
        formatted_message = "Catalog readiness check completed."
    else:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported action. Allowed actions: "
                "show_top_payers, explain_anomaly, generate_weekly_digest_now, run_catalog_readiness_check"
            ),
        )

    row = SupportMessage(
        artist_id=artist_id,
        thread_id=str((payload.payload or {}).get("thread_id") or str(uuid.uuid4())),
        role=SupportMessageRole.ACTION,
        message=f"Action executed: {action}",
        confidence=1.0,
        metadata_json=json.dumps({"result": result}),
        is_read=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()

    return SupportActionResponse(
        artist_id=artist_id,
        action=action,
        result=result,
        formatted_message=formatted_message,
    )


@router.get("/artists/{artist_id}/support/suggestions", response_model=SupportSuggestionResponse)
def support_suggestions(
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

    dashboard = DashboardEngine(db).compute(artist_id)
    return SupportSuggestionResponse(
        artist_id=artist_id,
        suggestions=_build_proactive_suggestions(dashboard),
    )
