from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.agents.orchestrator import run_tvfilm_vertical_orchestra_sync
from XR7.api.deps import get_artist_or_404
from XR7.models.anomaly import (
    Anomaly,
    AnomalyStatus,
    BlackBoxExpirationSchema,
    RecoverabilityClassificationSchema,
)
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.statement import Statement
from XR7.models.tvfilm_portfolio_job import TVFilmPortfolioJob, TVFilmPortfolioJobStatus
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.services.branding import inject_branding_metadata
from XR7.services.tvfilm_compensation_engine import calculate_expected_compensation
from XR7.services.tvfilm_evidence_packets import (
    build_tvfilm_bulk_export_zip,
    build_tvfilm_evidence_packet,
    build_tvfilm_packet_pdf,
    build_tvfilm_packet_zip,
)
from XR7.services.tvfilm_vertical import (
    AGENCY_NAMES,
    ANOMALY_RULE_CATALOG,
    ANOMALY_TO_CATEGORY,
    EVIDENCE_PACKET_TEMPLATES,
    TVFILM_ROLE_OPTIONS,
    forecast_from_amounts,
    infer_anomaly_subtype,
    list_all_anomaly_rules,
    parse_statement_preview,
    portfolio_rollup,
    severity_for_delta,
    to_json,
)

router = APIRouter(prefix="/tvfilm", tags=["tvfilm"])


class TVFilmClaimDraftRequest(BaseModel):
    anomaly_ids: list[str] = Field(default_factory=list)
    union_template: str = "SAG-AFTRA"


class TVFilmBulkClaimDraftRequest(BaseModel):
    anomaly_ids: list[str] = Field(default_factory=list)
    group_by_template: bool = True


class TVFilmForecastRequest(BaseModel):
    anomaly_ids: list[str] = Field(default_factory=list)
    confidence_override: float | None = None


class TVFilmPortfolioAnalysisRequest(BaseModel):
    organization_name: str
    entity_type: str
    records: list[dict[str, Any]]
    uploaded_filename: str | None = None


class TVFilmTrustExplainRequest(BaseModel):
    role: str
    agency_mode: bool = False


class TVFilmBulkExportRequest(BaseModel):
    claim_ids: list[str] = Field(default_factory=list)


class TVFilmRecoverabilityPreviewItem(BaseModel):
    subtype: str
    estimated_recoverable: float
    union: str | None = None
    platform: str | None = None
    black_box_expiration: BlackBoxExpirationSchema
    recoverability: RecoverabilityClassificationSchema
    legal_basis: str
    claim_draft_allowed: bool


class TVFilmScanAnomaliesResponse(BaseModel):
    artist_id: str
    signals_scanned: int
    anomalies_created: int
    anomaly_rule_catalog: dict[str, Any]
    recoverability_summary: dict[str, int]
    recoverability_preview: list[TVFilmRecoverabilityPreviewItem]


class TVFilmDashboardRecoverabilityBucket(BaseModel):
    count: int
    amount: float


class TVFilmDashboardResponse(BaseModel):
    artist_id: str
    sections: dict[str, Any]
    trust_layer: dict[str, Any]
    role_breakdown: dict[str, float]


class TVFilmTrustExplainResponse(BaseModel):
    role: str
    agency_mode: bool
    logo_state: str
    what_xr7_is_doing_now: list[str]
    plain_language: str
    recoverability_explainer: dict[str, Any]
    agency_language: str | None = None


def _artist_or_404(db: Session, artist_id: str) -> Artist:
    artist = get_artist_or_404(artist_id, db)
    return artist


def _build_claim_packet(db: Session, claim: Claim) -> dict[str, Any]:
    artist = _artist_or_404(db, claim.artist_id)
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found for claim")
    feature_snapshot = json.loads(anomaly.feature_snapshot or "{}")
    evidence = claim.evidence or {}
    template = str(evidence.get("template") or "STUDIO_GENERIC")
    return build_tvfilm_evidence_packet(
        artist=artist,
        claim=claim,
        anomaly=anomaly,
        feature_snapshot=feature_snapshot,
        template=template,
    )


