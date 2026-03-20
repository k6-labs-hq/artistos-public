"""SLO dashboards + tenant cost telemetry router."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.slo_metric import (
    SloMetric,
    SloMetricCreate,
    SloMetricSchema,
    SloMetricUpdate,
    TenantCostLedger,
    TenantCostLedgerCreate,
    TenantCostLedgerSchema,
)

router = APIRouter(tags=["slo"])

_ADMIN_SECRET = os.environ.get("ADMIN_SECRET_KEY", "admin-secret")


def _require_admin(x_admin_key: str = Header(...)):
    if x_admin_key != _ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Admin key required")


# ---------------------------------------------------------------------------
# SLO metrics
# ---------------------------------------------------------------------------

@router.post(
    "/admin/orgs/{org_id}/slo",
    response_model=SloMetricSchema,
    status_code=201,
    dependencies=[Depends(_require_admin)],
)
def define_slo(org_id: str, body: SloMetricCreate, db: Session = Depends(get_db)):
    """Define a new SLO metric definition for an org."""
    metric = SloMetric(
        org_id=org_id,
        metric_name=body.metric_name,
        window_seconds=body.window_seconds,
        threshold_ms=body.threshold_ms,
        description=body.description,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@router.get(
    "/admin/orgs/{org_id}/slo",
    response_model=List[SloMetricSchema],
    dependencies=[Depends(_require_admin)],
)
def list_slo_metrics(
    org_id: str,
    breached_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List SLO metrics for an org, optionally filtered to breached ones."""
    q = db.query(SloMetric).filter(SloMetric.org_id == org_id)
    if breached_only:
        q = q.filter(SloMetric.breached.is_(True))
    return q.order_by(SloMetric.created_at.desc()).all()


@router.patch(
    "/admin/orgs/{org_id}/slo/{slo_id}",
    response_model=SloMetricSchema,
    dependencies=[Depends(_require_admin)],
)
def update_slo_measurement(
    org_id: str,
    slo_id: str,
    body: SloMetricUpdate,
    db: Session = Depends(get_db),
):
    """Record a new measurement against an SLO (publish from telemetry collector)."""
    metric = (
        db.query(SloMetric)
        .filter(SloMetric.id == slo_id, SloMetric.org_id == org_id)
        .first()
    )
    if not metric:
        raise HTTPException(status_code=404, detail="SLO metric not found")

    if body.current_p95_ms is not None:
        metric.current_p95_ms = body.current_p95_ms
        metric.breached = body.current_p95_ms > metric.threshold_ms
    if body.error_budget_pct is not None:
        metric.error_budget_pct = body.error_budget_pct
    if body.burn_rate is not None:
        metric.burn_rate = body.burn_rate
    if body.breached is not None:
        metric.breached = body.breached

    metric.measured_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(metric)
    return metric


# ---------------------------------------------------------------------------
# Cost telemetry
# ---------------------------------------------------------------------------

@router.post(
    "/admin/orgs/{org_id}/cost-telemetry",
    response_model=TenantCostLedgerSchema,
    status_code=201,
    dependencies=[Depends(_require_admin)],
)
def record_period_costs(
    org_id: str,
    body: TenantCostLedgerCreate,
    db: Session = Depends(get_db),
):
    """Record period-level cost telemetry for a tenant."""
    total = (
        body.pipeline_cost_usd
        + body.compute_cost_usd
        + body.storage_cost_usd
        + body.llm_cost_usd
    )
    entry = TenantCostLedger(
        org_id=org_id,
        period_start=body.period_start,
        period_end=body.period_end,
        pipeline_cost_usd=body.pipeline_cost_usd,
        compute_cost_usd=body.compute_cost_usd,
        storage_cost_usd=body.storage_cost_usd,
        llm_tokens_used=body.llm_tokens_used,
        llm_cost_usd=body.llm_cost_usd,
        total_cost_usd=total,
        budget_limit_usd=body.budget_limit_usd,
        budget_alert_pct=body.budget_alert_pct,
        notes=body.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get(
    "/admin/orgs/{org_id}/cost-telemetry",
    response_model=List[TenantCostLedgerSchema],
    dependencies=[Depends(_require_admin)],
)
def get_cost_telemetry(
    org_id: str,
    limit: int = Query(12, ge=1, le=120),
    db: Session = Depends(get_db),
):
    """Return cost ledger entries for a tenant, newest first."""
    return (
        db.query(TenantCostLedger)
        .filter(TenantCostLedger.org_id == org_id)
        .order_by(TenantCostLedger.period_start.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/admin/orgs/{org_id}/cost-telemetry/alert-check",
    dependencies=[Depends(_require_admin)],
)
def cost_alert_check(org_id: str, db: Session = Depends(get_db)):
    """Return whether the most recent period has exceeded the budget alert threshold."""
    entry: Optional[TenantCostLedger] = (
        db.query(TenantCostLedger)
        .filter(TenantCostLedger.org_id == org_id)
        .order_by(TenantCostLedger.period_start.desc())
        .first()
    )
    if not entry:
        return {"alert": False, "reason": "no_cost_data"}

    if not entry.budget_limit_usd or entry.budget_limit_usd <= 0:
        return {"alert": False, "reason": "no_budget_limit_set"}

    pct_used = (entry.total_cost_usd / entry.budget_limit_usd) * 100.0
    alert = pct_used >= entry.budget_alert_pct
    return {
        "alert": alert,
        "pct_used": round(pct_used, 2),
        "budget_alert_pct": entry.budget_alert_pct,
        "total_cost_usd": entry.total_cost_usd,
        "budget_limit_usd": entry.budget_limit_usd,
        "period_start": entry.period_start.isoformat(),
        "period_end": entry.period_end.isoformat(),
    }
