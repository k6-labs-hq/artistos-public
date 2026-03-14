from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.anomaly.variance_detection_engine import run_variance_scan
from XR7.graph.catalog_graph_builder import build_catalog_graph
from XR7.ingestion.fetchers import get_fetcher
from XR7.ingestion.file_ingestion_pipeline import FileIngestionPipeline
from XR7.ingestion.missing_data_detector import detect_missing_data
from XR7.ingestion.parser_engine import get_statement_parser
from XR7.ingestion.sync_jobs import enqueue_sync_job, run_due_sync_jobs, run_sync_job, run_sync_job_with_session
from XR7.ml.auto_inference_engine import infer_catalog_relationships
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.catalog_confirmation import CatalogConfirmation, CatalogConfirmationSchema
from XR7.models.claim import Claim
from XR7.models.event import Event
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntrySchema
from XR7.models.oauth_connector import ConnectorAccountLink
from XR7.models.parser_plugin import ParserPlugin, ParserPluginSchema
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.models.sync_job import SyncJob, SyncJobSchema
from XR7.models.terms_acceptance import TermsAcceptance
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.recovery.recovery_automation_engine import automate_recovery
from XR7.services.parser_plugins import ParserPluginError, parse_with_plugin
from XR7.services.workflow_orchestrator import XR7WorkflowService

router = APIRouter(tags=["onboarding"])

_PERMISSIONS_UI_PATH = Path(__file__).resolve().parents[2] / "widget" / "permissions_dashboard.html"


class CatalogConfirmRequest(BaseModel):
    work_id: str
    ownership_confirmed: str = "confirmed"
    splits_confirmed: str = "confirmed"
    publisher_confirmed: str = "confirmed"
    admin_confirmed: str = "confirmed"
    correction_notes: str | None = None


class VarianceScanRequest(BaseModel):
    rows: list[dict[str, Any]]


class ParserPluginUpsertRequest(BaseModel):
    parser_type: str
    plugin_name: str
    plugin_entrypoint: str
    plugin_signature: str | None = None
    enabled: bool = True


class SyncJobCreateRequest(BaseModel):
    integration: str
    max_attempts: int = 3
    payload: dict[str, Any] | None = None
    run_async: bool = True
    queue_backend: str = "background"


class WorkflowRunRequest(BaseModel):
    async_run: bool = False


def _artist_or_404(artist_id: str, db: Session) -> Artist:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.get("/artists/{artist_id}/onboarding/status")
def onboarding_status(artist_id: str, db: Session = Depends(get_db)):
    artist = _artist_or_404(artist_id, db)

    terms_accepted = (
        db.query(TermsAcceptance.id)
        .filter(TermsAcceptance.artist_id == artist_id)
        .first()
        is not None
    )
    statement_count = db.query(func.count(Statement.id)).filter(Statement.artist_id == artist_id).scalar() or 0
    connector_count = (
        db.query(func.count(ConnectorAccountLink.id))
        .filter(ConnectorAccountLink.artist_id == artist_id, ConnectorAccountLink.is_active.is_(True))
        .scalar()
        or 0
    )

    return {
        "artist_id": artist_id,
        "status": artist.status,
        "gates": {
            "terms_accepted": bool(terms_accepted),
            "statement_uploaded": int(statement_count) > 0,
            "connector_linked": int(connector_count) > 0,
        },
        "progress": {
            "statements_uploaded": int(statement_count),
            "active_connectors": int(connector_count),
        },
        "timestamps": {
            "created_at": artist.created_at.isoformat() if artist.created_at else None,
            "onboarded_at": artist.onboarded_at.isoformat() if artist.onboarded_at else None,
            "activated_at": artist.activated_at.isoformat() if artist.activated_at else None,
        },
        "expected_status_flow": ["NEW", "ONBOARDED", "ACTIVE"],
    }


@router.get("/permissions/ui")
def get_permissions_dashboard_ui():
    if not _PERMISSIONS_UI_PATH.exists():
        raise HTTPException(status_code=404, detail="Permissions dashboard UI not found")
    return FileResponse(str(_PERMISSIONS_UI_PATH), media_type="text/html")


