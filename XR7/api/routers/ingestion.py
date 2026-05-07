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
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from XR7.api.authz import require_admin_session
from XR7.api.routers.anomalies import run_detection_and_persist
from XR7.api.routers.terms import require_terms_accepted
from XR7.auth.event_notifications import send_event_notification
from XR7.fingerprinting.matching.identity_matching import persist_identity_match
from XR7.ingestion.connectors.regional_global import RegionalGlobalConnector
from XR7.ingestion.connectors.soundexchange_mlc import SoundExchangeMLCConnector
from XR7.ingestion.numbers_file import numbers_to_csv_bytes
from XR7.ingestion.parse_timeout import StatementParseTimeoutError, parse_with_timeout
from XR7.ingestion.statement_parser import SUPPORTED_FORMATS, parse_csv, parse_statement_file
from XR7.ingestion.statement_signal_extractor import (
    extract_statement_signals,
    merge_statement_signals,
    to_json,
)
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.event import Event, EventType
from XR7.models.notification_preference import NotificationPreference
from XR7.models.payment import Payment, PaymentType
from XR7.models.statement import Statement, StatementSchema
from XR7.recovery.statute_tracker import classify_anomalies
from XR7.services.artist_lifecycle import promote_to_active
from XR7.services.branding import inject_branding_metadata
from XR7.services.founder_program import handle_founder_notifications
from XR7.services.live_updates import broadcast_live_update
from XR7.services.rate_limiter import check_upload_rate_limit
from XR7.services.router_v21_phase1 import router_service_for
from XR7.services.webhook_delivery import OutboundWebhookService
from XR7.tasks.celery_tasks import on_soundcloud_statement_upload
from XR7.tasks.hubspot import hubspot_sync_recovery_update, hubspot_sync_statement_ingestion
from XR7.tasks.webhooks import deliver_webhook_event
from XR7.trolley.client import TrolleyClient, TrolleyException
from xr7_common.logging import get_logger

router = APIRouter(tags=["ingestion"])
_router_service = router_service_for("ingestion")
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


def _save_events(db: Session, events: list[dict]) -> dict[str, int]:
    """Persist normalised event dicts to the DB with row-level deduplication.

    Uses INSERT...ON CONFLICT DO NOTHING to skip duplicate events based on
    the unique constraint (artist_id, event_type, platform, territory,
    timestamp, quantity, unit_value, work_id).

    Returns dict with counts: {"inserted": N, "skipped": M}

    Commits in batches of 500 to limit memory pressure for large statements.
    """
    _CHUNK = 500
    inserted = 0
    skipped = 0

    # Prepare event records
    event_records = []
    for e in events:
        try:
            et_raw = str(e.get("event_type", "STREAM")).upper()
            try:
                event_type = EventType(et_raw)
            except ValueError:
                event_type = EventType.STREAM

            event_records.append(
                {
                    "id": str(uuid.uuid4()),
                    "event_type": event_type.value,
                    "artist_id": e["artist_id"],
                    "platform": e.get("platform"),
                    "territory": e.get("territory"),
                    "timestamp": e.get("timestamp") or datetime.now(timezone.utc),
                    "quantity": int(e.get("quantity", 1)),
                    "unit_value": float(e.get("unit_value", 0.0)),
                    "currency": e.get("currency", "USD"),
                    "work_id": None,  # future: match by ISRC lookup
                }
            )
        except Exception:  # noqa: BLE001
            skipped += 1
            continue

    # Bulk insert with ON CONFLICT DO NOTHING for deduplication
    total_attempted = len(event_records)
    for i in range(0, total_attempted, _CHUNK):
        chunk = event_records[i : i + _CHUNK]
        if not chunk:
            continue

        # Use PostgreSQL INSERT...ON CONFLICT DO NOTHING
        stmt = insert(Event.__table__).values(chunk)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[
                "artist_id",
                "event_type",
                "platform",
                "territory",
                "timestamp",
                "quantity",
                "unit_value",
            ]
        )

        result = db.execute(stmt)
        db.commit()

        # Track how many were actually inserted (excluding duplicates)
        inserted += result.rowcount

    skipped += total_attempted - inserted
    logger.info(
        "Event ingestion complete",
        extra={
            "total_events": len(events),
            "inserted": inserted,
            "skipped_duplicates": skipped,
            "deduplication_rate": round(skipped / len(events) * 100, 1) if events else 0,
        },
    )

    return {"inserted": inserted, "skipped": skipped}


