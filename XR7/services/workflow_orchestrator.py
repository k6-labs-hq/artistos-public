from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from XR7.anomaly.variance_detection_engine import run_variance_scan
from XR7.core.workflow.variance_rows import event_to_universal_row, event_to_variance_row
from XR7.graph.catalog_graph_builder import build_catalog_graph
from XR7.ml.auto_inference_engine import infer_catalog_relationships
from XR7.models.artist import Artist
from XR7.models.catalog_graph import CatalogGraphSnapshot
from XR7.models.event import Event
from XR7.models.statement import Statement
from XR7.models.universal_royalty_event import UniversalRoyaltyEvent
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.recovery.recovery_automation_engine import automate_recovery

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

    def _build_and_persist_catalog_graph(
        self,
        artist_id: str,
        *,
        works: list[dict[str, Any]],
        registrations: list[dict[str, Any]],
        statements: list[dict[str, Any]],
    ) -> dict[str, Any]:
        graph = build_catalog_graph(works=works, registrations=registrations, statements=statements)
        snapshot = CatalogGraphSnapshot(
            artist_id=artist_id,
            nodes_json=json.dumps(graph.get("nodes", []), default=str),
            edges_json=json.dumps(graph.get("edges", []), default=str),
            duplicates_json=json.dumps(graph.get("duplicates", []), default=str),
            missing_metadata_json=json.dumps(graph.get("missing_metadata", []), default=str),
            ownership_conflicts_json=json.dumps(graph.get("ownership_conflicts", []), default=str),
        )
        self.db.add(snapshot)
        self.db.commit()
        return graph

    def _persist_universal_events(self, rows: list[dict[str, Any]]) -> int:
        count = 0
        for row in rows:
            self.db.add(
                UniversalRoyaltyEvent(
                    artist_id=row["artist_id"],
                    source_type=row["source_type"],
                    source_name=row["source_name"],
                    record_type=row["record_type"],
                    event_type=row["event_type"],
                    amount=float(row.get("amount") or 0.0),
                    quantity=float(row.get("quantity") or 0.0),
                    unit_value=float(row.get("unit_value") or 0.0),
                    currency=row.get("currency") or "USD",
                    territory=row.get("territory"),
                    work_id=row.get("work_id"),
                    work_title=row.get("work_title"),
                    isrc=row.get("isrc"),
                    ipi=row.get("ipi"),
                    statement_period=row.get("statement_period"),
                    source_ref=row.get("source_ref"),
                    metadata_json=json.dumps(row.get("metadata") or {}, sort_keys=True),
                )
            )
            count += 1
        self.db.commit()
        return count

    def run(self, artist_id: str) -> WorkflowRunResult:
        self._artist_or_404(artist_id)
        steps: list[dict[str, Any]] = []

        # Step 1: fetch graph inputs from existing data.
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        statements = self.db.query(Statement).filter(Statement.artist_id == artist_id).all()
        graph = self._build_and_persist_catalog_graph(
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
            registrations=[
                {"registration_id": w.iswc, "work_id": w.id, "source": "internal"} for w in works
            ],
            statements=[
                {"statement_id": s.id, "work_id": None, "source": s.format_detected}
                for s in statements
            ],
        )
        steps.append({"name": "build_catalog_graph", "nodes": len(graph.get("nodes") or [])})

        # Step 2: infer missing catalog relationships.
        inference = infer_catalog_relationships(
            [
                {"work_id": w.id, "contributors": [], "streams": 0.0, "owner": artist_id}
                for w in works
            ]
        )
        steps.append({"name": "infer_catalog", "count": inference.get("count", 0)})

        # Step 3: variance scan from basic event projections.
        events = self.db.query(Event).filter(Event.artist_id == artist_id).limit(1000).all()
        variance_rows = [
            event_to_variance_row(
                float(e.quantity or 0.0),
                float(e.unit_value or 0.0),
            )
            for e in events
        ]
        variance = run_variance_scan(variance_rows)
        steps.append({"name": "variance_scan", "findings": variance.get("finding_count", 0)})

        # Step 4: persist universal events from current events (normalization bridge).
        universal_rows = [
            event_to_universal_row(
                artist_id=artist_id,
                source_name=e.platform or "unknown",
                event_type=str(e.event_type),
                amount=float((e.quantity or 0.0) * (e.unit_value or 0.0)),
                quantity=float(e.quantity or 0.0),
                unit_value=float(e.unit_value or 0.0),
                currency=e.currency or "USD",
                territory=e.territory,
                event_id=e.id,
            )
            for e in events
        ]
        persisted = self._persist_universal_events(universal_rows) if universal_rows else 0
        steps.append({"name": "persist_universal_events", "count": persisted})

        # Step 5: recovery automation + immutable ledger.
        findings = variance.get("findings") or []
        recovery = automate_recovery(artist_id, findings[:25])
        ledger = ImmutableLedgerService(self.db).append(
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
