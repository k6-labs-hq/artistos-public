from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.event import Event
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.services.modules import (
    AutoInferenceService,
    CatalogGraphService,
    ImmutableLedgerModuleService,
    RecoveryAutomationService,
    UniversalEventService,
    VarianceDetectionService,
)

# XR7 event flow (orchestrator-level):
# connect_accounts -> fetch_catalog/statements -> upload_statements -> parse_normalize
# -> build_catalog_graph -> confirm_catalog -> variance_detection
# -> generate_evidence_packets -> submit_recovery_actions -> append_immutable_ledger


@dataclass
class WorkflowRunResult:
    artist_id: str
    steps: list[dict[str, Any]]


class XR7WorkflowService:
    """Runs the baseline XR7 end-to-end workflow in one orchestrated operation."""

    def __init__(self, db: Session):
        self.db = db

    def _artist_or_404(self, artist_id: str) -> Artist:
        artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise ValueError("Artist not found")
        return artist

    def run(self, artist_id: str) -> WorkflowRunResult:
        self._artist_or_404(artist_id)
        steps: list[dict[str, Any]] = []

        # Step 1: fetch graph inputs from existing data.
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        statements = self.db.query(Statement).filter(Statement.artist_id == artist_id).all()
        graph = CatalogGraphService(self.db).build_and_persist(
            artist_id,
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
        steps.append({"name": "build_catalog_graph", "nodes": len(graph.get("nodes") or [])})

        # Step 2: infer missing catalog relationships.
        inference = AutoInferenceService().infer(
            [{"work_id": w.id, "contributors": [], "streams": 0.0, "owner": artist_id} for w in works]
        )
        steps.append({"name": "infer_catalog", "count": inference.get("count", 0)})

        # Step 3: variance scan from basic event projections.
        events = self.db.query(Event).filter(Event.artist_id == artist_id).limit(1000).all()
        variance_rows = [
            {
                "streams": float(e.quantity or 0.0),
                "payout": float((e.quantity or 0.0) * (e.unit_value or 0.0)),
                "expected_payout": float((e.quantity or 0.0) * (e.unit_value or 0.0) * 1.2),
                "has_registration": True,
                "reported_usage": float(e.quantity or 0.0),
            }
            for e in events
        ]
        variance = VarianceDetectionService().run(variance_rows)
        steps.append({"name": "variance_scan", "findings": variance.get("finding_count", 0)})

        # Step 4: persist universal events from current events (normalization bridge).
        universal_rows = [
            {
                "artist_id": artist_id,
                "source_type": "event",
                "source_name": e.platform or "unknown",
                "record_type": "EVENT",
                "event_type": str(e.event_type),
                "amount": float((e.quantity or 0.0) * (e.unit_value or 0.0)),
                "quantity": float(e.quantity or 0.0),
                "unit_value": float(e.unit_value or 0.0),
                "currency": e.currency or "USD",
                "territory": e.territory,
                "work_id": None,
                "work_title": None,
                "isrc": None,
                "metadata": {"event_id": e.id},
            }
            for e in events
        ]
        persisted = UniversalEventService(self.db).persist_many(universal_rows) if universal_rows else 0
        steps.append({"name": "persist_universal_events", "count": persisted})

        # Step 5: recovery automation + immutable ledger.
        findings = variance.get("findings") or []
        recovery = RecoveryAutomationService().run(artist_id, findings[:25])
        ledger_service = ImmutableLedgerModuleService(self.db)
        ledger = ledger_service.append(
            artist_id,
            "workflow_run",
            {
                "steps": steps,
                "recovery": recovery,
            },
        )
        steps.append({"name": "ledger_append", "entry_hash": ledger.entry_hash})

        return WorkflowRunResult(artist_id=artist_id, steps=steps)

    def preview(self, artist_id: str) -> dict[str, Any]:
        self._artist_or_404(artist_id)
        works = self.db.query(Work).filter(Work.artist_id == artist_id).count()
        statements = self.db.query(Statement).filter(Statement.artist_id == artist_id).count()
        events = self.db.query(Event).filter(Event.artist_id == artist_id).count()
        return {
            "artist_id": artist_id,
            "inputs": {
                "works": works,
                "statements": statements,
                "events": events,
            },
            "orchestration_steps": [
                "connect_accounts",
                "fetch_catalog_and_statements",
                "upload_statements",
                "parse_and_normalize",
                "build_catalog_graph",
                "confirm_catalog",
                "variance_detection",
                "evidence_packets",
                "recovery_automation",
                "immutable_ledger_logging",
            ],
        }
