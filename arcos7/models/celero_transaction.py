"""
Celero Commerce transaction audit model for ARCOS7 Engine 2.

Every payment processed through Celero Commerce — whether a contingency-fee
charge, a refund, a void, or an artist disbursement — is recorded here.
This table is the authoritative audit trail for ARCOS7's payment activity
and must never be deleted from.

Transaction types
-----------------
CHARGE
    ARCOS7 charging the artist a contingency fee (10% of recovered amount).
    Initiated by ``POST /artists/{id}/celero/charge``.

REFUND
    Partial or full refund of a previous CHARGE.
    Initiated by ``POST /artists/{id}/celero/refund/{txn_id}``.

VOID
    Voiding an unsettled CHARGE.
    Initiated by ``POST /artists/{id}/celero/void/{txn_id}``.

DISBURSEMENT
    ARCOS7 paying the artist their net recovery share via ACH credit.
    Initiated by ``POST /artists/{id}/celero/disburse``.

Transaction statuses
--------------------
PENDING     Created locally; not yet submitted or response pending.
APPROVED    Celero approved the transaction.
DECLINED    Celero declined the transaction.
VOIDED      Transaction was voided before settlement.
REFUNDED    A full or partial refund was issued.
SETTLED     Disbursement ACH has settled to the artist's account.
FAILED      Disbursement failed (bank rejection, etc.).
ERROR       Gateway communication error or malformed response.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class CeleroTxnType(str, enum.Enum):
    CHARGE = "CHARGE"
    REFUND = "REFUND"
    VOID = "VOID"
    DISBURSEMENT = "DISBURSEMENT"


class CeleroTxnStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    VOIDED = "VOIDED"
    REFUNDED = "REFUNDED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class CeleroTransaction(Base):
    """
    Audit record for a single transaction processed through Celero Commerce.
    """

    __tablename__ = "celero_transactions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    claim_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("claims.id"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(Enum(CeleroTxnType), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[str] = mapped_column(
        Enum(CeleroTxnStatus), default=CeleroTxnStatus.PENDING
    )
    # Celero gateway identifiers
    celero_transaction_id: Mapped[str | None] = mapped_column(
        String, nullable=True, index=True
    )
    celero_customer_vault_id: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    celero_auth_code: Mapped[str | None] = mapped_column(String, nullable=True)
    celero_response_code: Mapped[str | None] = mapped_column(String, nullable=True)
    celero_response_text: Mapped[str | None] = mapped_column(String, nullable=True)
    # Internal reference fields
    order_id: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class CeleroTransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    claim_id: str | None
    type: CeleroTxnType
    amount: float
    currency: str
    status: CeleroTxnStatus
    celero_transaction_id: str | None
    celero_customer_vault_id: str | None
    celero_auth_code: str | None
    celero_response_code: str | None
    celero_response_text: str | None
    order_id: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
