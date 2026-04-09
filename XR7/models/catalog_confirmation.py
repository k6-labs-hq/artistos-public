from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CatalogConfirmation(Base):
    __tablename__ = "catalog_confirmations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    work_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ownership_confirmed: Mapped[str] = mapped_column(String, default="pending")
    splits_confirmed: Mapped[str] = mapped_column(String, default="pending")
    publisher_confirmed: Mapped[str] = mapped_column(String, default="pending")
    admin_confirmed: Mapped[str] = mapped_column(String, default="pending")
    correction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class CatalogConfirmationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    work_id: str
    ownership_confirmed: str
    splits_confirmed: str
    publisher_confirmed: str
    admin_confirmed: str
    correction_notes: str | None
    confirmed_at: datetime