@router.get("/roles/options")
def tvfilm_role_options():
    return {
        "role_options": TVFILM_ROLE_OPTIONS,
        "agency_examples": AGENCY_NAMES,
        "enterprise_supported_entities": [
            "Talent Agency",
            "Management Company",
            "Production Company",
            "Union",
            "Law Firm",
            "Accounting Firm",
        ],
    }


@router.get("/ingestion/formats")
def tvfilm_ingestion_formats():
    return {
        "supported_statement_groups": {
            "residuals_and_royalties": [
                "SAG-AFTRA residuals",
                "WGA residuals",
                "DGA residuals",
                "IATSE residuals",
                "AFM/AFTRA music-in-film residuals",
                "Studio residuals (Disney/WB/NBCU/Paramount/Sony)",
                "Streaming residuals (Netflix/Hulu/Amazon/Apple TV+/Max)",
                "Foreign residuals",
            ],
            "production_payments": [
                "Call sheets + payroll exports",
                "Timecard CSVs",
                "Deal memo summaries",
                "Production payout reports",
                "Episodic payment breakdowns",
                "Feature payment breakdowns",
            ],
            "licensing_and_distribution": [
                "International distribution revenue",
                "Syndication revenue",
                "Home video revenue",
                "FAST/AVOD/SVOD",
                "Airline licensing",
                "Educational licensing",
            ],
            "ugc_social_clips": [
                "YouTube Content ID claims",
                "TikTok/IG Reels monetization",
                "Clip licensing payouts",
                "Viral reuse detections",
            ],
        },
        "detection": {
            "auto_detect_format_from_headers": True,
            "auto_repair_malformed_fields": True,
            "auto_normalize_episode_season_production_ids": True,
            "auto_link_payments_to_roles": True,
        },
    }


@router.post("/ingestion/preview")
async def tvfilm_ingestion_preview(file: UploadFile = File(...)):
    raw = await file.read()
    preview = parse_statement_preview(raw, filename=file.filename or "upload.csv")
    return {
        "statement_type": preview.statement_type,
        "rows_detected": len(preview.normalized_rows),
        "repaired_fields": preview.repaired_fields,
        "warnings": preview.warnings,
        "sample_rows": preview.normalized_rows[:20],
    }


@router.post("/artists/{artist_id}/ingestion/commit")
async def tvfilm_ingestion_commit(
    artist_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    artist = _artist_or_404(db, artist_id)
    raw = await file.read()
    file_hash = hashlib.sha256(raw).hexdigest()
    preview = parse_statement_preview(raw, filename=file.filename or "upload.csv")

    statement = Statement(
        artist_id=artist_id,
        filename=file.filename or "tvfilm_statement.csv",
        file_hash=file_hash,
        format_detected=preview.statement_type,
        row_count=len(preview.normalized_rows),
        events_created=len(preview.normalized_rows),
        payments_created=len(preview.normalized_rows),
        skipped_rows=0,
        status="PROCESSED",
        error_summary=("; ".join(preview.warnings) if preview.warnings else None),
        ingestion_metadata_json=to_json(
            {
                "vertical": "TV_FILM",
                "detected_type": preview.statement_type,
                "repaired_fields": preview.repaired_fields,
                "rows": preview.normalized_rows,
            }
        ),
    )
    db.add(statement)

    if not artist.primary_vertical:
        artist.primary_vertical = "TV_FILM"
    if not artist.tvfilm_role and artist.role:
        artist.tvfilm_role = artist.role

    db.commit()
    db.refresh(statement)

    return inject_branding_metadata(
        db,
        {
            "statement_id": statement.id,
            "artist_id": artist_id,
            "format_detected": statement.format_detected,
            "rows_committed": statement.row_count,
            "automation": {
                "auto_repair_applied": bool(preview.repaired_fields),
                "episode_season_normalization": True,
                "production_id_normalization": True,
                "role_linking": True,
                "union_studio_rule_engine": True,
            },
        },
    )


@router.get("/artists/{artist_id}/calculation-audit")
def tvfilm_calculation_audit(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(db, artist_id)
    statements = (
        db.query(Statement)
        .filter(Statement.artist_id == artist_id)
        .order_by(Statement.uploaded_at.desc())
        .limit(5)
        .all()
    )
    if not statements:
        raise HTTPException(status_code=400, detail="No statements found for artist")

    calculations: list[dict[str, Any]] = []
    for statement in statements:
        payload = json.loads(statement.ingestion_metadata_json or "{}")
        for row in payload.get("rows") or []:
            calculation = calculate_expected_compensation(row)
            calculations.append(
                {
                    "production_id": row.get("production_id"),
                    "role": row.get("role"),
                    "union": row.get("union"),
                    "platform": row.get("platform"),
                    "distribution_window": row.get("distribution_window"),
                    "expected_amount": calculation["expected_amount"],
                    "actual_amount": calculation["actual_amount"],
                    "delta": calculation["delta"],
                    "confidence": calculation["confidence"],
                    "recommended_template": calculation["recommended_template"],
                    "notes": calculation["calculation_notes"],
                }
            )

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "rows_audited": len(calculations),
            "calculation_profiles": calculations,
        },
    )


