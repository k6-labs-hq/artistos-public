"""
Widget Lead model for XR7 Engine 2.

Every artist who completes the royalty estimation widget (passes MFA and
retrieves an estimate) has a lead record created here.  This allows the
XR7 recovery team to follow up, track conversion to full audits, and
report on funnel metrics.

Privacy notes
-------------
- ``phone_hash`` stores a SHA-256 hash of the normalised phone number, NOT
  the raw number.  The phone was collected only for MFA verification; it is
  not needed for follow-up.
- ``email`` is stored in plain text because it IS required for follow-up
  communications.  It must be handled in accordance with your privacy policy
  and applicable regulations (GDPR, CCPA).
- ``artist_name`` is stored as provided; it may be a pseudonym / stage name.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class WidgetLead(Base):
    __tablename__ = "widget_leads"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Identity fields
    artist_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    phone_hash: Mapped[str] = mapped_column(String, nullable=False)   # SHA-256 of normalised phone

    # Career profile submitted in Step 3
    career_stage: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[str] = mapped_column(String, nullable=False)
    years_active: Mapped[int] = mapped_column(Integer, nullable=False)
    territory: Mapped[str] = mapped_column(String, nullable=False)

    # Estimate results stored for follow-up / reporting
    estimate_conservative: Mapped[float] = mapped_column(Float, nullable=False)
    estimate_likely: Mapped[float] = mapped_column(Float, nullable=False)
    estimate_optimistic: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="USD")

    # Status flags
    results_emailed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed: Mapped[bool] = mapped_column(Boolean, default=False)     # artist clicked "Claim My Recovery"
    claim_submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schema for API responses
# ---------------------------------------------------------------------------

class WidgetLeadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_name: str
    email: str
    career_stage: str
    genre: str
    years_active: int
    territory: str
    estimate_conservative: float
    estimate_likely: float
    estimate_optimistic: float
    currency: str
    results_emailed: bool
    claimed: bool
    claim_submitted_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def hash_phone(phone: str) -> str:
    """Return a SHA-256 hex digest of *phone* for de-duplication without storing PII."""
    return hashlib.sha256(phone.encode()).hexdigest()