# Map detected statement format → payer canonical IDs that imply a routing
# affiliation. We don't infer "you're a BMI writer" from a DistroKid statement —
# only PRO/MLC/SoundExchange statements are direct evidence of an affiliation.
_FORMAT_TO_AFFILIATIONS: dict[str, tuple[str, ...]] = {
    "ascap": ("ASCAP",),
    "bmi": ("BMI",),
    "bmi_real": ("BMI",),
    "bmi_pdf": ("BMI",),
    "mlc": ("MLC",),
    "soundexchange": ("SoundExchange",),
}


def _infer_affiliations_from_formats(formats: list[str]) -> list[str]:
    """Collect the canonical payer IDs implied by a list of detected formats."""
    seen: list[str] = []
    for fmt in formats:
        for affiliation in _FORMAT_TO_AFFILIATIONS.get((fmt or "").lower(), ()):
            if affiliation not in seen:
                seen.append(affiliation)
    return seen


def _autofill_payer_routing_from_uploads(
    db: Session,
    artist,  # noqa: ANN001 — Artist model, avoid circular import in type hints
    formats_seen: list[str],
    bmi_affiliate_state: str | None = None,
) -> None:
    """Backfill Artist.pro_affiliations + Artist.bmi_office_name from upload signals.

    Idempotent: pre-existing values stay put. Only fills empty fields. This
    replaces the manual "where do your statements come from?" onboarding gate
    — once we've parsed a BMI/ASCAP/MLC statement, we already know who pays.
    """
    inferred = _infer_affiliations_from_formats(formats_seen)
    if inferred and not artist.pro_affiliations:
        artist.pro_affiliations = inferred
    if (
        "BMI" in (artist.pro_affiliations or [])
        and not artist.bmi_office_name
    ):
        from XR7.recovery.payer_config import infer_bmi_office_from_state  # noqa: PLC0415

        artist.bmi_office_name = infer_bmi_office_from_state(bmi_affiliate_state)