@router.post("/artists/{artist_id}/anomalies/scan", response_model=TVFilmScanAnomaliesResponse)
def tvfilm_scan_anomalies(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(db, artist_id)
    statements = (
        db.query(Statement)
        .filter(Statement.artist_id == artist_id)
        .order_by(Statement.uploaded_at.desc())
        .limit(10)
        .all()
    )
    if not statements:
        raise HTTPException(status_code=400, detail="No statements found for artist")

    created = 0
    scanned_rows = 0
    recoverability_counts: dict[str, int] = {}
    recoverability_preview: list[dict[str, Any]] = []

    for st in statements:
        payload = json.loads(st.ingestion_metadata_json or "{}")
        if str(payload.get("vertical") or "").upper() != "TV_FILM":
            continue
        rows = payload.get("rows") or []
        for row in rows:
            scanned_rows += 1
            anomaly_group, subtype = infer_anomaly_subtype(row)
            estimated = max(float(row.get("delta") or 0.0), 0.0)
            if estimated <= 0.0 and subtype not in {
                "MISSING_ROLE_METADATA",
                "MISSING_CLIP_LICENSING_PAYOUTS",
            }:
                continue

            severity = severity_for_delta(estimated)
            confidence = float(
                row.get("calculation_confidence") or 0.78
                if estimated == 0
                else min(0.98, 0.72 + (estimated / 100000.0))
            )

            db.add(
                Anomaly(
                    artist_id=artist_id,
                    category=ANOMALY_TO_CATEGORY[anomaly_group],
                    subtype=subtype,
                    severity=severity,
                    expected_amount=float(row.get("expected_amount") or 0.0),
                    actual_amount=float(row.get("amount_paid") or 0.0),
                    estimated_recoverable=estimated,
                    confidence_score=round(confidence, 4),
                    status=AnomalyStatus.OPEN,
                    territory=row.get("market"),
                    description=f"TV/Film anomaly detected for production {row.get('production_id')}",
                    feature_snapshot=to_json(
                        {
                            "vertical": "TV_FILM",
                            "production_id": row.get("production_id"),
                            "season": row.get("season"),
                            "episode": row.get("episode"),
                            "role": row.get("role"),
                            "distribution_window": row.get("distribution_window"),
                            "market": row.get("market"),
                            "platform": row.get("platform"),
                            "recommended_template": row.get("recommended_template"),
                            "calculation_notes": row.get("calculation_notes") or [],
                            "calculation_breakdown": row.get("calculation_breakdown") or {},
                        }
                    ),
                )
            )

            recoverability = build_recoverability_payload(
                {
                    "artist_id": artist_id,
                    "category": str(ANOMALY_TO_CATEGORY[anomaly_group]),
                    "subtype": subtype,
                    "severity": str(severity),
                    "estimated_recoverable": estimated,
                    "confidence_score": round(confidence, 4),
                    "territory": row.get("market"),
                    "description": f"TV/Film anomaly detected for production {row.get('production_id')}",
                    "event_date": row.get("statement_period_end") or row.get("event_date"),
                    "feature_snapshot": {
                        "union": row.get("union"),
                        "platform": row.get("platform"),
                        "production_id": row.get("production_id"),
                    },
                }
            )
            recoverability_class = str(
                (recoverability.get("recoverability") or {}).get("recoverability_class")
                or "Unknown"
            )
            recoverability_counts[recoverability_class] = (
                recoverability_counts.get(recoverability_class, 0) + 1
            )
            if len(recoverability_preview) < 25:
                recoverability_preview.append(
                    {
                        "subtype": subtype,
                        "estimated_recoverable": round(estimated, 2),
                        "union": row.get("union"),
                        "platform": row.get("platform"),
                        **recoverability,
                    }
                )
            created += 1

    db.commit()
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "signals_scanned": scanned_rows,
            "anomalies_created": created,
            "anomaly_rule_catalog": ANOMALY_RULE_CATALOG,
            "recoverability_summary": recoverability_counts,
            "recoverability_preview": recoverability_preview,
        },
    )


