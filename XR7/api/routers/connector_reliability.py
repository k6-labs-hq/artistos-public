"""Connector reliability router — webhook ingestion, DLQ replay, sync cursor."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.authz import require_admin

from XR7.models.base import get_db
from XR7.models.connector_sync_cursor import ConnectorSyncCursor, ConnectorSyncCursorSchema
from XR7.models.webhook_event import WebhookEventSchema
from XR7.services.connector_replay_service import (
    get_failed_events,
    ingest_webhook,
    replay_event,
    upsert_sync_cursor,
)

router = APIRouter(tags=["connector-reliability"])


# ---------------------------------------------------------------------------
# Webhook ingestion
# ---------------------------------------------------------------------------


class WebhookIngestRequest(BaseModel):
    source: str
    event_type: str
    raw_payload: str
    signature: Optional[str] = None


@router.post("/connectors/webhook/ingest", response_model=WebhookEventSchema, status_code=201)
def ingest_webhook_event(
    body: WebhookIngestRequest,
    db: Session = Depends(get_db),
):
    """Receive and persist an inbound webhook payload."""
    secret = os.environ.get(f"WEBHOOK_SECRET_{body.source.upper()}", "")
    event = ingest_webhook(
        source=body.source,
        event_type=body.event_type,
        raw_payload=body.raw_payload,
        signature=body.signature,
        secret=secret or None,
        db=db,
    )
    return event


# ---------------------------------------------------------------------------
# DLQ — admin replay
# ---------------------------------------------------------------------------


@router.get(
    "/admin/connectors/webhook/queue",
    response_model=List[WebhookEventSchema],
    dependencies=[Depends(require_admin)],
)
def get_dlq(
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List failed webhook events (DLQ)."""
    return get_failed_events(source=source, db=db, limit=limit)


@router.post(
    "/admin/connectors/webhook/{event_id}/replay",
    response_model=WebhookEventSchema,
    dependencies=[Depends(require_admin)],
)
def replay_webhook_event(event_id: str, db: Session = Depends(get_db)):
    """Reset a FAILED event to REPLAYING for re-processing."""
    try:
        return replay_event(event_id=event_id, db=db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Sync cursor
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/connectors/{integration}/sync-cursor",
    response_model=ConnectorSyncCursorSchema,
)
def get_sync_cursor(artist_id: str, integration: str, db: Session = Depends(get_db)):
    """Return the current sync cursor for an artist/integration pair."""
    cursor = (
        db.query(ConnectorSyncCursor)
        .filter(
            ConnectorSyncCursor.artist_id == artist_id,
            ConnectorSyncCursor.integration == integration,
        )
        .first()
    )
    if not cursor:
        raise HTTPException(
            status_code=404,
            detail=f"No sync cursor found for artist {artist_id} / {integration}",
        )
    return cursor


class SyncCursorUpdateRequest(BaseModel):
    cursor_value: str


@router.put(
    "/artists/{artist_id}/connectors/{integration}/sync-cursor",
    response_model=ConnectorSyncCursorSchema,
)
def update_sync_cursor(
    artist_id: str,
    integration: str,
    body: SyncCursorUpdateRequest,
    db: Session = Depends(get_db),
):
    """Advance the sync cursor after a successful fetch."""
    return upsert_sync_cursor(
        artist_id=artist_id,
        integration=integration,
        cursor_value=body.cursor_value,
        db=db,
    )
