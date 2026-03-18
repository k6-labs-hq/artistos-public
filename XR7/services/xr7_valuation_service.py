from __future__ import annotations

import json
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.xr7_royalty import XR7CatalogValuationSnapshot, XR7RecoveryForecast, XR7Track, XR7UsageEvent


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_catalog_health(db: Session, *, tenant_id: str, artist_id: str) -> dict[str, object]:
    tracks = db.query(XR7Track).filter(XR7Track.tenant_id == tenant_id, XR7Track.artist_id == artist_id).all()
    if not tracks:
        return {
            "score": 0.0,
            "components": {
                "metadata_quality": 0.0,
                "ugc_coverage": 0.0,
                "catalog_completeness": 0.0,
            },
            "top_actions": ["ingest_catalog", "connect_platforms"],
        }

    metadata_quality = sum(float(t.metadata_quality_score) for t in tracks) / len(tracks)
    ugc_coverage = sum(float(t.ugc_platform_coverage_score) for t in tracks) / len(tracks)
    completeness = min(1.0, sum(1 for t in tracks if t.isrc) / max(1, len(tracks)))

    score = round((0.45 * metadata_quality) + (0.25 * ugc_coverage) + (0.30 * completeness), 4)
    return {
        "score": score,
        "components": {
            "metadata_quality": round(metadata_quality, 4),
            "ugc_coverage": round(ugc_coverage, 4),
            "catalog_completeness": round(completeness, 4),
        },
        "top_actions": [
            "apply_metadata_repairs",
            "link_unmatched_works",
            "connect_ugc_sources",
        ],
    }


def get_or_create_valuation_snapshot(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    as_of: date,
) -> dict[str, object]:
    existing = (
        db.query(XR7CatalogValuationSnapshot)
        .filter(
            XR7CatalogValuationSnapshot.tenant_id == tenant_id,
            XR7CatalogValuationSnapshot.artist_id == artist_id,
            XR7CatalogValuationSnapshot.as_of_date == as_of,
        )
        .first()
    )
    if existing:
        return {
            "id": existing.id,
            "as_of": str(existing.as_of_date),
            "baseline_value": existing.baseline_value,
            "corrected_value": existing.corrected_value,
            "upside_value": existing.upside_value,
            "confidence_interval": [existing.confidence_interval_low, existing.confidence_interval_high],
            "assumptions": json.loads(existing.assumptions_json or "{}"),
        }

    usage = db.query(XR7UsageEvent).filter(XR7UsageEvent.tenant_id == tenant_id, XR7UsageEvent.artist_id == artist_id).all()
    baseline = round(sum(float(u.monetization_estimate or 0.0) for u in usage), 2)
    corrected = round(baseline * 1.17, 2)
    upside = round(corrected - baseline, 2)

    snap = XR7CatalogValuationSnapshot(
        tenant_id=tenant_id,
        artist_id=artist_id,
        as_of_date=as_of,
        baseline_value=baseline,
        corrected_value=corrected,
        upside_value=upside,
        confidence_interval_low=round(corrected * 0.9, 2),
        confidence_interval_high=round(corrected * 1.1, 2),
        assumptions_json=json.dumps({"model": "xr7_valuation_v1", "base_usage_events": len(usage)}, sort_keys=True),
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)

    return {
        "id": snap.id,
        "as_of": str(snap.as_of_date),
        "baseline_value": snap.baseline_value,
        "corrected_value": snap.corrected_value,
        "upside_value": snap.upside_value,
        "confidence_interval": [snap.confidence_interval_low, snap.confidence_interval_high],
        "assumptions": json.loads(snap.assumptions_json or "{}"),
    }


def forecast_recovery(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    horizon_days: int,
    scenario_overrides: dict[str, object] | None,
) -> dict[str, object]:
    usage = db.query(XR7UsageEvent).filter(XR7UsageEvent.tenant_id == tenant_id, XR7UsageEvent.artist_id == artist_id).all()
    baseline_month = sum(float(u.monetization_estimate or 0.0) for u in usage)
    base_multiplier = {30: 1.0, 90: 2.6, 365: 9.5}.get(horizon_days, max(1.0, horizon_days / 30.0))
    override_factor = float((scenario_overrides or {}).get("uplift_factor", 1.0))
    forecast_amount = round(baseline_month * base_multiplier * override_factor, 2)

    rec = XR7RecoveryForecast(
        tenant_id=tenant_id,
        artist_id=artist_id,
        scope_type="artist",
        scope_id=artist_id,
        forecast_horizon_days=horizon_days,
        forecast_amount=forecast_amount,
        confidence_interval_json=json.dumps(
            {
                "low": round(forecast_amount * 0.85, 2),
                "high": round(forecast_amount * 1.15, 2),
            },
            sort_keys=True,
        ),
        model_version="xr7_forecast_v1",
        feature_snapshot_ref=f"usage_events:{len(usage)}",
    )
    db.add(rec)
    db.commit()

    return {
        "forecast_amount": forecast_amount,
        "confidence_interval": [round(forecast_amount * 0.85, 2), round(forecast_amount * 1.15, 2)],
        "recommended_actions": [
            "prioritize_high_confidence_ugc_cases",
            "apply_metadata_repairs",
            "run_reconciliation_weekly",
        ],
    }


def run_simulation(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    scenarios: list[dict[str, object]],
) -> dict[str, object]:
    _ = db, tenant_id, artist_id
    results: list[dict[str, object]] = []
    for idx, scenario in enumerate(scenarios):
        label = str(scenario.get("label") or f"scenario_{idx + 1}")
        base = float(scenario.get("base", 1000.0))
        rate_delta = float(scenario.get("rate_delta", 0.0))
        territory_uplift = float(scenario.get("territory_uplift", 0.0))
        simulated = round(base * (1 + rate_delta + territory_uplift), 2)
        results.append(
            {
                "label": label,
                "forecast_amount": simulated,
                "confidence_interval": [round(simulated * 0.9, 2), round(simulated * 1.1, 2)],
            }
        )

    return {"scenarios": results, "generated_at": _now().isoformat()}