@router.post("/artists/{artist_id}/claims/draft")
def tvfilm_draft_claims(
    artist_id: str, payload: TVFilmClaimDraftRequest, db: Session = Depends(get_db)
):
    _artist_or_404(db, artist_id)

    if payload.union_template not in EVIDENCE_PACKET_TEMPLATES:
        raise HTTPException(status_code=400, detail="Unsupported union/studio evidence template")

    anomalies_q = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if payload.anomaly_ids:
        anomalies_q = anomalies_q.filter(Anomaly.id.in_(payload.anomaly_ids))
    anomalies = anomalies_q.all()

    if not anomalies:
        raise HTTPException(status_code=400, detail="No anomalies available to draft claims")

    drafted_ids: list[str] = []
    skipped: list[dict[str, Any]] = []
    for anomaly in anomalies:
        recoverability_payload = build_recoverability_payload(
            {
                "id": anomaly.id,
                "artist_id": anomaly.artist_id,
                "category": str(anomaly.category),
                "subtype": anomaly.subtype,
                "severity": str(anomaly.severity),
                "estimated_recoverable": anomaly.estimated_recoverable,
                "confidence_score": anomaly.confidence_score,
                "time_window_start": anomaly.time_window_start,
                "time_window_end": anomaly.time_window_end,
                "description": anomaly.description,
                "feature_snapshot": anomaly.feature_snapshot,
                "created_at": anomaly.created_at,
            }
        )
        if not bool(recoverability_payload.get("claim_draft_allowed")):
            skipped.append(
                {
                    "anomaly_id": anomaly.id,
                    "recoverability_class": (
                        recoverability_payload.get("recoverability") or {}
                    ).get("recoverability_class"),
                    "rule_applied": (recoverability_payload.get("black_box_expiration") or {}).get(
                        "rule_applied"
                    ),
                }
            )
            continue

        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type=f"TV_FILM::{anomaly.subtype}",
            status=ClaimStatus.PREPARED,
            recovered_amount=anomaly.estimated_recoverable,
            currency="USD",
            payer_name="Pending Counterparty",
            evidence={
                "template": payload.union_template,
                "required_sections": EVIDENCE_PACKET_TEMPLATES[payload.union_template][
                    "required_sections"
                ],
                "anomaly_subtype": anomaly.subtype,
                "evidence_hashes": [
                    hashlib.sha256(
                        f"{artist_id}:{anomaly.id}:{payload.union_template}".encode("utf-8")
                    ).hexdigest()
                ],
            },
            anomaly_report={
                "vertical": "TV_FILM",
                "category": str(anomaly.category),
                "subtype": anomaly.subtype,
                "confidence": anomaly.confidence_score,
            },
        )
        db.add(claim)
        db.flush()
        drafted_ids.append(claim.id)

    db.commit()
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claims_drafted": len(drafted_ids),
            "claim_ids": drafted_ids,
            "evidence_template": payload.union_template,
            "skipped": skipped,
        },
    )


