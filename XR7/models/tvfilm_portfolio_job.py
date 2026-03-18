from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class TVFilmPortfolioJobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class TVFilmPortfolioJob(Base):
    __tablename__ = "tvfilm_portfolio_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    uploaded_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    roster_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(Enum(TVFilmPortfolioJobStatus), nullable=False, default=TVFilmPortfolioJobStatus.QUEUED)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TVFilmPortfolioJobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_name: str
    entity_type: str
    uploaded_filename: str | None = None
    roster_size: int
    status: TVFilmPortfolioJobStatus
    summary_json: str
    created_at: datetime
    updated_at: datetime