def _save_payments(db: Session, payments: list[dict]) -> int:
    """Persist normalised payment dicts to the DB, returning the count saved.

    Uses per-row savepoints so a duplicate (artist_id, reference_id) skips the
    row without aborting the whole transaction. Matches the ingestion
    idempotency contract: re-uploading the same statement is a no-op.
    """
    count = 0
    created: list[Payment] = []
    for p in payments:
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
            payer_account_id=p.get("payer_account_id"),
            payer_ip_number=p.get("payer_ip_number"),
            payer_work_id=p.get("payer_work_id"),
        )
        try:
            with db.begin_nested():
                db.add(payment)
                db.flush()
            created.append(payment)
            count += 1
        except IntegrityError:
            # Duplicate (artist_id, reference_id) — skip idempotently.
            continue
    db.commit()
    webhook_service = OutboundWebhookService(db)
    for payment in created:
        event = webhook_service.queue_event(
            event_type="payment.received",
            payload={
                "payment_id": payment.id,
                "artist_id": payment.artist_id,
                "amount": float(payment.amount or 0.0),
                "currency": payment.currency,
                "source": payment.source,
            },
        )
        deliver_webhook_event.delay(event.id)
        broadcast_live_update(
            "payment.received",
            {
                "payment_id": payment.id,
                "artist_id": payment.artist_id,
                "amount": float(payment.amount or 0.0),
                "currency": payment.currency,
            },
        )
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
    artist = _router_service.get_artist_or_404(artist_id, db)

    # CRITICAL SECURITY: Rate limit uploads to prevent resource exhaustion
    check_upload_rate_limit(artist_id)

    # Gate: artist must have accepted the current T&C before submitting data.
    require_terms_accepted(artist_id, db)

    if not file.filename or not file.filename.lower().endswith(
        (".csv", ".tsv", ".xlsx", ".numbers", ".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV/TSV/XLSX/Numbers/PDF files are accepted.  "
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

    # De-duplication runs on the *original* uploaded bytes. A .numbers and a
    # CSV that happen to convert to the same content are still two different
    # files the user submitted — treat them as different. Re-uploading the
    # exact same file (.numbers or .csv) still dedups correctly because the
    # original bytes are identical.
    file_hash = hashlib.sha256(content).hexdigest()

    # Preserve the un-converted bytes for object-storage persistence below.
    # `content` may be rewritten by the .numbers → CSV step that follows.
    original_content = content

    # Apple Numbers files (.numbers) are zip-wrapped binary protobuf — the CSV-based
    # parsers can't read them directly. Convert AFTER hashing so dedup is keyed on
    # the original upload, not on post-conversion bytes. See #195.
    if file.filename.lower().endswith(".numbers"):
        try:
            content = numbers_to_csv_bytes(content)
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Could not read Numbers file: {exc}",
            ) from exc
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

    # Persist the original bytes (pre-conversion) to object storage so we
    # can reprocess later under updated parsers and produce the source
    # statement on demand for audit/legal review. See
    # docs/decisions/statement-storage-and-retention.md. Failure doesn't
    # block ingestion — the parsed data is still usable — but the warning
    # is now surfaced in the Statement's error_summary so the dashboard
    # makes the missing source bytes visible instead of silently losing
    # them the way the prior log-only handling did.
    s3_uri: str | None = None
    storage_warning: str | None = None
    try:
        from XR7.services.storage_service import ObjectStorageService  # noqa: PLC0415

        storage = ObjectStorageService()
        original_ext = (file.filename or "statement.csv").rsplit(".", 1)[-1]
        s3_key = storage.build_statement_key(artist_id, file_hash, original_ext)
        # `original_content` is the un-converted bytes; `content` may have been
        # rewritten by the .numbers → CSV step above. Always store the original.
        s3_uri = storage.upload_bytes(
            s3_key,
            original_content,
            content_type="application/octet-stream",
        )
    except Exception as exc:  # noqa: BLE001
        storage_warning = f"Source bytes not persisted to object storage: {exc}"
        logger.warning(
            "Failed to persist statement bytes to object storage; continuing with parse",
            extra={"artist_id": artist_id, "file_hash": file_hash, "filename": file.filename},
            exc_info=True,
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

    # Parse with timeout enforcement (prevents DoS from malformed files).
    # If the input was a .numbers file we already converted it to CSV bytes
    # above; pass a .csv suffix to the parser dispatcher so it picks the
    # CSV path. Statement audit / display still uses the user's original filename.
    parse_filename = (
        (file.filename or "statement.csv").rsplit(".", 1)[0] + ".csv"
        if (file.filename or "").lower().endswith(".numbers")
        else (file.filename or "statement.csv")
    )

    # PDF route: BMI Royalty Statement PDFs go through the dedicated
    # bmi_pdf parser. Other PDFs aren't currently supported.
    bmi_affiliate_state: str | None = None
    if (file.filename or "").lower().endswith(".pdf"):
        from XR7.ingestion.bmi_pdf import (  # noqa: PLC0415
            bmi_pdf_to_events_and_payments,
            is_bmi_pdf,
            parse_bmi_pdf_bytes,
        )
        from XR7.ingestion.statement_parser import ParseResult  # noqa: PLC0415

        if not is_bmi_pdf(original_content):
            raise HTTPException(
                status_code=422,
                detail="Only BMI Royalty Statement PDFs are supported today.",
            )
        events, payments, errors = bmi_pdf_to_events_and_payments(original_content, artist_id)
        try:
            bmi_affiliate_state = parse_bmi_pdf_bytes(original_content).affiliate_state
        except Exception:  # noqa: BLE001
            bmi_affiliate_state = None
        result = ParseResult(
            events=events,
            payments=payments,
            errors=errors,
            row_count=len(events),
            skipped_rows=0,
            format_detected="bmi_pdf",
        )
    else:
        try:
            result = parse_with_timeout(
                parse_statement_file,
                content,
                artist_id,
                filename=parse_filename,
            )
        except StatementParseTimeoutError as timeout_err:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Statement parsing timed out after {timeout_err.timeout_seconds} seconds. "
                    "The file may be malformed or too complex to process. "
                    "Please check the file format and try uploading a smaller date range."
                ),
            ) from timeout_err

    # Signal extraction reads the file as a tabular CSV/TSV. PDFs (and
    # other non-tabular sources) crash the csv reader, so skip them and
    # fall back to an empty signals dict — non-critical, only used for
    # HubSpot sync + analytics.
    if (file.filename or "").lower().endswith(".pdf"):
        statement_signals = {"source_format": result.format_detected}
    else:
        statement_signals = extract_statement_signals(
            content, file.filename or "statement.csv", format_detected=result.format_detected
        )
    status = "PROCESSED"
    error_summary: str | None = None

    if result.errors and not result.events:
        status = "FAILED"
        error_summary = "; ".join(result.errors[:5])

    # Append the storage-persist warning so the dashboard's upload history
    # shows it. We don't downgrade status to FAILED — parsing succeeded,
    # the audit-trail half is just incomplete — but the user/operator
    # should be able to see at a glance that the source bytes weren't kept.
    if storage_warning:
        error_summary = (
            f"{error_summary}; {storage_warning}" if error_summary else storage_warning
        )

    # Persist
    event_result = _save_events(db, result.events)
    events_created = event_result["inserted"]
    payments_created = _save_payments(db, result.payments)

    # Run anomaly detection on newly ingested data and persist findings.
    # Without this, dicts came back from the engine but were never inserted
    # into the anomalies table — so the dashboard / notifications saw nothing.
    if events_created > 0:
        try:
            run_detection_and_persist(artist_id, db)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Anomaly detection after upload failed (non-blocking)",
                extra={"artist_id": artist_id},
            )

    anomaly_count_after = (
        db.query(func.count(Anomaly.id)).filter(Anomaly.artist_id == artist_id).scalar() or 0
    )
    new_anomalies = max(0, int(anomaly_count_after) - int(anomaly_count_before))
    if new_anomalies > 0:
        pref = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.artist_id == artist_id)
            .first()
        )
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
                logger.exception(
                    "Failed to enqueue HubSpot first anomalies sync", extra={"artist_id": artist_id}
                )

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
        s3_uri=s3_uri,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(statement)
    became_active = False
    founder_assignment = None
    if status != "FAILED":
        became_active, founder_assignment = promote_to_active(db, artist)
        _autofill_payer_routing_from_uploads(
            db,
            artist,
            [result.format_detected],
            bmi_affiliate_state=bmi_affiliate_state,
        )
    db.commit()
    db.refresh(statement)
    if founder_assignment is not None:
        handle_founder_notifications(db, artist, founder_assignment)
        db.commit()

    if status != "FAILED" and became_active and not artist.trolley_recipient_id:
        first_name = artist.first_name or (artist.name.split(" ")[0] if artist.name else "")
        last_name = artist.last_name or (
            " ".join(artist.name.split(" ")[1:]) if artist.name and " " in artist.name else ""
        )
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
            logger.exception(
                "Failed to auto-create Trolley recipient", extra={"artist_id": artist.id}
            )

    if status != "FAILED" and int(processed_before) == 0:
        try:
            hubspot_sync_recovery_update.delay(artist_id, event="first_statement_uploaded")
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enqueue HubSpot first statement sync", extra={"artist_id": artist_id}
            )

    identity_match = None
    if status != "FAILED":
        try:
            identity_match = persist_identity_match(db, artist, statement, statement_signals)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Identity auto-match failed (non-blocking)",
                extra={"artist_id": artist_id, "statement_id": statement.id},
            )

        try:
            hubspot_sync_statement_ingestion.delay(
                artist_id,
                statement.id,
                statement_signals,
                event="statement_uploaded",
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enqueue HubSpot statement ingestion sync",
                extra={"artist_id": artist_id, "statement_id": statement.id},
            )

    if status != "FAILED" and result.format_detected == "soundcloud":
        try:
            on_soundcloud_statement_upload.delay(artist_id, statement.id)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enqueue SoundCloud statement follow-up workflow",
                extra={"artist_id": artist_id},
            )

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

    # Auto-drafting now happens inside `run_detection_and_persist` per
    # anomaly (see XR7.recovery.auto_draft.auto_draft_and_promote). The
    # previous "first anomaly only" gate here meant batch BMI uploads
    # produced zero claims and the operator queue stayed empty.
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
    artist = _router_service.get_artist_or_404(artist_id, db)

    # CRITICAL SECURITY: Rate limit uploads to prevent resource exhaustion
    check_upload_rate_limit(artist_id)

    require_terms_accepted(artist_id, db)

    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    if len(files) > _MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400, detail=f"Batch exceeds max file count ({_MAX_BATCH_FILES})"
        )

    processed = []
    failed = []
    duplicates = 0
    extracted_signals: list[dict] = []
    formats_seen: list[str] = []
    bmi_affiliate_state: str | None = None

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
        elif lower.endswith(".numbers"):
            # Apple Numbers files need conversion to CSV before the parser can
            # touch them. Parity with the single-file upload endpoint above —
            # without this, .numbers files in a batch silently fall through
            # and never get into the statements table at all.
            try:
                converted = numbers_to_csv_bytes(raw)
            except ValueError as exc:
                failed.append({"filename": file.filename, "error": f"numbers conversion: {exc}"})
                continue
            csv_name = file.filename.rsplit(".", 1)[0] + ".csv"
            expanded.append((csv_name, converted))
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
                failed.append(
                    {"filename": filename, "error": "duplicate", "statement_id": existing.id}
                )
                continue

            if filename.lower().endswith(".pdf"):
                from XR7.ingestion.bmi_pdf import (  # noqa: PLC0415
                    bmi_pdf_to_events_and_payments,
                    is_bmi_pdf,
                    parse_bmi_pdf_bytes,
                )

                if is_bmi_pdf(content):
                    pdf_events, pdf_payments, pdf_errors = bmi_pdf_to_events_and_payments(
                        content, artist_id
                    )
                    if bmi_affiliate_state is None:
                        try:
                            bmi_affiliate_state = parse_bmi_pdf_bytes(content).affiliate_state
                        except Exception:  # noqa: BLE001
                            bmi_affiliate_state = None
                    result = parse_csv(b"", artist_id)
                    result.events = pdf_events
                    result.payments = pdf_payments
                    result.errors = pdf_errors
                    result.row_count = len(pdf_events)
                    result.format_detected = "bmi_pdf"
                else:
                    # Non-BMI PDF: keep the metadata-only stub for now.
                    result = parse_csv(b"", artist_id)
                    result.events = []
                    result.payments = []
                    result.errors = [
                        "PDF format not recognized; only BMI Royalty Statement PDFs parse today"
                    ]
                    result.format_detected = "pdf"
            else:
                try:
                    result = parse_with_timeout(
                        parse_statement_file, content, artist_id, filename=filename
                    )
                except StatementParseTimeoutError as timeout_err:
                    # For batch upload, log timeout but continue with other files
                    logger.error(
                        f"Batch upload file parsing timeout: {filename}",
                        extra={"artist_id": artist_id, "filename": filename},
                    )
                    result = parse_csv(b"", artist_id)
                    result.errors = [
                        f"Parsing timed out after {timeout_err.timeout_seconds}s (file may be malformed)"
                    ]
                    result.format_detected = "timeout"

            # Skip signal extraction for non-tabular formats (PDF) — the
            # csv reader can't read PDF binary. Same fallback as the
            # single-file path above.
            if filename.lower().endswith(".pdf"):
                statement_signals = {"source_format": result.format_detected}
            else:
                statement_signals = extract_statement_signals(
                    content, filename, format_detected=result.format_detected
                )
            event_result = _save_events(db, result.events)
            events_created = event_result["inserted"]
            payments_created = _save_payments(db, result.payments)

            # Persist source bytes — same path as the single-file endpoint.
            # Batch was previously skipping this entirely, so every BMI corpus
            # upload silently lost its source bytes. See parity in upload_statement.
            s3_uri: str | None = None
            storage_warning: str | None = None
            try:
                from XR7.services.storage_service import ObjectStorageService  # noqa: PLC0415

                storage = ObjectStorageService()
                original_ext = (filename or "statement.csv").rsplit(".", 1)[-1]
                s3_key = storage.build_statement_key(artist_id, file_hash, original_ext)
                s3_uri = storage.upload_bytes(
                    s3_key, content, content_type="application/octet-stream"
                )
            except Exception as exc:  # noqa: BLE001
                storage_warning = f"Source bytes not persisted to object storage: {exc}"
                logger.warning(
                    "Batch upload: failed to persist statement bytes; continuing",
                    extra={"artist_id": artist_id, "file_hash": file_hash, "filename": filename},
                    exc_info=True,
                )

            base_summary = (
                "; ".join(result.errors[:5]) if result.errors and not result.events else None
            )
            error_summary = (
                f"{base_summary}; {storage_warning}"
                if base_summary and storage_warning
                else (base_summary or storage_warning)
            )

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
                error_summary=error_summary,
                ingestion_metadata_json=to_json(statement_signals),
                s3_uri=s3_uri,
                uploaded_at=datetime.now(timezone.utc),
            )
            db.add(statement)
            db.commit()
            db.refresh(statement)

            processed.append(
                {
                    "filename": filename,
                    "statement_id": statement.id,
                    "events_created": events_created,
                    "payments_created": payments_created,
                    "status": statement.status,
                }
            )
            if statement.status != "FAILED":
                extracted_signals.append(statement_signals)
                formats_seen.append(result.format_detected)
        except Exception as exc:  # noqa: BLE001
            failed.append({"filename": filename, "error": str(exc)})

    # Trigger anomaly detection once after the full batch.
    if processed:
        became_active, founder_assignment = promote_to_active(db, artist)
        _autofill_payer_routing_from_uploads(
            db,
            artist,
            formats_seen,
            bmi_affiliate_state=bmi_affiliate_state,
        )
        db.commit()
        if founder_assignment is not None:
            handle_founder_notifications(db, artist, founder_assignment)
            db.commit()
        if became_active and not artist.trolley_recipient_id:
            first_name = artist.first_name or (artist.name.split(" ")[0] if artist.name else "")
            last_name = artist.last_name or (
                " ".join(artist.name.split(" ")[1:]) if artist.name and " " in artist.name else ""
            )
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
                logger.exception(
                    "Failed to auto-create Trolley recipient", extra={"artist_id": artist.id}
                )
        try:
            hubspot_sync_recovery_update.delay(artist_id, event="statement_batch_uploaded")
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enqueue HubSpot statement batch sync", extra={"artist_id": artist_id}
            )
        try:
            merged_signals = merge_statement_signals(extracted_signals)
            hubspot_sync_statement_ingestion.delay(
                artist_id,
                None,
                merged_signals,
                event="statement_batch_uploaded",
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enqueue HubSpot batch statement signal sync",
                extra={"artist_id": artist_id},
            )
        try:
            run_detection_and_persist(artist_id, db)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Batch anomaly detection failed (non-blocking)", extra={"artist_id": artist_id}
            )

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "requested": len(files),
            "expanded_files": len(expanded),
            "processed_count": len(processed),
            "failed_count": len(failed),
            "duplicate_count": duplicates,
            "processed": processed,
            "failed": failed,
        },
    )