@router.post("/artists/{artist_id}/claims/bulk-draft")
def tvfilm_bulk_draft_claims(
    artist_id: str, payload: TVFilmBulkClaimDraftRequest, db: Session = Depends(get_db)
):
    _artist_or_404(db, artist_id)

    anomalies_q = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if payload.anomaly_ids:
        anomalies_q = anomalies_q.filter(Anomaly.id.in_(payload.anomaly_ids))
    anomalies = anomalies_q.all()
    if not anomalies:
        raise HTTPException(status_code=400, detail="No anomalies available to draft claims")

    drafted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for anomaly in anomalies:
        recoverability_payload = build_recoverability_payload(
            {
                "id": anomaly.id,
                "artist_id": anomaly.artist_id,
                "category": str(anomaly.category),
                "subtype": anomaly.subtype,
                "severity": str(anomaly.severity),
                "estimated_recoverable": anomaly.estimated_recoverable,
                "confidence_score": anomaly.confidence_score,
                "time_window_start": anomaly.time_window_start,
                "time_window_end": anomaly.time_window_end,
                "description": anomaly.description,
                "feature_snapshot": anomaly.feature_snapshot,
                "created_at": anomaly.created_at,
            }
        )
        if not bool(recoverability_payload.get("claim_draft_allowed")):
            skipped.append(
                {
                    "anomaly_id": anomaly.id,
                    "recoverability_class": (
                        recoverability_payload.get("recoverability") or {}
                    ).get("recoverability_class"),
                }
            )
            continue

        feature_snapshot = json.loads(anomaly.feature_snapshot or "{}")
        template = str(feature_snapshot.get("recommended_template") or "STUDIO_GENERIC")
        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type=f"TV_FILM::{anomaly.subtype}",
            status=ClaimStatus.PREPARED,
            recovered_amount=anomaly.estimated_recoverable,
            currency="USD",
            payer_name=str(feature_snapshot.get("platform") or "Pending Counterparty"),
            evidence={
                "template": template,
                "required_sections": EVIDENCE_PACKET_TEMPLATES.get(
                    template, EVIDENCE_PACKET_TEMPLATES["STUDIO_GENERIC"]
                )["required_sections"],
                "anomaly_subtype": anomaly.subtype,
                "evidence_hashes": [
                    hashlib.sha256(
                        f"bulk:{artist_id}:{anomaly.id}:{template}".encode("utf-8")
                    ).hexdigest()
                ],
            },
        )
        db.add(claim)
        db.flush()
        drafted.append({"claim_id": claim.id, "template": template, "anomaly_id": anomaly.id})

    db.commit()

    template_groups: dict[str, int] = {}
    for item in drafted:
        template_groups[item["template"]] = template_groups.get(item["template"], 0) + 1

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claims_drafted": len(drafted),
            "drafts": drafted,
            "template_groups": template_groups,
            "skipped": skipped,
        },
    )


@router.post("/artists/{artist_id}/forecast")
def tvfilm_forecast(artist_id: str, payload: TVFilmForecastRequest, db: Session = Depends(get_db)):
    _artist_or_404(db, artist_id)

    anomalies_q = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if payload.anomaly_ids:
        anomalies_q = anomalies_q.filter(Anomaly.id.in_(payload.anomaly_ids))
    anomalies = anomalies_q.all()

    if not anomalies:
        raise HTTPException(status_code=400, detail="No anomalies available for forecasting")

    total = sum(float(a.estimated_recoverable or 0.0) for a in anomalies)
    confidence = (
        payload.confidence_override
        if payload.confidence_override is not None
        else (sum(float(a.confidence_score or 0.0) for a in anomalies) / max(len(anomalies), 1))
    )

    forecast = forecast_from_amounts(base_amount=total, confidence=confidence)

    by_role: dict[str, float] = {}
    by_production: dict[str, float] = {}
    by_platform: dict[str, float] = {}

    for anomaly in anomalies:
        snap = json.loads(anomaly.feature_snapshot or "{}")
        role = str(snap.get("role") or "Unspecified")
        production_id = str(snap.get("production_id") or "UNKNOWN")
        platform = str(snap.get("platform") or "Unspecified")
        value = float(anomaly.estimated_recoverable or 0.0)
        by_role[role] = round(by_role.get(role, 0.0) + value, 2)
        by_production[production_id] = round(by_production.get(production_id, 0.0) + value, 2)
        by_platform[platform] = round(by_platform.get(platform, 0.0) + value, 2)

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "forecast": forecast,
            "inputs": {
                "anomaly_count": len(anomalies),
                "historical_residuals": total,
                "distribution_windows": True,
                "platform_seasonality": True,
                "syndication_cycles": True,
                "foreign_society_lag_factors": True,
                "contract_terms": True,
                "metadata_repairs": True,
            },
            "per_role_forecast": by_role,
            "per_production_forecast": by_production,
            "per_platform_forecast": by_platform,
        },
    )


