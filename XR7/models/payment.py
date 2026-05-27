import enum
import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class PaymentType(str, enum.Enum):
    ROYALTY = "ROYALTY"
    SETTLEMENT = "SETTLEMENT"
    PAYOUT = "PAYOUT"
    GRANT_DISBURSEMENT = "GRANT_DISBURSEMENT"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        # Prevents duplicate payments for the same artist + payer reference.
        # Only enforced when reference_id is non-NULL (partial: composite IS NOT NULL
        # is DB-specific; the application-level uniqueness check in onboarding handles NULLs).
        UniqueConstraint("artist_id", "reference_id", name="uq_payments_artist_reference"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_type: Mapped[str] = mapped_column(Enum(PaymentType), nullable=False)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    # Source statement this payment was parsed from. See Event.statement_id (#333).
    statement_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    # Payer-provided identifiers extracted at ingestion time. Used when
    # generating dispute packets that need to reference the payer's own
    # records by their internal IDs (e.g. BMI requires Work ID + member
    # account number on dispute submissions).
    #
    # `payer_account_id` — the payer's identifier for the artist's account
    #   (BMI PARTICIPANT #, ASCAP member #, MLC payee number, etc.).
    # `payer_ip_number`  — the writer/publisher IPI/CAE number (cross-PRO).
    # `payer_work_id`    — the payer's identifier for the song/work
    #   (BMI TITLE #, ASCAP Work ID, MLC Song Code, etc.).
    payer_account_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payer_ip_number: Mapped[str | None] = mapped_column(String, nullable=True)
    payer_work_id: Mapped[str | None] = mapped_column(String, nullable=True)
    # ISWC — the industry-standard composition identifier that bridges
    # PROs (BMI/ASCAP) with mechanical collectives (MLC). Populated at
    # ingestion time via WorkIdentityLookup (MusicBrainz) when the source
    # statement doesn't carry it. The pair (payer_work_id, iswc) is what
    # turns BMI rows into something MLC's database can be queried against.
    iswc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)


class PaymentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payment_type: PaymentType
    artist_id: str
    statement_id: str | None = None
    amount: float
    currency: str
    period_start: date | None = None
    period_end: date | None = None
    source: str | None = None
    reference_id: str | None = None
    received_at: datetime
    payer_account_id: str | None = None
    payer_ip_number: str | None = None
    payer_work_id: str | None = None
    iswc: str | None = None
