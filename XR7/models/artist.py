import uuid
from datetime import datetime, timezone
import enum
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ArtistLifecycleStatus(str, enum.Enum):
    NEW = "NEW"
    ONBOARDED = "ONBOARDED"
    ACTIVE = "ACTIVE"


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    ipi_number: Mapped[str | None] = mapped_column(String, nullable=True)
    stage_names: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String, default=ArtistLifecycleStatus.NEW.value, index=True)
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # Celero Commerce — Merchant of Record
    # Populated when the artist is registered via POST /artists/{id}/celero/register
    celero_customer_vault_id: Mapped[str | None] = mapped_column(String, nullable=True)
    default_attorney_grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    primary_jurisdiction: Mapped[str] = mapped_column(String, nullable=False, default="USA")
    preferred_contract_type: Mapped[str] = mapped_column(String, nullable=False, default="recording")
    xr7_future_leakage_prevented: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class ArtistSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str | None = None
    role: str | None = None
    ipi_number: str | None = None
    stage_names: list[str] | None = None
    created_at: datetime
    status: ArtistLifecycleStatus
    onboarded_at: datetime | None = None
    activated_at: datetime | None = None
    celero_customer_vault_id: str | None = None
    default_attorney_grace_period_days: int = 60
    primary_jurisdiction: str = "USA"
    preferred_contract_type: str = "recording"
    xr7_future_leakage_prevented: float = 0.0


class ArtistCreate(BaseModel):
    name: str
    email: str | None = None
    role: str | None = None
    ipi_number: str | None = None
    stage_names: list[str] | None = None
    default_attorney_grace_period_days: int = 60
    primary_jurisdiction: str = "USA"
    preferred_contract_type: str = "recording"
