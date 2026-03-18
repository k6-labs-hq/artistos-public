from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.xr7_valuation_service import (
    forecast_recovery,
    get_catalog_health,
    get_or_create_valuation_snapshot,
    run_simulation,
)

router = APIRouter(tags=["xr7-valuation"])


class ForecastRequest(BaseModel):
    tenant_id: str = "default"
    horizon_days: int = 90
    scenario_overrides: dict[str, object] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    tenant_id: str = "default"
    scenarios: list[dict[str, object]] = Field(default_factory=list)


@router.get("/artists/{artist_id}/xr7/catalog/health")
def catalog_health(artist_id: str, tenant_id: str = "default", db: Session = Depends(get_db)):
    return get_catalog_health(db, tenant_id=tenant_id, artist_id=artist_id)


@router.get("/artists/{artist_id}/xr7/valuation/snapshot")
def valuation_snapshot(
    artist_id: str,
    tenant_id: str = "default",
    as_of: date | None = None,
    db: Session = Depends(get_db),
):
    return get_or_create_valuation_snapshot(
        db,
        tenant_id=tenant_id,
        artist_id=artist_id,
        as_of=as_of or date.today(),
    )


@router.post("/artists/{artist_id}/xr7/forecast/recovery")
def recovery_forecast(artist_id: str, payload: ForecastRequest, db: Session = Depends(get_db)):
    return forecast_recovery(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        horizon_days=payload.horizon_days,
        scenario_overrides=payload.scenario_overrides,
    )


@router.post("/artists/{artist_id}/xr7/simulations/what-if")
def simulation(artist_id: str, payload: SimulationRequest, db: Session = Depends(get_db)):
    return run_simulation(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        scenarios=payload.scenarios,
    )
