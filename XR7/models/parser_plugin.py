from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ParserPlugin(Base):
    __tablename__ = "parser_plugins"
    __table_args__ = (
        UniqueConstraint("artist_id", "parser_type", name="uq_parser_plugin_artist_type"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    parser_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    plugin_name: Mapped[str] = mapped_column(String, nullable=False)
    plugin_entrypoint: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class ParserPluginSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    parser_type: str
    plugin_name: str
    plugin_entrypoint: str
    enabled: bool
    created_at: datetime
    updated_at: datetime
