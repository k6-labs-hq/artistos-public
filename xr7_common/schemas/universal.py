from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class UniversalRoyaltyEventSchema(BaseModel):
    schema_version: str = "xr7.universal.royalty_event.v1"
    artist_id: str
    source_type: str
    source_name: str
    record_type: str
    event_type: str
    amount: float = 0.0
    quantity: float = 0.0
    unit_value: float = 0.0
    currency: str = "USD"
    territory: str | None = None
    work_id: str | None = None
    work_title: str | None = None
    isrc: str | None = None
    ipi: str | None = None
    statement_period: str | None = None
    source_ref: str | None = None
    ingested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class XR7UniversalRoyaltyEventSchema(BaseModel):
    """Forensic universal event schema with explicit XR7 contract field names."""

    event_id: str
    work_id: str | None = None
    isrc: str | None = None
    iswc: str | None = None
    title: str | None = None
    artist_name: str | None = None
    writer_name: str | None = None
    publisher_name: str | None = None
    distributor: str | None = None
    platform: str | None = None
    usage_type: str | None = None
    usage_count: int = 0
    payout_amount: float = 0.0
    payout_currency: str = "USD"
    statement_period_start: str | None = None
    statement_period_end: str | None = None
    source_file_id: str | None = None
    confidence_score: float = 0.0
    metadata_flags: dict[str, Any] = Field(default_factory=dict)
    ingestion_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CatalogGraphNodeSchema(BaseModel):
    id: str
    node_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class CatalogGraphEdgeSchema(BaseModel):
    source_id: str
    target_id: str
    edge_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class CatalogGraphSchema(BaseModel):
    artist_id: str
    graph_version: str = "xr7.catalog_graph.v1"
    nodes: list[CatalogGraphNodeSchema] = Field(default_factory=list)
    edges: list[CatalogGraphEdgeSchema] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


UNIVERSAL_ROYALTY_EVENT_EXAMPLE: dict[str, Any] = {
    "schema_version": "xr7.universal.royalty_event.v1",
    "artist_id": "artist-123",
    "source_type": "distributor",
    "source_name": "spotify",
    "record_type": "STATEMENT",
    "event_type": "ROYALTY_EVENT",
    "amount": 142.56,
    "quantity": 35234,
    "unit_value": 0.004046,
    "currency": "USD",
    "territory": "US",
    "work_id": "work-1",
    "work_title": "Midnight Tape",
    "isrc": "USAAA1234567",
    "ipi": None,
    "statement_period": "2026-01",
    "source_ref": "statement-row-42",
    "ingested_at": "2026-03-14T00:00:00+00:00",
    "metadata": {"provider_statement_id": "st-2026-01"},
}

CATALOG_GRAPH_EXAMPLE: dict[str, Any] = {
    "artist_id": "artist-123",
    "graph_version": "xr7.catalog_graph.v1",
    "generated_at": "2026-03-14T00:00:00+00:00",
    "nodes": [
        {
            "id": "work-1",
            "node_type": "work",
            "attributes": {"title": "Midnight Tape", "isrc": "USAAA1234567"},
        },
        {
            "id": "reg-1",
            "node_type": "registration",
            "attributes": {"registration_id": "iswc:T-000.000.001-0"},
        },
    ],
    "edges": [
        {
            "source_id": "work-1",
            "target_id": "reg-1",
            "edge_type": "registered_in",
            "attributes": {},
        },
    ],
}
