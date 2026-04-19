import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from XR7.models.base import Base


class ArtistLifecycleStatus(str, enum.Enum):
    NEW = "NEW"
    ONBOARDED = "ONBOARDED"
    ACTIVE = "ACTIVE"


class Artist(Base):
    __tablename__ = "artists"
    __table_args__ = (
        CheckConstraint(
            "is_founder = 0 OR contingency_fee_percent <= 12",
            name="ck_artists_founder_fee_max",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    ipi_number: Mapped[str | None] = mapped_column(String, nullable=True)
    stage_names: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[str] = mapped_column(String, default=ArtistLifecycleStatus.NEW.value, index=True)
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    country_code: Mapped[str] = mapped_column(String, nullable=False, default="US")
    trolley_recipient_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payout_account_status: Mapped[str] = mapped_column(
        String, nullable=False, default="not_started"
    )
    payout_method_type: Mapped[str | None] = mapped_column(String, nullable=True)
    payout_last4: Mapped[str | None] = mapped_column(String, nullable=True)
    tax_form_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    default_attorney_grace_period_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60
    )
    primary_jurisdiction: Mapped[str] = mapped_column(String, nullable=False, default="USA")
    preferred_contract_type: Mapped[str] = mapped_column(
        String, nullable=False, default="recording"
    )
    xr7_future_leakage_prevented: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_founder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    founder_slot_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    founder_locked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    contingency_fee_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    primary_vertical: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    tvfilm_role: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    organization_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    enterprise_mode_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    @validates("contingency_fee_percent")
    def _validate_founders_circle_rate_lock(self, key: str, value: float | None) -> float | None:
        """Enforce immutability of contingency_fee_percent after Founders Circle lock.

        Business Rule: Founders Circle members (2,500 artist cap) receive a lifetime
        rate lock guarantee. Once `founder_locked_at` is set, the contingency fee
        cannot be changed - not even by admins or the artist themselves.

        This prevents rate manipulation that would undermine the Founders Circle
        value proposition and violates the explicit contract promise.

        Compliance: SOC 2 CC6.1 - Logical access controls (immutable financial terms)

        Raises:
            ValueError: If attempting to change fee after founder_locked_at is set

        Regulatory citation: 17 CFR § 270.22c-2 (anti-manipulation of fee schedules)
        """
        # First check: is this a Founders Circle member with a lock timestamp?
        if self.founder_locked_at is not None:
            # Retrieve the current value from the database
            # self.contingency_fee_percent references the ORM-managed value before this change
            current_value = self.contingency_fee_percent

            # Allow setting the same value (idempotent operation)
            if current_value is not None and value != current_value:
                raise ValueError(
                    f"Cannot modify contingency_fee_percent for Founders Circle member. "
                    f"Rate locked at {current_value}% since {self.founder_locked_at.isoformat()}. "
                    f"Attempted new value: {value}%. "
                    f"This violates the Founders Circle lifetime rate guarantee."
                )

        return value


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
    primary_vertical: str | None = None
    tvfilm_role: str | None = None
    organization_type: str | None = None
    enterprise_mode_enabled: bool = False


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
    primary_vertical: str | None = "MUSIC"
    tvfilm_role: str | None = None
    organization_type: str | None = None
    enterprise_mode_enabled: bool = False
