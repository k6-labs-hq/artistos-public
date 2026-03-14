from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.anomaly.variance_detection_engine import run_variance_scan
from XR7.graph.catalog_graph_builder import build_catalog_graph
from XR7.ingestion.fetchers import get_fetcher
from XR7.ingestion.file_ingestion_pipeline import FileIngestionPipeline
from XR7.ingestion.missing_data_detector import detect_missing_data
from XR7.ingestion.parser_engine import get_statement_parser
from XR7.ml.auto_inference_engine import infer_catalog_relationships
from XR7.models.catalog_confirmation import CatalogConfirmation
from XR7.models.catalog_graph import CatalogGraphSnapshot
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry
from XR7.models.universal_royalty_event import UniversalRoyaltyEvent
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.recovery.recovery_automation_engine import automate_recovery


class OAuthConnectorService:
    def __init__(self, db: Session):
        self.db = db


class DataFetcherService:
    def fetch(self, integration: str, artist_id: str):
        return get_fetcher(integration).fetch_all(artist_id)


class PermissionsDashboardService:
    @staticmethod
    def health(is_active: bool) -> str:
        return "healthy" if is_active else "disconnected"


class FileIngestionService:
    def process(self, uploads: list[tuple[str, bytes]], strict_validation: bool = True):
        return FileIngestionPipeline().process(uploads, strict_validation=strict_validation)


class StatementParserService:
    def parse(self, parser_type: str, content: bytes, artist_id: str, filename: str):
        parser = get_statement_parser(parser_type)
        return parser.parse(content, artist_id, filename)


class MissingDataService:
    def detect(self, *, connected_sources, catalog_rows, registration_rows, usage_rows):
        return detect_missing_data(
            connected_sources=connected_sources,
            catalog_rows=catalog_rows,
            registration_rows=registration_rows,
            usage_rows=usage_rows,
        )


class CatalogGraphService:
    def __init__(self, db: Session):
        self.db = db

    def build_and_persist(self, artist_id: str, *, works: list[dict[str, Any]], registrations: list[dict[str, Any]], statements: list[dict[str, Any]]) -> dict[str, Any]:
        graph = build_catalog_graph(works=works, registrations=registrations, statements=statements)
        snapshot = CatalogGraphSnapshot(
            artist_id=artist_id,
            graph_version="xr7.catalog_graph.v1",
            nodes_json=json.dumps(graph.get("nodes") or [], sort_keys=True),
            edges_json=json.dumps(graph.get("edges") or [], sort_keys=True),
            duplicates_json=json.dumps(graph.get("duplicates") or [], sort_keys=True),
            missing_metadata_json=json.dumps(graph.get("missing_metadata") or [], sort_keys=True),
            ownership_conflicts_json=json.dumps(graph.get("ownership_conflicts") or [], sort_keys=True),
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(snapshot)
        self.db.commit()
        return graph


class CatalogConfirmationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> CatalogConfirmation:
        row = CatalogConfirmation(**kwargs)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class AutoInferenceService:
    def infer(self, rows: list[dict[str, Any]]):
        return infer_catalog_relationships(rows)


class VarianceDetectionService:
    def run(self, rows: list[dict[str, Any]]):
        return run_variance_scan(rows)


class EvidencePacketService:
    def __init__(self, db: Session):
        self.db = db
        self.ledger = ImmutableLedgerService(db)

    def persist_packet_ledger(self, artist_id: str, packet: dict[str, Any]) -> ImmutableLedgerEntry:
        return self.ledger.append(artist_id, "evidence_packet", packet)


class RecoveryAutomationService:
    def run(self, artist_id: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
        return automate_recovery(artist_id, findings)


class ImmutableLedgerModuleService:
    def __init__(self, db: Session):
        self.db = db
        self.ledger = ImmutableLedgerService(db)

    def append(self, artist_id: str, entry_type: str, payload: dict[str, Any]):
        return self.ledger.append(artist_id, entry_type, payload)


class UniversalEventService:
    def __init__(self, db: Session):
        self.db = db

    def persist_many(self, rows: list[dict[str, Any]]) -> int:
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
