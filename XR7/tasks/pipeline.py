from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from XR7.celery_app import celery_app
from XR7.ingestion.sync_jobs import run_sync_job
from XR7.models.anomaly import Anomaly
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.artist import Artist
from XR7.models.contract import Contract
from XR7.models.notification_preference import NotificationPreference
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.weekly_digest import build_weekly_digest, deliver_weekly_digest
from XR7.services.catalog_graph_adjacency import CatalogGraphAdjacencyService
from XR7.services.ml_feedback import aggregate_feedback_and_update_calibration
from XR7.llm.claim_drafter import claim_drafter
from XR7.ml.catalog_auditor import CatalogAuditor
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
        try:
            run_catalog_audit.delay(statement.artist_id)
        except Exception:  # noqa: BLE001
            logger.exception("Unable to enqueue catalog audit task")
        return {"statement_id": statement.id, "parsed": True, "events_created": statement.events_created}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.llm_generate_demand_letter", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def llm_generate_demand_letter_task(self, claim_id: str, anomaly: dict, evidence: dict, artist_id: str) -> dict:  # noqa: ANN001
    """Generate and persist demand-letter markdown asynchronously."""
    db = SessionLocal()
    try:
        markdown = claim_drafter.generate_demand_letter(anomaly, evidence, artist_id)
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            claim.evidence = claim.evidence or {}
            claim.evidence.setdefault("llm_outputs", {})
            claim.evidence["llm_outputs"]["demand_letter_markdown"] = markdown
            claim.evidence["llm_outputs"]["demand_letter_task_generated"] = datetime.now(timezone.utc).isoformat()
            db.commit()
        return {"claim_id": claim_id, "generated": bool(markdown)}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.llm_generate_negotiation_script", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def llm_generate_negotiation_script_task(self, claim_id: str, claim_payload: dict) -> dict:  # noqa: ANN001
    """Generate and persist negotiation script asynchronously."""
    db = SessionLocal()
    try:
        script = claim_drafter.generate_negotiation_script(claim_payload)
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            claim.evidence = claim.evidence or {}
            claim.evidence.setdefault("llm_outputs", {})
            claim.evidence["llm_outputs"]["negotiation_script"] = script
            claim.evidence["llm_outputs"]["negotiation_script_task_generated"] = datetime.now(timezone.utc).isoformat()
            db.commit()
        return {"claim_id": claim_id, "generated": bool(script)}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.llm_generate_advice", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def llm_generate_advice_task(self, artist_id: str, dashboard: dict, history: list[dict]) -> dict:  # noqa: ANN001
    """Generate advice asynchronously for warm-cache or batch usage."""
    advice = claim_drafter.generate_personalized_advice({**dashboard, "conversation_history": history[-10:]})
    return {"artist_id": artist_id, "generated": bool(advice), "length": len(advice or "")}


