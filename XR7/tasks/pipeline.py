from __future__ import annotations

from datetime import datetime, timezone

from XR7.celery_app import celery_app
from XR7.ingestion.sync_jobs import run_sync_job
from XR7.models.anomaly import Anomaly
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.statement import Statement
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.catalog_graph_adjacency import CatalogGraphAdjacencyService
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _ledger_event(db, artist_id: str, event_type: str, payload: dict) -> None:
    ImmutableLedgerService(db).append(artist_id, event_type, payload)


@celery_app.task(name="xr7.pipeline.ingest_file", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def ingest_file(self, statement_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        statement = db.query(Statement).filter(Statement.id == statement_id).first()
        if not statement:
            raise ValueError("statement not found")
        logger.info("ingest_file started", extra={"statement_id": statement_id})
        _ledger_event(db, statement.artist_id, "ingest_file", {"statement_id": statement.id, "status": statement.status})
        return {"statement_id": statement.id, "status": statement.status}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.parse_statement", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def parse_statement(self, statement_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        statement = db.query(Statement).filter(Statement.id == statement_id).first()
        if not statement:
            raise ValueError("statement not found")
        logger.info("parse_statement started", extra={"statement_id": statement_id})
        _ledger_event(
            db,
            statement.artist_id,
            "parse_statement",
            {"statement_id": statement.id, "format_detected": statement.format_detected, "events_created": statement.events_created},
        )
        return {"statement_id": statement.id, "parsed": True, "events_created": statement.events_created}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.build_catalog_graph", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def build_catalog_graph(self, artist_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        logger.info("build_catalog_graph started", extra={"artist_id": artist_id})
        graph = CatalogGraphAdjacencyService(db).fetch(artist_id)
        _ledger_event(db, artist_id, "build_catalog_graph", {"node_count": len(graph.nodes), "edge_count": len(graph.edges)})
        return {"artist_id": artist_id, "node_count": len(graph.nodes), "edge_count": len(graph.edges)}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.run_variance_detection", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_variance_detection(self, artist_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        rows = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        logger.info("run_variance_detection started", extra={"artist_id": artist_id, "existing": len(rows)})
        _ledger_event(db, artist_id, "run_variance_detection", {"variance_events": len(rows)})
        return {"artist_id": artist_id, "variance_events": len(rows)}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.generate_evidence_packet", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_evidence_packet(self, claim_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError("claim not found")
        evidence = claim.evidence or {}
        evidence["generated_at"] = datetime.now(timezone.utc).isoformat()
        claim.evidence = evidence
        db.commit()
        _ledger_event(db, claim.artist_id, "generate_evidence_packet", {"claim_id": claim.id})
        return {"claim_id": claim.id, "generated": True}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.submit_recovery_action", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def submit_recovery_action(self, claim_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError("claim not found")
        claim.status = ClaimStatus.IN_REVIEW
        claim.updated_at = datetime.now(timezone.utc)
        db.commit()
        _ledger_event(db, claim.artist_id, "submit_recovery_action", {"claim_id": claim.id, "status": str(claim.status)})
        return {"claim_id": claim.id, "status": str(claim.status)}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.run_sync_job", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_sync_job_task_alias(self, job_id: str) -> str:  # noqa: ANN001
    """Alias task to bridge queue events into existing sync job execution logic."""
    run_sync_job(job_id)
    return job_id