@router.post("/enterprise/portfolio/analyze")
def tvfilm_enterprise_portfolio_analyze(
    payload: TVFilmPortfolioAnalysisRequest, db: Session = Depends(get_db)
):
    if not payload.records:
        raise HTTPException(status_code=400, detail="Portfolio record list is empty")

    summary = portfolio_rollup(payload.records)
    summary["organization_name"] = payload.organization_name
    summary["entity_type"] = payload.entity_type
    summary["analysis_completed_at"] = datetime.now(timezone.utc).isoformat()

    job = TVFilmPortfolioJob(
        organization_name=payload.organization_name,
        entity_type=payload.entity_type,
        uploaded_filename=payload.uploaded_filename,
        roster_size=len(payload.records),
        status=TVFilmPortfolioJobStatus.COMPLETE,
        summary_json=to_json(summary),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": job.status,
        "summary": summary,
        "bulk_features": {
            "bulk_claim_drafting": True,
            "bulk_evidence_packets": True,
            "bulk_forecasting": True,
            "bulk_metadata_repair": True,
            "historical_backfill": True,
        },
    }


@router.get("/enterprise/portfolio/{job_id}")
def tvfilm_enterprise_portfolio_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(TVFilmPortfolioJob).filter(TVFilmPortfolioJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Portfolio job not found")
    return {
        "job_id": job.id,
        "organization_name": job.organization_name,
        "entity_type": job.entity_type,
        "status": job.status,
        "roster_size": job.roster_size,
        "summary": json.loads(job.summary_json or "{}"),
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }


@router.get("/artists/{artist_id}/dashboard", response_model=TVFilmDashboardResponse)
def tvfilm_dashboard(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(db, artist_id)

    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

    total_residuals = sum(
        float(a.estimated_recoverable or 0.0)
        for a in anomalies
        if "RESIDUAL" in str(a.subtype or "")
    )
    production_payments = sum(
        float(a.estimated_recoverable or 0.0)
        for a in anomalies
        if "OVERTIME" in str(a.subtype or "") or "DAY_RATE" in str(a.subtype or "")
    )
    licensing_distribution = sum(
        float(a.estimated_recoverable or 0.0)
        for a in anomalies
        if "SYNDICATION" in str(a.subtype or "")
        or "DISTRIBUTION" in str(a.subtype or "")
        or "BACKEND" in str(a.subtype or "")
    )
    streaming_reuse = sum(
        float(a.estimated_recoverable or 0.0)
        for a in anomalies
        if "STREAMING" in str(a.subtype or "")
    )
    ugc_clips = sum(
        float(a.estimated_recoverable or 0.0)
        for a in anomalies
        if "CLIP" in str(a.subtype or "")
        or "CONTENT_ID" in str(a.subtype or "")
        or "VIRAL" in str(a.subtype or "")
    )
    metadata_health_total = sum(
        1
        for a in anomalies
        if "MISMATCH" in str(a.subtype or "") or "METADATA" in str(a.subtype or "")
    )

    backend_claims = sum(1 for c in claims if "BACKEND" in str(c.claim_type or ""))

    trust_stream = [
        "Validating union residual schedules",
        "Reconciling platform and studio payout windows",
        "Repairing production IDs and episode-season metadata",
        "Preparing evidence-backed claim packets",
    ]

    role_breakdown: dict[str, float] = {}
    recoverability_by_class: dict[str, dict[str, Any]] = {}
    for anomaly in anomalies:
        snap = json.loads(anomaly.feature_snapshot or "{}")
        role = str(snap.get("role") or "Unspecified")
        role_breakdown[role] = round(
            role_breakdown.get(role, 0.0) + float(anomaly.estimated_recoverable or 0.0), 2
        )

        recoverability = build_recoverability_payload(
            {
                "id": anomaly.id,
                "artist_id": anomaly.artist_id,
                "category": str(anomaly.category),
                "subtype": anomaly.subtype,
                "severity": str(anomaly.severity),
                "estimated_recoverable": anomaly.estimated_recoverable,
                "confidence_score": anomaly.confidence_score,
                "time_window_start": anomaly.time_window_start,
                "time_window_end": anomaly.time_window_end,
                "description": anomaly.description,
                "feature_snapshot": anomaly.feature_snapshot,
                "created_at": anomaly.created_at,
            }
        )
        cls = str(
            (recoverability.get("recoverability") or {}).get("recoverability_class")
            or "Unclassified"
        )
        if cls not in recoverability_by_class:
            recoverability_by_class[cls] = {"count": 0, "amount": 0.0}
        recoverability_by_class[cls]["count"] += 1
        recoverability_by_class[cls]["amount"] = round(
            float(recoverability_by_class[cls]["amount"])
            + float(anomaly.estimated_recoverable or 0.0),
            2,
        )

    recoverable_amount = round(
        sum(
            v["amount"]
            for k, v in recoverability_by_class.items()
            if k != "Expired (Black-Box Redistributed)"
        ),
        2,
    )
    expired_amount = round(
        float(
            (recoverability_by_class.get("Expired (Black-Box Redistributed)") or {}).get("amount")
            or 0.0
        ),
        2,
    )

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "sections": {
                "residuals_discovered": {
                    "value": round(total_residuals, 2),
                    "count": len(anomalies),
                },
                "production_payments": {"value": round(production_payments, 2)},
                "distribution_licensing": {"value": round(licensing_distribution, 2)},
                "streaming_reuse": {"value": round(streaming_reuse, 2)},
                "ugc_clips": {"value": round(ugc_clips, 2)},
                "metadata_health_tvfilm": {
                    "open_issues": metadata_health_total,
                    "status": "healthy" if metadata_health_total < 5 else "at_risk",
                },
                "backend_participation": {"active_claims": backend_claims},
                "agency_portfolio_view": {
                    "available": True,
                    "path": "/tvfilm/enterprise/portfolio/{job_id}",
                },
                "recoverability": {
                    "recoverable_amount": recoverable_amount,
                    "expired_amount": expired_amount,
                    "by_class": recoverability_by_class,
                },
            },
            "trust_layer": {
                "logo_state": "glowing",
                "what_xr7_is_doing_now": trust_stream,
                "recoverability_explainer": {
                    "here_is_what_you_can_still_recover": {
                        "amount": recoverable_amount,
                        "why": "Within claim windows or contract/damages pathways.",
                        "next": "XR7 drafts claims, evidence packets, and negotiation playbooks.",
                    },
                    "here_is_what_expired": {
                        "amount": expired_amount,
                        "why": "Black-box redistribution windows elapsed under society/union rules.",
                        "rule_note": "Examples: ASCAP 2-3 years, MLC 3 years, foreign residual societies 6-18 months.",
                    },
                    "here_is_what_xr7_prevents_going_forward": [
                        "Metadata repair",
                        "Identifier normalization",
                        "Cross-system linking",
                        "Future leakage prevention scoring",
                        "UGC fingerprinting",
                        "Foreign society crosswalks",
                    ],
                },
            },
            "role_breakdown": role_breakdown,
        },
    )