@router.get("/artists/{artist_id}/connect/permissions-dashboard")
def permissions_dashboard(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    rows = db.query(ConnectorAccountLink).filter(ConnectorAccountLink.artist_id == artist_id).all()

    connected_accounts = [
        {
            "id": r.id,
            "provider": r.provider,
            "tenant_id": r.tenant_id,
            "status": r.status,
            "is_active": r.is_active,
            "last_sync_timestamp": (r.last_refreshed_at or r.updated_at).isoformat() if (r.last_refreshed_at or r.updated_at) else None,
            "connection_health": "healthy" if r.is_active else "disconnected",
        }
        for r in rows
    ]

    expected = {"distributor", "pro", "mlc", "youtube", "social"}
    connected = {str(r.provider).strip().lower() for r in rows}
    missing_connections = sorted(expected - connected)

    return {
        "artist_id": artist_id,
        "connected_accounts": connected_accounts,
        "missing_connections": missing_connections,
        "connection_health": {
            "healthy_count": sum(1 for r in connected_accounts if r["connection_health"] == "healthy"),
            "disconnected_count": sum(1 for r in connected_accounts if r["connection_health"] != "healthy"),
        },
        "last_sync_timestamps": [a["last_sync_timestamp"] for a in connected_accounts if a["last_sync_timestamp"]],
    }


@router.post("/artists/{artist_id}/fetchers/{integration}")
def run_data_fetcher(
    artist_id: str,
    integration: str,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    fetcher = get_fetcher(integration)
    bundle = fetcher.fetch_all(artist_id)
    return {
        "artist_id": artist_id,
        "integration": integration,
        "historical_statements": bundle.historical_statements,
        "catalog_metadata": bundle.catalog_metadata,
        "registrations": bundle.registrations,
        "usage_data": bundle.usage_data,
        "normalized_universal_events": bundle.normalized_events,
    }


@router.post("/artists/{artist_id}/ingestion/upload-any")
async def upload_any_statement(
    artist_id: str,
    files: list[UploadFile] = File(...),
    strict_validation: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    uploads: list[tuple[str, bytes]] = []
    for f in files:
        uploads.append((f.filename or "upload.bin", await f.read()))

    report = FileIngestionPipeline().process(uploads, strict_validation=strict_validation)
    if not report.virus_scan_passed:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Upload blocked by security validation.",
                "scanner": report.scanned_with,
                "documents": [
                    {
                        "filename": d.filename,
                        "validation_passed": d.validation_passed,
                        "warnings": d.warnings,
                    }
                    for d in report.documents
                ],
            },
        )
    return {
        "artist_id": artist_id,
        "virus_scan_passed": report.virus_scan_passed,
        "scanner": report.scanned_with,
        "documents": [
            {
                "filename": d.filename,
                "detected_type": d.detected_type,
                "extension_type": d.extension_type,
                "magic_type": d.magic_type,
                "mime_type": d.mime_type,
                "validation_passed": d.validation_passed,
                "size_bytes": d.size_bytes,
                "pages": d.pages,
                "ocr_text_preview": (d.ocr_text or "")[:400],
                "bundle_items": d.extracted_rows,
                "warnings": d.warnings,
            }
            for d in report.documents
        ],
    }


@router.post("/artists/{artist_id}/parsers/{parser_type}")
async def parse_statement_with_engine(
    artist_id: str,
    parser_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)

    builtins = {"distributor", "pro", "publisher", "mlc"}
    plugin_entrypoint: str | None = None
    if parser_type.lower() not in builtins:
        plugin = (
            db.query(ParserPlugin)
            .filter(
                ParserPlugin.artist_id == artist_id,
                func.lower(ParserPlugin.parser_type) == parser_type.strip().lower(),
                ParserPlugin.enabled.is_(True),
            )
            .first()
        )
        if not plugin:
            raise HTTPException(status_code=404, detail="Parser type is not enabled for this artist")
        plugin_entrypoint = plugin.plugin_entrypoint

    content = await file.read()
    if parser_type.lower() in builtins:
        parser = get_statement_parser(parser_type)
        parsed = parser.parse(content, artist_id, file.filename or "statement.csv")
    else:
        try:
            parsed = parse_with_plugin(
                entrypoint=plugin_entrypoint or "",
                parser_type=parser_type.strip().lower(),
                content=content,
                artist_id=artist_id,
                filename=file.filename or "statement.csv",
                plugin_signature=plugin.plugin_signature,
            )
        except ParserPluginError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "artist_id": artist_id,
        "parser_type": parsed.parser_type,
        "event_count": parsed.event_count,
        "warnings": parsed.warnings,
        "events": parsed.events[:100],
    }