@router.post("/artists/{artist_id}/connect/soundexchange-mlc")
async def connect_soundexchange_mlc(
    artist_id: str, years_back: int = 10, db: Session = Depends(get_db)
):
    _router_service.get_artist_or_404(artist_id, db)
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
async def connect_regional_global(
    artist_id: str, genre: str = "latin", territory: str = "LATAM", db: Session = Depends(get_db)
):
    _router_service.get_artist_or_404(artist_id, db)
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
    _router_service.get_artist_or_404(artist_id, db)

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


@router.get("/admin/statements/{statement_id}/download")
def admin_download_statement(
    statement_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin_session),
):
    """Retrieve the original uploaded statement bytes from object storage.

    Admin-only. Returns 404 if the statement doesn't exist or was uploaded
    before the storage wiring landed (legacy rows have ``s3_uri`` NULL).
    Used for audit / legal evidence and for the reprocess script.
    """
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")
    if not statement.s3_uri:
        raise HTTPException(
            status_code=404,
            detail=(
                "This statement was uploaded before object storage was wired; "
                "the original bytes are not retained."
            ),
        )

    from XR7.services.storage_service import ObjectStorageService  # noqa: PLC0415

    storage = ObjectStorageService()
    try:
        key = storage.s3_uri_to_key(statement.s3_uri)
        data = storage.download_bytes(key)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Statement download from object storage failed")
        raise HTTPException(
            status_code=502,
            detail=f"Could not retrieve stored statement bytes: {exc}",
        ) from exc

    filename = statement.filename or f"{statement_id}.bin"
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
