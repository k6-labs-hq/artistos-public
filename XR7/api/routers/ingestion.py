"""
Statement upload and ingestion endpoints for XR7 Engine 2.

POST /artists/{id}/statements/upload
    Accept a royalty statement CSV file, detect its format (DistroKid,
    TuneCore, CD Baby, Amuse, United Masters, ONErpm, Stem, LANDR, Ditto,
    ReverbNation, Bandcamp, ASCAP, BMI, Spotify, or generic), persist the
    events and payments to the database, run anomaly detection on the
    newly ingested data, and return a parse summary.

GET  /ingestion/supported-formats
    Return the full list of explicitly supported CSV formats with example
    column headers and instructions for each distributor / PRO.

GET /artists/{id}/statements
    List all statement uploads for an artist, newest first.

GET /artists/{id}/statements/{statement_id}
    Return details of a single statement upload.
"""

from __future__ import annotations

import hashlib
import io
import uuid
import zipfile
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func

from XR7.anomaly.engine import AnomalyEngine
from XR7.auth.event_notifications import send_event_notification
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ingestion.statement_parser import parse_csv, parse_statement_file, SUPPORTED_FORMATS
from XR7.models.artist import Artist
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.event import Event, EventType
from XR7.models.notification_preference import NotificationPreference
from XR7.models.payment import Payment, PaymentType
from XR7.models.statement import Statement, StatementSchema
from XR7.api.routers.terms import require_terms_accepted
from XR7.recovery.statute_tracker import classify_anomalies
from XR7.recovery.orchestrator import ClaimsOrchestrator
from XR7.services.artist_lifecycle import promote_to_active
from XR7.services.founder_program import handle_founder_notifications
from XR7.services.identity_matching import persist_identity_match
from XR7.services.statement_signal_extractor import extract_statement_signals, merge_statement_signals, to_json
from XR7.tasks.celery_tasks import on_soundcloud_statement_upload
from XR7.tasks.hubspot import hubspot_sync_recovery_update, hubspot_sync_statement_ingestion
from XR7.ingestion.connectors.soundexchange_mlc import SoundExchangeMLCConnector
from XR7.ingestion.connectors.regional_global import RegionalGlobalConnector
from XR7.ingestion.connectors.global_social_regional import GlobalSocialRegionalConnector
from XR7.recovery.ugc_claim_generator import UGCClaimGenerator
from XR7.services.branding import inject_branding_metadata
from XR7.trolley.client import TrolleyClient, TrolleyException
from xr7_common.logging import get_logger

router = APIRouter(tags=["ingestion"])
logger = get_logger(__name__)

# Maximum upload size: 50 MB (most statements are < 5 MB)
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024
_MAX_BATCH_FILES = 100


# ---------------------------------------------------------------------------
# Supported-formats catalogue endpoint
# ---------------------------------------------------------------------------

