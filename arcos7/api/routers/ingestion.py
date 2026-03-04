"""
Statement upload and ingestion endpoints for ARCOS7 Engine 2.

POST /artists/{id}/statements/upload
    Accept a royalty statement CSV file, detect its format (DistroKid,
    TuneCore, CD Baby, ASCAP, BMI, Spotify, or generic), persist the
    events and payments to the database, run anomaly detection on the
    newly ingested data, and return a parse summary.

GET /artists/{id}/statements
    List all statement uploads for an artist, newest first.

GET /artists/{id}/statements/{statement_id}
    Return details of a single statement upload.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from arcos7.anomaly.engine import AnomalyEngine
from arcos7.earnings.engine import EarningsEngine
from arcos7.graph.rights_graph import RightsGraph
from arcos7.ingestion.statement_parser import parse_csv
from arcos7.models.artist import Artist
from arcos7.models.base import get_db
from arcos7.models.event import Event, EventType
from arcos7.models.payment import Payment, PaymentType
from arcos7.models.statement import Statement, StatementSchema

router = APIRouter(tags=["ingestion"])

# Maximum upload size: 50 MB (most statements are < 5 MB)
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024


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
    Upload a royalty statement CSV and ingest it into the database.

    Supported formats are automatically detected from the column headers:
    **DistroKid**, **TuneCore**, **CD Baby**, **ASCAP**, **BMI**,
    **Spotify for Artists**, and a **generic** fallback for any CSV with
    recognisable date / amount / quantity columns.

    After ingestion, anomaly detection is run automatically so that any
    under-payment issues are immediately flagged.

    Returns a :class:`~arcos7.models.statement.Statement` record summarising
    what was parsed and saved.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted.  "
            "Export your statement as CSV from your distributor or PRO portal.",
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

    # Parse
    result = parse_csv(content, artist_id)
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
            pass  # anomaly detection failure must not block the upload response

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
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)

    if status == "FAILED":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Statement could not be parsed.",
                "errors": result.errors[:10],
                "hint": (
                    "Ensure the CSV has column headers in the first row.  "
                    "Supported formats: DistroKid, TuneCore, CD Baby, ASCAP, BMI, "
                    "Spotify for Artists, or any generic CSV with date/amount columns."
                ),
            },
        )

    return statement


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
