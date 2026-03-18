"""Pillar 8 — Class-action evidence signals (admin + artist-facing)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_auth_payload, require_admin
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.services.class_action_aggregator import aggregate_class_action_signals, get_active_signals

router = APIRouter(tags=["class_action"])


@router.post("/admin/class-action/aggregate")
def run_class_action_aggregation(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
) -> dict:
    """Re-run the class-action signal aggregator across all open anomalies.

    Requires admin role. Returns created/updated signal records.
    """
    signals = aggregate_class_action_signals(db)
    return inject_branding_metadata(db, {
        "signals_upserted": len(signals),
        "signals": signals,
    })


@router.get("/admin/class-action/signals")
def list_class_action_signals(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
) -> dict:
    """Return all active class-action evidence signals."""
    signals = get_active_signals(db)
    return inject_branding_metadata(db, {
        "count": len(signals),
        "signals": signals,
    })
