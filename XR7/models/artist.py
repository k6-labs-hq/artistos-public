import uuid
from datetime import datetime, timezone
import enum
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ArtistLifecycleStatus(str, enum.Enum):
    NEW = "NEW"
    ONBOARDED = "ONBOARDED"
    ACTIVE = "ACTIVE"


class Artist(Base):
    __tablename__ = "artists"
    __table_args__ = (
        CheckConstraint(
            "is_founder = 0 OR contingency_fee_percent <= 10",
            name="ck_artists_founder_fee_max",
        ),
    )

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
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=False, default="US")
    trolley_recipient_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payout_account_status: Mapped[str] = mapped_column(String, nullable=False, default="not_started")
    payout_method_type: Mapped[str | None] = mapped_column(String, nullable=True)
    payout_last4: Mapped[str | None] = mapped_column(String, nullable=True)
    tax_form_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    default_attorney_grace_period_days: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    primary_jurisdiction: Mapped[str] = mapped_column(String, nullable=False, default="USA")
    preferred_contract_type: Mapped[str] = mapped_column(String, nullable=False, default="recording")
    xr7_future_leakage_prevented: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_founder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    founder_slot_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    founder_locked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    contingency_fee_percent: Mapped[float | None] = mapped_column(Float, nullable=True)


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
    first_name: str | None = None
    last_name: str | None = None
    country_code: str = "US"
    trolley_recipient_id: str | None = None
    payout_account_status: str = "not_started"
    payout_method_type: str | None = None
    payout_last4: str | None = None
    tax_form_status: str = "pending"
    default_attorney_grace_period_days: int = 60
    primary_jurisdiction: str = "USA"
    preferred_contract_type: str = "recording"
    xr7_future_leakage_prevented: float = 0.0
    is_founder: bool = False
    founder_slot_number: int | None = None
    founder_locked_at: datetime | None = None
    contingency_fee_percent: float | None = None


class ArtistCreate(BaseModel):
    name: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    country_code: str = "US"
    role: str | None = None
    ipi_number: str | None = None
    stage_names: list[str] | None = None
    default_attorney_grace_period_days: int = 60
    primary_jurisdiction: str = "USA"
    preferred_contract_type: str = "recording"