@router.post("/trust/explain", response_model=TVFilmTrustExplainResponse)
def tvfilm_trust_explain(payload: TVFilmTrustExplainRequest):
    role = payload.role.strip() or "TV/Film Professional"
    return {
        "role": role,
        "agency_mode": payload.agency_mode,
        "logo_state": "glowing" if payload.agency_mode else "dimming",
        "what_xr7_is_doing_now": [
            "Normalizing production IDs, episode-season trees, and role credits.",
            "Reconciling residual schedules against statement actuals.",
            "Drafting evidence-backed claims with union/studio templates.",
            "Forecasting 30/60/90/180-day recovery with confidence bands.",
        ],
        "plain_language": f"XR7 is checking every payment line tied to your {role} work, showing exactly where money is missing, why it is missing, and what claim action is being prepared.",
        "recoverability_explainer": {
            "what_you_can_still_recover": "Within claim window anomalies, plus contract and damages pathways.",
            "what_expired": "Black-box redistributed unmatched funds after payer/society windows.",
            "why": [
                "ASCAP redistributes unmatched royalties after 2-3 years.",
                "MLC redistributes unmatched digital mechanicals after 3 years.",
                "Foreign societies often redistribute after 6-18 months.",
            ],
            "what_xr7_prevents_going_forward": [
                "Metadata repair",
                "Identifier normalization",
                "Cross-system linking",
                "Future leakage prevention",
                "UGC fingerprinting",
                "Foreign society crosswalks",
            ],
        },
        "agency_language": (
            "XR7 is running portfolio-scale reconciliation across roster, production, union, and platform dimensions with audit-grade evidence hashes."
            if payload.agency_mode
            else None
        ),
    }


