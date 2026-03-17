from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class TrolleyTxnType(str, enum.Enum):
    REMITTANCE = "REMITTANCE"
    DISBURSEMENT = "DISBURSEMENT"


class TrolleyTxnStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAID = "PAID"
    FAILED = "FAILED"
    RETURNED = "RETURNED"


class TrolleyTransaction(Base):
    __tablename__ = "trolley_transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False, index=True)
    claim_id: Mapped[str | None] = mapped_column(String, ForeignKey("claims.id"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(Enum(TrolleyTxnType), nullable=False)
    status: Mapped[str] = mapped_column(Enum(TrolleyTxnStatus), nullable=False, default=TrolleyTxnStatus.PENDING)
    gross_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    platform_fee_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    local_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_currency: Mapped[str | None] = mapped_column(String, nullable=True)
    exchange_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    trolley_payment_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    trolley_batch_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TrolleyTransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    claim_id: str | None
    type: TrolleyTxnType
    status: TrolleyTxnStatus
    gross_amount: float | None = None
    platform_fee_amount: float | None = None
    net_amount: float | None = None
    source_currency: str = "USD"
    local_amount: float | None = None
    local_currency: str | None = None
    exchange_rate: float | None = None
    trolley_payment_id: str | None = None
    trolley_batch_id: str | None = None
    external_id: str | None = None
    failure_reason: str | None = None
    retry_count: int = 0
    description: str | None = None
    created_at: datetime
    updated_at: datetime
