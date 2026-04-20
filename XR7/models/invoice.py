"""Invoice model for billing and revenue tracking."""

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Invoice(Base):
    """Invoice for recovered royalties with contingency fee calculation.

    TDD-BILL-001 Remediation: Database-level idempotency constraint ensures that
    duplicate invoice creation (via Celery retry after process crash) is prevented
    at the database layer, not just in-memory application logic.

    Compliance: SOC 2 CC6.1 - Logical access controls (revenue integrity)
    Regulatory: Revenue accounting must be idempotent and tamper-evident
    """

    __tablename__ = "invoices"
    __table_args__ = (
        # IDEMPOTENCY CONSTRAINT: One invoice per claim_id
        # TDD-BILL-001: Prevents double-billing under Celery retry + process crash
        # If create_invoice(claim_id=X) is called twice, second call fails at DB layer
        UniqueConstraint("claim_id", name="uq_invoices_claim_id"),
        # BUSINESS LOGIC CONSTRAINTS
        CheckConstraint("recovered_amount >= 0", name="ck_invoices_recovered_amount_positive"),
        CheckConstraint("contingency_fee >= 0", name="ck_invoices_contingency_fee_positive"),
        CheckConstraint(
            "contingency_fee <= recovered_amount", name="ck_invoices_fee_not_exceeds_recovery"
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(
        String, ForeignKey("claims.id"), nullable=False, unique=True, index=True
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    recovered_amount: Mapped[float] = mapped_column(Float, nullable=False)
    contingency_fee: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    status: Mapped[str] = mapped_column(
        Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class InvoiceSchema(BaseModel):
    """Pydantic schema for Invoice serialization."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    claim_id: str
    artist_id: str
    recovered_amount: float
    contingency_fee: float
    currency: str
    status: InvoiceStatus
    created_at: datetime
    paid_at: datetime | None = None
    cancelled_at: datetime | None = None
