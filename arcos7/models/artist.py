import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    ipi_number: Mapped[str | None] = mapped_column(String, nullable=True)
    stage_names: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.utcnow())


class ArtistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    ipi_number: str | None = None
    stage_names: list[str] | None = None
    created_at: datetime


class ArtistCreate(BaseModel):
    name: str
    ipi_number: str | None = None
    stage_names: list[str] | None = None