@router.post("/artists/{artist_id}/agents/run")
def run_tvfilm_agents(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(db, artist_id)
    state = run_tvfilm_vertical_orchestra_sync(artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "run_id": state.get("run_id"),
            "current_step": state.get("current_step"),
            "confidence_scores": state.get("confidence_scores", {}),
            "evidence_hash_count": len(state.get("evidence_hashes") or []),
            "agent_activity": state.get("agent_activity", []),
        },
    )


@router.get("/claims/{claim_id}/evidence/export")
def tvfilm_export_evidence_packet(
    claim_id: str,
    format: str = Query(default="zip", pattern="^(zip|pdf|json)$"),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    packet = _build_claim_packet(db, claim)

    if format == "json":
        return packet
    if format == "pdf":
        return Response(
            content=build_tvfilm_packet_pdf(packet),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="tvfilm_evidence_{claim_id}.pdf"'
            },
        )

    return Response(
        content=build_tvfilm_packet_zip(packet),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="tvfilm_evidence_{claim_id}.zip"'},
    )


@router.post("/artists/{artist_id}/claims/bulk-export")
def tvfilm_bulk_export_claims(
    artist_id: str, payload: TVFilmBulkExportRequest, db: Session = Depends(get_db)
):
    _artist_or_404(db, artist_id)

    claims_q = db.query(Claim).filter(Claim.artist_id == artist_id)
    if payload.claim_ids:
        claims_q = claims_q.filter(Claim.id.in_(payload.claim_ids))
    claims = claims_q.all()
    if not claims:
        raise HTTPException(status_code=400, detail="No claims available for bulk export")

    items = []
    for claim in claims:
        items.append({"claim_id": claim.id, "packet": _build_claim_packet(db, claim)})

    return Response(
        content=build_tvfilm_bulk_export_zip(items),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="tvfilm_bulk_export_{artist_id}.zip"'
        },
    )


@router.get("/catalogs/anomaly-rules")
def tvfilm_anomaly_rule_catalog():
    return {
        "rules": ANOMALY_RULE_CATALOG,
        "flat_rule_list": list_all_anomaly_rules(),
    }


@router.get("/catalogs/evidence-templates")
def tvfilm_evidence_templates():
    return {
        "templates": EVIDENCE_PACKET_TEMPLATES,
    }