@router.put("/artists/{artist_id}/parsers/plugins", response_model=ParserPluginSchema)
def upsert_parser_plugin(
    artist_id: str,
    payload: ParserPluginUpsertRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    row = (
        db.query(ParserPlugin)
        .filter(
            ParserPlugin.artist_id == artist_id,
            func.lower(ParserPlugin.parser_type) == payload.parser_type.strip().lower(),
        )
        .first()
    )
    if not row:
        row = ParserPlugin(
            artist_id=artist_id,
            parser_type=payload.parser_type.strip().lower(),
            plugin_name=payload.plugin_name,
            plugin_entrypoint=payload.plugin_entrypoint,
            plugin_signature=payload.plugin_signature,
            enabled=payload.enabled,
        )
        db.add(row)
    else:
        row.plugin_name = payload.plugin_name
        row.plugin_entrypoint = payload.plugin_entrypoint
        row.plugin_signature = payload.plugin_signature
        row.enabled = payload.enabled
    db.commit()
    db.refresh(row)
    return row


@router.get("/artists/{artist_id}/parsers/plugins", response_model=list[ParserPluginSchema])
def list_parser_plugins(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return (
        db.query(ParserPlugin)
        .filter(ParserPlugin.artist_id == artist_id)
        .order_by(ParserPlugin.created_at.desc())
        .all()
    )


@router.post("/artists/{artist_id}/sync/jobs", response_model=SyncJobSchema)
def create_sync_job(
    artist_id: str,
    payload: SyncJobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    try:
        get_fetcher(payload.integration)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = SyncJob(
        artist_id=artist_id,
        integration=payload.integration.strip().lower(),
        status="PENDING",
        attempts=0,
        max_attempts=max(1, payload.max_attempts),
        payload_json=json.dumps(payload.payload or {}, sort_keys=True),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if payload.run_async:
        if payload.queue_backend == "background":
            background_tasks.add_task(run_sync_job, job.id)
        else:
            enqueue_sync_job(job.id, queue_backend=payload.queue_backend, db=db)
    else:
        if payload.queue_backend == "inline":
            run_sync_job_with_session(db, job.id)
        else:
            enqueue_sync_job(job.id, queue_backend=payload.queue_backend, db=db)

    job.queue_backend = payload.queue_backend
    db.commit()
    db.refresh(job)

    return job


@router.get("/artists/{artist_id}/sync/jobs", response_model=list[SyncJobSchema])
def list_sync_jobs(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return (
        db.query(SyncJob)
        .filter(SyncJob.artist_id == artist_id)
        .order_by(SyncJob.created_at.desc())
        .all()
    )


@router.get("/artists/{artist_id}/sync/jobs/{job_id}", response_model=SyncJobSchema)
def get_sync_job(artist_id: str, job_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    row = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.artist_id == artist_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Sync job not found")
    return row


@router.post("/artists/{artist_id}/sync/jobs/{job_id}/run", response_model=SyncJobSchema)
def run_sync_job_now(
    artist_id: str,
    job_id: str,
    background_tasks: BackgroundTasks,
    async_run: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    row = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.artist_id == artist_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Sync job not found")

    if async_run:
        background_tasks.add_task(run_sync_job, row.id)
    else:
        run_sync_job_with_session(db, row.id)

    db.expire_all()
    row = db.query(SyncJob).filter(SyncJob.id == job_id, SyncJob.artist_id == artist_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Sync job not found after run")
    return row


@router.post("/artists/{artist_id}/sync/jobs/requeue-due")
def requeue_due_sync_jobs(
    artist_id: str,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    due_for_artist = (
        db.query(SyncJob)
        .filter(
            SyncJob.artist_id == artist_id,
            SyncJob.status == "RETRYING",
            SyncJob.next_run_at.is_not(None),
        )
        .count()
    )
    enqueued = run_due_sync_jobs(db=db)
    return {
        "artist_id": artist_id,
        "due_jobs_for_artist": due_for_artist,
        "enqueued_jobs": enqueued,
    }


@router.get("/artists/{artist_id}/ingestion/missing-data")
def missing_data_status(
    artist_id: str,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)

    accounts = db.query(ConnectorAccountLink).filter(ConnectorAccountLink.artist_id == artist_id).all()
    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    events = db.query(Event).filter(Event.artist_id == artist_id).all()

    connected_sources = [a.provider for a in accounts if a.is_active]
    catalog_rows = [{"isrc": w.isrc, "work_title": w.title, "publisher": None} for w in works]
    registration_rows = [{"registration_id": None if not w.iswc else w.iswc} for w in works]
    usage_rows = [{"source": e.platform or "unknown"} for e in events]

    return detect_missing_data(
        connected_sources=connected_sources,
        catalog_rows=catalog_rows,
        registration_rows=registration_rows,
        usage_rows=usage_rows,
    )


@router.post("/artists/{artist_id}/catalog/graph/build")
def build_catalog_work_graph(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)

    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    statements = db.query(Statement).filter(Statement.artist_id == artist_id).all()

    graph = build_catalog_graph(
        works=[
            {
                "work_id": w.id,
                "work_title": w.title,
                "isrc": w.isrc,
                "owner": artist_id,
                "alt_owner": None,
            }
            for w in works
        ],
        registrations=[{"registration_id": w.iswc, "work_id": w.id, "source": "internal"} for w in works],
        statements=[{"statement_id": s.id, "work_id": None, "source": s.format_detected} for s in statements],
    )
    return {"artist_id": artist_id, **graph}


@router.post("/artists/{artist_id}/catalog/confirm", response_model=CatalogConfirmationSchema)
def confirm_catalog_item(
    artist_id: str,
    payload: CatalogConfirmRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)

    row = CatalogConfirmation(
        artist_id=artist_id,
        work_id=payload.work_id,
        ownership_confirmed=payload.ownership_confirmed,
        splits_confirmed=payload.splits_confirmed,
        publisher_confirmed=payload.publisher_confirmed,
        admin_confirmed=payload.admin_confirmed,
        correction_notes=payload.correction_notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/artists/{artist_id}/catalog/confirm", response_model=list[CatalogConfirmationSchema])
def list_catalog_confirmations(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return (
        db.query(CatalogConfirmation)
        .filter(CatalogConfirmation.artist_id == artist_id)
        .order_by(CatalogConfirmation.confirmed_at.desc())
        .all()
    )


@router.post("/artists/{artist_id}/catalog/infer")
def infer_catalog(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    rows = [{"id": w.id, "work_id": w.id, "streams": 0, "contributors": [], "owner": None} for w in works]
    return infer_catalog_relationships(rows)


@router.post("/artists/{artist_id}/variance/scan")
def variance_scan(
    artist_id: str,
    payload: VarianceScanRequest,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)
    report = run_variance_scan(payload.rows)

    ledger = ImmutableLedgerService(db)
    ledger.append(artist_id, "variance_scan", report)

    return {"artist_id": artist_id, **report}


@router.post("/claims/{claim_id}/evidence/generate-audit")
def generate_audit_evidence_packet(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    packet = {
        "claim_id": claim_id,
        "artist_id": claim.artist_id,
        "timestamped_mismatch": True,
        "source_of_truth_comparison": claim.evidence or {},
        "contract_justification": "Derived from linked terms and payout expectations.",
        "exact_dollar_amount": float(claim.recovered_amount or 0.0),
        "recovery_ledger_entry": f"ledger:{claim_id}",
    }

    ledger = ImmutableLedgerService(db)
    entry = ledger.append(claim.artist_id, "evidence_packet", packet)

    return {"packet": packet, "ledger_entry_hash": entry.entry_hash}


@router.post("/artists/{artist_id}/recovery/automate")
def run_recovery_automation(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    anomalies = db.query(func.count(Event.id)).filter(Event.artist_id == artist_id).scalar() or 0
    findings = [{"type": "STREAM_VS_PAYOUT_MISMATCH", "row": {"counterparty": "pro", "index": i}} for i in range(min(5, int(anomalies)))]
    result = automate_recovery(artist_id, findings)

    ledger = ImmutableLedgerService(db)
    entry = ledger.append(artist_id, "recovery_automation", result)

    return {**result, "ledger_entry_hash": entry.entry_hash}


@router.get("/artists/{artist_id}/ledger/immutable", response_model=list[ImmutableLedgerEntrySchema])
def list_immutable_ledger_entries(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return ImmutableLedgerService(db).list_entries(artist_id)


@router.get("/artists/{artist_id}/workflow/preview")
def preview_full_workflow(artist_id: str, db: Session = Depends(get_db)):
    _artist_or_404(artist_id, db)
    return XR7WorkflowService(db).preview(artist_id)


@router.post("/artists/{artist_id}/workflow/run")
def run_full_workflow(
    artist_id: str,
    payload: WorkflowRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    _artist_or_404(artist_id, db)

    if payload.async_run:
        # Keep async mode lightweight while preserving request-scoped DB context.
        enqueued_jobs = run_due_sync_jobs(db=db)
        return {
            "artist_id": artist_id,
            "queued": True,
            "mode": "async",
            "enqueued_jobs": enqueued_jobs,
            "preview": XR7WorkflowService(db).preview(artist_id),
        }

    result = XR7WorkflowService(db).run(artist_id)
    return {
        "artist_id": result.artist_id,
        "queued": False,
        "mode": "inline",
        "steps": result.steps,
    }