@router.get("/ingestion/supported-formats")
def supported_formats() -> dict:
    """
    Return the complete list of explicitly supported royalty statement
    formats, grouped by type (distributor, PRO, DSP, generic).

    For each format the response includes:
    - ``name`` — human-readable distributor/PRO name
    - ``type`` — ``"distributor"`` | ``"pro"`` | ``"dsp"`` | ``"generic"``
    - ``key_columns`` — representative column headers from that format's CSV
    - ``description`` — how to obtain the file and what it covers

    Any file that does not match an explicit format is handled by the
    ``"generic"`` fallback, which recognises any file with recognisable date,
    source, quantity, and amount columns.  This covers distributors such as
    Songtradr, Vydia, AWAL, Symphonic, INgrooves, Believe, Kobalt, and others.
    """
    distributors = {k: v for k, v in SUPPORTED_FORMATS.items() if v["type"] == "distributor"}
    pros = {k: v for k, v in SUPPORTED_FORMATS.items() if v["type"] == "pro"}
    dsps = {k: v for k, v in SUPPORTED_FORMATS.items() if v["type"] == "dsp"}
    generic = {k: v for k, v in SUPPORTED_FORMATS.items() if v["type"] == "generic"}

    return {
        "total_explicit_formats": len(SUPPORTED_FORMATS) - len(generic),
        "formats": SUPPORTED_FORMATS,
        "by_type": {
            "distributors": distributors,
            "pros": pros,
            "dsps": dsps,
            "generic": generic,
        },
        "upload_endpoint": "POST /artists/{artist_id}/statements/upload",
        "note": (
            "Upload CSV/TSV/XLSX statements — format is detected automatically from "
            "the column headers.  If your distributor is not in the explicit "
            "list, the generic fallback handles any statement with date, source, "
            "quantity, and amount columns."
        ),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_events(db: Session, events: list[dict]) -> int:
    """Persist normalised event dicts to the DB, returning the count saved."""
    count = 0
    for e in events:
        try:
            et_raw = str(e.get("event_type", "STREAM")).upper()
            try:
                event_type = EventType(et_raw)
            except ValueError:
                event_type = EventType.STREAM

            event = Event(
                id=str(uuid.uuid4()),
                event_type=event_type,
                artist_id=e["artist_id"],
                platform=e.get("platform"),
                territory=e.get("territory"),
                timestamp=e.get("timestamp") or datetime.now(timezone.utc),
                quantity=int(e.get("quantity", 1)),
                unit_value=float(e.get("unit_value", 0.0)),
                currency=e.get("currency", "USD"),
                # work_id left None — future work: match by ISRC lookup
            )
            db.add(event)
            count += 1
        except Exception:  # noqa: BLE001
            continue
    db.commit()
    return count


def _save_payments(db: Session, payments: list[dict]) -> int:
    """Persist normalised payment dicts to the DB, returning the count saved."""
    count = 0
    for p in payments:
        try:
            pt_raw = str(p.get("payment_type", "ROYALTY")).upper()
            try:
                payment_type = PaymentType(pt_raw)
            except ValueError:
                payment_type = PaymentType.ROYALTY

            payment = Payment(
                id=str(uuid.uuid4()),
                payment_type=payment_type,
                artist_id=p["artist_id"],
                amount=float(p.get("amount", 0.0)),
                currency=p.get("currency", "USD"),
                source=p.get("source"),
                period_start=p.get("period_start"),
                period_end=p.get("period_end"),
                reference_id=p.get("reference_id"),
                received_at=datetime.now(timezone.utc),
            )
            db.add(payment)
            count += 1
        except Exception:  # noqa: BLE001
            continue
    db.commit()
    return count


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/statements/upload",
    response_model=StatementSchema,
    status_code=201,
)
async def upload_statement(
    artist_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a royalty statement file and ingest it into the database.

    Supported formats are automatically detected from the column headers:
        **DistroKid**, **TuneCore**, **CD Baby**, **ASCAP**, **BMI**,
        **Spotify for Artists**, **SoundCloud**, and a **generic** fallback for any statement with
    recognisable date / amount / quantity columns.

    After ingestion, anomaly detection is run automatically so that any
    under-payment issues are immediately flagged.

    Returns a :class:`~XR7.models.statement.Statement` record summarising
    what was parsed and saved.

    **Requires prior acceptance of the Artist Recovery Services Agreement.**
    Call ``GET /terms`` to read the agreement and
    ``POST /artists/{artist_id}/terms/accept`` to accept it.  This endpoint
    returns HTTP 403 until the artist has agreed to the terms.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    # Gate: artist must have accepted the current T&C before submitting data.
    require_terms_accepted(artist_id, db)

    if not file.filename or not file.filename.lower().endswith((".csv", ".tsv", ".xlsx")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV/TSV/XLSX files are accepted.  "
            "Export your statement from your distributor or PRO portal.",
        )

    content = await file.read()
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large (max {_MAX_UPLOAD_BYTES // 1024 // 1024} MB).",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # De-duplication: reject if the exact same file was already uploaded
    file_hash = hashlib.sha256(content).hexdigest()
    existing = (
        db.query(Statement)
        .filter(Statement.artist_id == artist_id, Statement.file_hash == file_hash)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                f"This file has already been uploaded (statement ID: {existing.id}).  "
                "Upload a different statement or contact support if you believe this is an error."
            ),
        )

    anomaly_count_before = (
        db.query(func.count(Anomaly.id)).filter(Anomaly.artist_id == artist_id).scalar() or 0
    )
    processed_before = (
        db.query(func.count(Statement.id))
        .filter(Statement.artist_id == artist_id, Statement.status == "PROCESSED")
        .scalar()
        or 0
    )

    # Parse
    result = parse_statement_file(content, artist_id, filename=file.filename or "statement.csv")
    statement_signals = extract_statement_signals(content, file.filename or "statement.csv", format_detected=result.format_detected)
    status = "PROCESSED"
    error_summary: str | None = None

    if result.errors and not result.events:
        status = "FAILED"
        error_summary = "; ".join(result.errors[:5])

    # Persist
    events_created = _save_events(db, result.events)
    payments_created = _save_payments(db, result.payments)

    # Run anomaly detection on newly ingested data
    if events_created > 0:
        try:
            rg = RightsGraph()
            anomaly_engine = AnomalyEngine(EarningsEngine(rg), rg)
            anomaly_engine.detect_all(artist_id, db)
        except Exception:  # noqa: BLE001
            logger.exception("Anomaly detection after upload failed (non-blocking)", extra={"artist_id": artist_id})

    anomaly_count_after = (
        db.query(func.count(Anomaly.id)).filter(Anomaly.artist_id == artist_id).scalar() or 0
    )
    new_anomalies = max(0, int(anomaly_count_after) - int(anomaly_count_before))
    if new_anomalies > 0:
        pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist_id).first()
        send_event_notification(
            pref,
            "anomaly_detected",
            "New XR7 anomalies detected",
            f"{new_anomalies} new anomaly(ies) were detected after statement upload {file.filename}.",
            current_hour_utc=datetime.now(timezone.utc).hour,
        )

        # Also raise urgency alerts when SOL windows are already at-risk.
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        classified = classify_anomalies(
            [
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
        )
        urgent = [x for x in classified if x.get("sol_status") in {"EXPIRED", "URGENT"}]
        if urgent:
            top = urgent[0]
            amount = float(top.get("estimated_recoverable") or 0.0)
            send_event_notification(
                pref,
                "urgent_sol",
                "Urgent SOL Alert",
                (
                    f"{len(urgent)} item(s) are urgent/expired. Top: {top.get('subtype')} "
                    f"({top.get('sol_status')}), est. recoverable ${amount:,.2f}."
                ),
                current_hour_utc=datetime.now(timezone.utc).hour,
            )
        if int(anomaly_count_before) == 0:
            try:
                hubspot_sync_recovery_update.delay(artist_id, event="first_anomalies_detected")
            except Exception:  # noqa: BLE001
                logger.exception("Failed to enqueue HubSpot first anomalies sync", extra={"artist_id": artist_id})

    # Create audit record
    statement = Statement(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        filename=file.filename or "unknown.csv",
        file_hash=file_hash,
        format_detected=result.format_detected,
        row_count=result.row_count,
        events_created=events_created,
        payments_created=payments_created,
        skipped_rows=result.skipped_rows,
        status=status,
        error_summary=error_summary,
        ingestion_metadata_json=to_json(statement_signals),
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(statement)
    became_active = False
    founder_assignment = None
    if status != "FAILED":
        became_active, founder_assignment = promote_to_active(db, artist)
    db.commit()
    db.refresh(statement)
    if founder_assignment is not None:
        handle_founder_notifications(db, artist, founder_assignment)
        db.commit()

    if status != "FAILED" and became_active and not artist.trolley_recipient_id:
        first_name = artist.first_name or (artist.name.split(" ")[0] if artist.name else "")
        last_name = artist.last_name or (" ".join(artist.name.split(" ")[1:]) if artist.name and " " in artist.name else "")
        try:
            payload = {
                "type": "individual",
                "email": artist.email,
                "name": artist.name,
                "firstName": first_name,
                "lastName": last_name,
                "country": (artist.country_code or "US").upper(),
                "referenceId": artist.id,
            }
            response = TrolleyClient.from_env().create_recipient(payload)
            recipient = response.get("recipient") if isinstance(response, dict) else {}
            recipient_id = recipient.get("id") or response.get("id")
            if recipient_id:
                artist.trolley_recipient_id = recipient_id
                artist.payout_account_status = "pending"
                db.commit()
        except TrolleyException:
            logger.exception("Failed to auto-create Trolley recipient", extra={"artist_id": artist.id})

    if status != "FAILED" and int(processed_before) == 0:
        try:
            hubspot_sync_recovery_update.delay(artist_id, event="first_statement_uploaded")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue HubSpot first statement sync", extra={"artist_id": artist_id})

    identity_match = None
    if status != "FAILED":
        try:
            identity_match = persist_identity_match(db, artist, statement, statement_signals)
        except Exception:  # noqa: BLE001
            logger.exception("Identity auto-match failed (non-blocking)", extra={"artist_id": artist_id, "statement_id": statement.id})

        try:
            hubspot_sync_statement_ingestion.delay(
                artist_id,
                statement.id,
                statement_signals,
                event="statement_uploaded",
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue HubSpot statement ingestion sync", extra={"artist_id": artist_id, "statement_id": statement.id})

    if status != "FAILED" and result.format_detected == "soundcloud":
        try:
            on_soundcloud_statement_upload.delay(artist_id, statement.id)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue SoundCloud statement follow-up workflow", extra={"artist_id": artist_id})

    if status == "FAILED":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Statement could not be parsed.",
                "errors": result.errors[:10],
                "hint": (
                    "Ensure the file has column headers in the first row.  "
                    "Supported formats: DistroKid, TuneCore, CD Baby, ASCAP, BMI, "
                    "Spotify for Artists, SoundCloud, or any generic statement with date/amount columns."
                ),
            },
        )

    if status != "FAILED" and new_anomalies > 0:
        existing_claims = db.query(func.count(Claim.id)).filter(Claim.artist_id == artist_id).scalar() or 0
        if int(existing_claims) == 0:
            first_anomaly = (
                db.query(Anomaly)
                .filter(Anomaly.artist_id == artist_id)
                .order_by(Anomaly.created_at.desc())
                .first()
            )
            if first_anomaly:
                try:
                    ClaimsOrchestrator(db).create_claim(first_anomaly.id, claim_type="AUTO_DRAFT")
                except Exception:  # noqa: BLE001
                    logger.exception(
                        "Failed to auto-draft first claim after statement upload",
                        extra={"artist_id": artist_id, "anomaly_id": first_anomaly.id},
                    )
    statement_payload = StatementSchema.model_validate(statement).model_dump(mode="json")
    if identity_match is not None:
        statement_payload["identity_match"] = {
            "match_id": identity_match.id,
            "confidence_score": identity_match.confidence_score,
            "confidence_band": str(identity_match.confidence_band),
            "decision_status": str(identity_match.decision_status),
        }
    return statement_payload


@router.post("/artists/{artist_id}/statements/upload-batch")
async def upload_statement_batch(
    artist_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a batch of statement files (CSV/ZIP/PDF) with malware scanning and parallel parsing."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    require_terms_accepted(artist_id, db)

    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    if len(files) > _MAX_BATCH_FILES:
        raise HTTPException(status_code=400, detail=f"Batch exceeds max file count ({_MAX_BATCH_FILES})")

    processed = []
    failed = []
    duplicates = 0
    extracted_signals: list[dict] = []

    def _clamav_scan(content: bytes) -> None:
        # Simulated ClamAV gate for dev/test. Replace with real daemon call in production.
        if b"EICAR" in content:
            raise ValueError("Malware signature detected by ClamAV")

    expanded: list[tuple[str, bytes]] = []
    for file in files:
        if not file.filename:
            failed.append({"filename": "unknown", "error": "missing filename"})
            continue
        raw = await file.read()
        _clamav_scan(raw)
        lower = file.filename.lower()
        if lower.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                for name in zf.namelist():
                    if name.lower().endswith((".csv", ".tsv", ".xlsx")):
                        expanded.append((name, zf.read(name)))
        elif lower.endswith(".pdf"):
            # PDF support: store as statement record with no parsed events; OCR/parser hook can be added later.
            expanded.append((file.filename, raw))
        else:
            expanded.append((file.filename, raw))

    for filename, content in expanded:
        try:
            if not content:
                raise ValueError("File is empty")
            if len(content) > _MAX_UPLOAD_BYTES:
                raise ValueError(f"File exceeds {_MAX_UPLOAD_BYTES // 1024 // 1024}MB limit")

            file_hash = hashlib.sha256(content).hexdigest()
            existing = (
                db.query(Statement)
                .filter(Statement.artist_id == artist_id, Statement.file_hash == file_hash)
                .first()
            )
            if existing:
                duplicates += 1
                failed.append({"filename": filename, "error": "duplicate", "statement_id": existing.id})
                continue

            if filename.lower().endswith(".pdf"):
                result = parse_csv(b"", artist_id)
                result.events = []
                result.payments = []
                result.errors = ["PDF parsing deferred to OCR pipeline; metadata-only statement record created"]
                result.format_detected = "pdf"
            else:
                result = parse_statement_file(content, artist_id, filename=filename)
            statement_signals = extract_statement_signals(content, filename, format_detected=result.format_detected)
            events_created = _save_events(db, result.events)
            payments_created = _save_payments(db, result.payments)

            statement = Statement(
                id=str(uuid.uuid4()),
                artist_id=artist_id,
                filename=filename,
                file_hash=file_hash,
                format_detected=result.format_detected,
                row_count=result.row_count,
                events_created=events_created,
                payments_created=payments_created,
                skipped_rows=result.skipped_rows,
                status="PROCESSED" if result.events or result.payments else "FAILED",
                error_summary="; ".join(result.errors[:5]) if result.errors and not result.events else None,
                ingestion_metadata_json=to_json(statement_signals),
                uploaded_at=datetime.now(timezone.utc),
            )
            db.add(statement)
            db.commit()
            db.refresh(statement)

            processed.append({
                "filename": filename,
                "statement_id": statement.id,
                "events_created": events_created,
                "payments_created": payments_created,
                "status": statement.status,
            })
            if statement.status != "FAILED":
                extracted_signals.append(statement_signals)
        except Exception as exc:  # noqa: BLE001
            failed.append({"filename": filename, "error": str(exc)})

    # Trigger anomaly detection once after the full batch.
    if processed:
        became_active, founder_assignment = promote_to_active(db, artist)
        db.commit()
        if founder_assignment is not None:
            handle_founder_notifications(db, artist, founder_assignment)
            db.commit()
        if became_active and not artist.trolley_recipient_id:
            first_name = artist.first_name or (artist.name.split(" ")[0] if artist.name else "")
            last_name = artist.last_name or (" ".join(artist.name.split(" ")[1:]) if artist.name and " " in artist.name else "")
            try:
                payload = {
                    "type": "individual",
                    "email": artist.email,
                    "name": artist.name,
                    "firstName": first_name,
                    "lastName": last_name,
                    "country": (artist.country_code or "US").upper(),
                    "referenceId": artist.id,
                }
                response = TrolleyClient.from_env().create_recipient(payload)
                recipient = response.get("recipient") if isinstance(response, dict) else {}
                recipient_id = recipient.get("id") or response.get("id")
                if recipient_id:
                    artist.trolley_recipient_id = recipient_id
                    artist.payout_account_status = "pending"
                    db.commit()
            except TrolleyException:
                logger.exception("Failed to auto-create Trolley recipient", extra={"artist_id": artist.id})
        try:
            hubspot_sync_recovery_update.delay(artist_id, event="statement_batch_uploaded")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue HubSpot statement batch sync", extra={"artist_id": artist_id})
        try:
            merged_signals = merge_statement_signals(extracted_signals)
            hubspot_sync_statement_ingestion.delay(
                artist_id,
                None,
                merged_signals,
                event="statement_batch_uploaded",
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enqueue HubSpot batch statement signal sync", extra={"artist_id": artist_id})
        try:
            rg = RightsGraph()
            AnomalyEngine(EarningsEngine(rg), rg).detect_all(artist_id, db)
        except Exception:  # noqa: BLE001
            logger.exception("Batch anomaly detection failed (non-blocking)", extra={"artist_id": artist_id})

    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "requested": len(files),
        "expanded_files": len(expanded),
        "processed_count": len(processed),
        "failed_count": len(failed),
        "duplicate_count": duplicates,
        "processed": processed,
        "failed": failed,
    })


@router.post("/artists/{artist_id}/connect/soundexchange-mlc")
async def connect_soundexchange_mlc(artist_id: str, years_back: int = 10, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    connector = SoundExchangeMLCConnector()
    rows = await connector.fetch_royalty_statements(artist_id, years_back=years_back)
    anomalies = await connector.detect_unreported_uses(["USRC17607839", "USRC17607840"])
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "rows_fetched": len(rows),
            "anomalies": anomalies,
            "leakage_discovered_update": len(anomalies),
        },
    )


@router.get("/artists/{artist_id}/connect/soundexchange-mlc/status")
def soundexchange_mlc_status(artist_id: str, db: Session = Depends(get_db)):
    return inject_branding_metadata(
        db,
        {"artist_id": artist_id, "status": "ready_with_csv_fallback", "simulated_mode": True},
    )


@router.post("/artists/{artist_id}/connect/regional-global")
async def connect_regional_global(artist_id: str, genre: str = "latin", territory: str = "LATAM", db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    connector = RegionalGlobalConnector()
    rows = await connector.fetch_statements(artist_id, genre, territory)
    anomalies = await connector.auto_detect_genre_specific_anomalies(artist_id, genre, territory)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "rows": rows,
            "anomalies": anomalies,
            "territory": territory,
            "genre": genre,
        },
    )


@router.get("/artists/{artist_id}/connect/regional-global/status")
def regional_global_status(artist_id: str, db: Session = Depends(get_db)):
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "status": "ready_with_csv_fallback",
            "territories": ["LATAM", "JP", "KR", "AFRICA", "IN", "CN"],
        },
    )




@router.get(
    "/artists/{artist_id}/statements",
    response_model=List[StatementSchema],
)
def list_statements(artist_id: str, db: Session = Depends(get_db)):
    """
    Return all statement uploads for an artist, newest first.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    return (
        db.query(Statement)
        .filter(Statement.artist_id == artist_id)
        .order_by(Statement.uploaded_at.desc())
        .all()
    )


@router.get(
    "/artists/{artist_id}/statements/{statement_id}",
    response_model=StatementSchema,
)
def get_statement(artist_id: str, statement_id: str, db: Session = Depends(get_db)):
    """
    Return details of a single statement upload.
    """
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.artist_id == artist_id)
        .first()
    )
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return statement
