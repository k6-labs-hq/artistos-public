import enum
import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from arcos7.models.base import Base


class PaymentType(str, enum.Enum):
    ROYALTY = "ROYALTY"
    SETTLEMENT = "SETTLEMENT"
    PAYOUT = "PAYOUT"
    GRANT_DISBURSEMENT = "GRANT_DISBURSEMENT"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_type: Mapped[str] = mapped_column(Enum(PaymentType), nullable=False)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.utcnow())


class PaymentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_type: PaymentType
    artist_id: str
    amount: float
    currency: str
    period_start: date | None = None
    period_end: date | None = None
    source: str | None = None
    reference_id: str | None = None
    received_at: datetime
