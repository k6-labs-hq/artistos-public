from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.ingestion.connectors.oauth_providers import PROVIDER_CONFIGS, OAuthProviderService
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.forensic_universal_event import (
    ForensicUniversalRoyaltyEvent,
    ForensicUniversalRoyaltyEventCreate,
    ForensicUniversalRoyaltyEventSchema,
)
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry, ImmutableLedgerEntrySchema
from XR7.models.statement import Statement
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.catalog_graph_adjacency import CatalogGraphAdjacencyService, build_minimal_catalog_graph
from XR7.tasks.pipeline import submit_recovery_action

router = APIRouter(tags=["forensic-api"])


class AuthConnectResponse(BaseModel):
    provider: str
    authorization_url: str
    configured: bool
    state: str


class CatalogConfirmRequest(BaseModel):
    artist_id: str
    works: list[dict[str, Any]] = Field(default_factory=list)


class RecoverySubmitResponse(BaseModel):
    claim_id: str
    status: str
    queued: bool
    task_id: str | None = None


@router.get("/auth/providers")
async def auth_providers() -> dict[str, list[dict[str, Any]]]:
    providers: list[dict[str, Any]] = []
    for provider_name, config in sorted(PROVIDER_CONFIGS.items()):
        service = OAuthProviderService(provider_name)
        providers.append(
            {
                "provider": provider_name,
                "authorize_url": config.authorize_url,
                "token_url": config.token_url,
                "default_scopes": list(config.default_scopes),
                "configured": service.configured(),
            }
        )
    return {"providers": providers}


@router.post("/auth/connect/{provider}", response_model=AuthConnectResponse)
async def auth_connect(provider: str, redirect_uri: str = Query(..., min_length=5)) -> AuthConnectResponse:
    service = OAuthProviderService(provider)
    if provider.strip().lower() not in PROVIDER_CONFIGS:
        raise HTTPException(status_code=404, detail="Unsupported OAuth provider")
    state = str(uuid.uuid4())
    url = service.build_authorization_url(redirect_uri=redirect_uri, state=state, scopes=[], tenant_id="default")
    return AuthConnectResponse(provider=provider.strip().lower(), authorization_url=url, configured=service.configured(), state=state)


@router.post("/statements/upload", response_model=ForensicUniversalRoyaltyEventSchema, status_code=201)
async def statements_upload(payload: ForensicUniversalRoyaltyEventCreate, db: Session = Depends(get_db)):
    """Minimal statement upload endpoint that stores a normalized universal event row."""
    row = ForensicUniversalRoyaltyEvent(
        event_id=str(uuid.uuid4()),
        work_id=payload.work_id,
        isrc=payload.isrc,
        iswc=payload.iswc,
        title=payload.title,
        artist_name=payload.artist_name,
        writer_name=payload.writer_name,
        publisher_name=payload.publisher_name,
        distributor=payload.distributor,
        platform=payload.platform,
        usage_type=payload.usage_type,
        usage_count=payload.usage_count,
        payout_amount=payload.payout_amount,
        payout_currency=payload.payout_currency,
        statement_period_start=payload.statement_period_start,
        statement_period_end=payload.statement_period_end,
        source_file_id=payload.source_file_id,
        confidence_score=payload.confidence_score,
        metadata_flags=json.dumps(payload.metadata_flags or {}, sort_keys=True),
        ingestion_timestamp=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/statements/{statement_id}/status")
async def statements_status(statement_id: str, db: Session = Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return {
        "statement_id": statement.id,
        "artist_id": statement.artist_id,
        "status": statement.status,
        "format_detected": statement.format_detected,
        "events_created": statement.events_created,
        "payments_created": statement.payments_created,
        "uploaded_at": statement.uploaded_at,
    }


@router.get("/catalog")
async def get_catalog(artist_id: str = Query(...), db: Session = Depends(get_db)):
    graph = CatalogGraphAdjacencyService(db).fetch(artist_id)
    return {"artist_id": artist_id, "nodes": graph.nodes, "edges": graph.edges}


@router.post("/catalog/confirm")
async def confirm_catalog(payload: CatalogConfirmRequest, db: Session = Depends(get_db)):
    graph_payload = build_minimal_catalog_graph(payload.works)
    summary = CatalogGraphAdjacencyService(db).persist(payload.artist_id, graph_payload)
    ImmutableLedgerService(db).append(
        payload.artist_id,
        "catalog_confirmed",
        {"works": len(payload.works), "created_nodes": summary["created_nodes"], "created_edges": summary["created_edges"]},
    )
    return {"artist_id": payload.artist_id, **summary}


@router.get("/variance")
async def list_variance(artist_id: str = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.query(Anomaly)
        .filter(Anomaly.artist_id == artist_id)
        .order_by(Anomaly.created_at.desc())
        .all()
    )
    return {
        "artist_id": artist_id,
        "count": len(rows),
        "items": [
            {
                "id": a.id,
                "subtype": a.subtype,
                "severity": str(a.severity),
                "estimated_recoverable": a.estimated_recoverable,
                "status": str(a.status),
                "created_at": a.created_at,
            }
            for a in rows
        ],
    }


@router.get("/variance/{variance_id}/evidence")
async def variance_evidence(variance_id: str, db: Session = Depends(get_db)):
    row = db.query(Anomaly).filter(Anomaly.id == variance_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Variance event not found")
    return {
        "variance_id": row.id,
        "evidence": {
            "description": row.description,
            "expected_amount": row.expected_amount,
            "actual_amount": row.actual_amount,
            "confidence_score": row.confidence_score,
            "time_window_start": row.time_window_start,
            "time_window_end": row.time_window_end,
        },
    }


@router.post("/recovery/{claim_id}/submit", response_model=RecoverySubmitResponse)
async def recovery_submit(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.status = ClaimStatus.SUBMITTED
    claim.updated_at = datetime.now(timezone.utc)
    db.commit()

    queued = True
    task_id: str | None = None
    try:
        task_result = submit_recovery_action.delay(claim.id)
        task_id = task_result.id
    except Exception:
        # Keep the endpoint usable in local/test contexts without a running broker.
        queued = False

    ImmutableLedgerService(db).append(claim.artist_id, "recovery_submitted", {"claim_id": claim.id, "task_id": task_id})
    return RecoverySubmitResponse(claim_id=claim.id, status=str(claim.status), queued=queued, task_id=task_id)


@router.get("/ledger", response_model=list[ImmutableLedgerEntrySchema])
async def list_ledger(artist_id: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(ImmutableLedgerEntry)
        .filter(ImmutableLedgerEntry.artist_id == artist_id)
        .order_by(ImmutableLedgerEntry.created_at.desc())
        .all()
    )


@router.get("/ledger/{entry_id}", response_model=ImmutableLedgerEntrySchema)
async def get_ledger_entry(entry_id: str, db: Session = Depends(get_db)):
    row = db.query(ImmutableLedgerEntry).filter(ImmutableLedgerEntry.id == entry_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return row