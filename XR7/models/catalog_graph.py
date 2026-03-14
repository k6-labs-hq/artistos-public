from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CatalogGraphSnapshot(Base):
    __tablename__ = "catalog_graph_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    graph_version: Mapped[str] = mapped_column(String, nullable=False, default="xr7.catalog_graph.v1")
    nodes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    edges_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    duplicates_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    missing_metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    ownership_conflicts_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class CatalogGraphSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    graph_version: str
    nodes_json: str
    edges_json: str
    duplicates_json: str
    missing_metadata_json: str
    ownership_conflicts_json: str
    created_at: datetime
