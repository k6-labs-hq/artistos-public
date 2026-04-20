"""Invoice model for billing and payment tracking.

Invoices are created when claims are recovered and track contingency fees owed.
Each claim can have at most one invoice (enforced by unique constraint).
"""

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice payment status lifecycle."""

    PENDING = "PENDING"  # Invoice created, awaiting payment
    PAID = "PAID"  # Payment received and processed
    CANCELLED = "CANCELLED"  # Invoice voided (claim disputed/reversed)
    REFUNDED = "REFUNDED"  # Payment refunded to artist


class Invoice(Base):
    """Billing invoice for recovered claims.

    Tracks contingency fees owed for successful claim recovery.
    Each claim generates exactly one invoice (idempotent via unique constraint).
    """

    __tablename__ = "invoices"
    __table_args__ = (
        # Idempotency: Prevent duplicate invoices for the same claim
        UniqueConstraint("claim_id", name="uq_invoices_claim_id"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(
        String, ForeignKey("claims.id"), nullable=False, unique=True
    )
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)

    # Financial amounts
    recovered_amount: Mapped[float] = mapped_column(Float, nullable=False)
    contingency_fee: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD", nullable=False)

    # Status tracking
    status: Mapped[str] = mapped_column(
        Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Invoice(id={self.id}, claim_id={self.claim_id}, "
            f"recovered=${self.recovered_amount}, fee=${self.contingency_fee}, "
            f"status={self.status})>"
        )


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