@celery_app.task(name="xr7.pipeline.run_catalog_audit", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_catalog_audit(self, artist_id: str) -> dict:  # noqa: ANN001
    """Run catalog auditor and return structured catalog_health payload."""
    db = SessionLocal()
    try:
        audit = asyncio.run(CatalogAuditor(db).run(artist_id))
        _ledger_event(db, artist_id, "run_catalog_audit", {"issue_count": len(audit.get("issues") or [])})
        return audit
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


@celery_app.task(name="xr7.pipeline.aggregate_feedback_calibration", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def aggregate_feedback_calibration(self, artist_id: str) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        summary = aggregate_feedback_and_update_calibration(artist_id, db)
        _ledger_event(db, artist_id, "aggregate_feedback_calibration", summary)
        return summary
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.aggregate_feedback_calibration_all", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def aggregate_feedback_calibration_all(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist_ids = [a.id for a in db.query(Artist.id).all()]
        summaries = []
        for artist_id in artist_ids:
            summaries.append(aggregate_feedback_and_update_calibration(artist_id, db))
        return {"artist_count": len(artist_ids), "summaries": summaries[:100]}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.auto_escalate_claims", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def auto_escalate_claims(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artists = db.query(Artist).all()
        escalated = 0
        for artist in artists:
            anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist.id).all()
            claims = db.query(Claim).filter(Claim.artist_id == artist.id).all()
            contracts = db.query(Contract).filter(Contract.artist_id == artist.id).all()
            payments = db.query(Payment).filter(Payment.artist_id == artist.id).all()

            risk = evaluate_deadline_risk(
                anomalies=[
                    {
                        "id": a.id,
                        "category": str(a.category),
                        "subtype": a.subtype,
                        "territory": a.territory,
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                        "estimated_recoverable": float(a.estimated_recoverable or 0.0),
                    }
                    for a in anomalies
                ],
                claims=[
                    {
                        "id": c.id,
                        "status": str(c.status),
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    }
                    for c in claims
                ],
                contracts=[{"id": c.id, "terms": c.terms or {}, "territory": c.territory} for c in contracts],
                payments=[{"id": p.id, "amount": p.amount, "source": p.source} for p in payments],
            )
            if risk.get("risk_color") != "RED":
                continue

            for claim in claims:
                if str(claim.status) in {"SUBMITTED", "FILED"}:
                    claim.status = ClaimStatus.IN_REVIEW
                    escalated += 1
            _ledger_event(db, artist.id, "auto_escalate_claims", {"risk": risk, "escalated_claims": escalated})
        db.commit()
        return {"escalated_claims": escalated}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.notify_deadline_risk", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def notify_deadline_risk(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artists = db.query(Artist).all()
        notified = 0
        for artist in artists:
            anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist.id).all()
            claims = db.query(Claim).filter(Claim.artist_id == artist.id).all()
            contracts = db.query(Contract).filter(Contract.artist_id == artist.id).all()
            payments = db.query(Payment).filter(Payment.artist_id == artist.id).all()
            pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist.id).first()

            risk = evaluate_deadline_risk(
                anomalies=[{"id": a.id, "category": str(a.category), "subtype": a.subtype, "created_at": a.created_at.isoformat() if a.created_at else None} for a in anomalies],
                claims=[{"id": c.id, "status": str(c.status), "created_at": c.created_at.isoformat() if c.created_at else None} for c in claims],
                contracts=[{"id": c.id, "terms": c.terms or {}} for c in contracts],
                payments=[{"id": p.id, "amount": p.amount} for p in payments],
            )

            if risk.get("risk_color") in {"RED", "YELLOW"} and pref and pref.notify_urgent_sol:
                _ledger_event(db, artist.id, "deadline_risk_notification", risk)
                notified += 1
        return {"artists_notified": notified}
    finally:
        db.close()


@celery_app.task(name="xr7.pipeline.weekly_artist_digest", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def weekly_artist_digest(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artists = db.query(Artist).all()
        sent = 0
        for artist in artists:
            anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist.id).all()
            claims = db.query(Claim).filter(Claim.artist_id == artist.id).all()
            contracts = db.query(Contract).filter(Contract.artist_id == artist.id).all()
            payments = db.query(Payment).filter(Payment.artist_id == artist.id).all()
            pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == artist.id).first()

            digest = build_weekly_digest(
                artist_id=artist.id,
                anomalies=anomalies,
                claims=claims,
                contracts=[{"id": c.id, "terms": c.terms or {}, "territory": c.territory} for c in contracts],
                payments=[{"id": p.id, "amount": p.amount, "source": p.source} for p in payments],
            )
            delivered = deliver_weekly_digest(
                digest,
                pref,
                email=(pref.email if pref else artist.email),
                sms_number=(pref.phone if pref else None),
            )
            _ledger_event(db, artist.id, "weekly_artist_digest", {"delivery": delivered, "digest": digest})
            sent += 1
        return {"artists_processed": len(artists), "digests_sent": sent}
    finally:
        db.close()