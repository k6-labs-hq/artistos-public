from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CatalogGraphNode(Base):
    """Adjacency-list graph node persisted in Postgres for forensic catalog traversal."""

    __tablename__ = "catalog_graph_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    attributes_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class CatalogGraphEdge(Base):
    """Adjacency-list edge between graph nodes."""

    __tablename__ = "catalog_graph_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_node_id: Mapped[str] = mapped_column(String, ForeignKey("catalog_graph_nodes.id"), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(String, ForeignKey("catalog_graph_nodes.id"), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    attributes_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class CatalogGraphNodeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    node_type: str
    external_id: str
    label: str | None
    attributes_json: str
    created_at: datetime


class CatalogGraphEdgeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    attributes_json: str
    created_at: datetime
