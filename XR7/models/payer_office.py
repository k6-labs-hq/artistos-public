"""Per-payer office records — submission addresses for dispute filing.

Each row is one office (or specialized team) for one payer. BMI has six
regional offices (Nashville, New York, Los Angeles, Atlanta, Austin,
London) that members are routed to for Writer/Publisher Relations
inquiries. Each has a distinct email + mailing address. We pick the
right one per artist based on the artist's chosen home region.

Why a table and not code: the per-region email + mailing address is
data that varies per artist (different writers go through different
offices), and storing it as data means the artist's selection at
onboarding flows naturally into dispute packet rendering. It also
means we can verify and refresh the addresses without a code deploy
when offices move or rename. The stable per-payer constants
(canonical_id, display_name, salutation, SLAs) stay in
`XR7/recovery/payer_config.py`.

Seeded via the alembic data migration that creates this table.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, Date, DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class PayerOffice(Base):
    __tablename__ = "payer_offices"
    __table_args__ = (
        UniqueConstraint("payer_id", "name", name="uq_payer_offices_payer_name"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # The canonical payer id this office belongs to ("BMI", "ASCAP", "MLC",
    # "SoundExchange"). Matches `PayerConfig.canonical_id`.
    payer_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Human-readable office or team name ("Nashville", "New York",
    # "Finance Team"). Unique within (payer_id).
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Email address dispute submissions go to.
    submission_email: Mapped[str] = mapped_column(String, nullable=False)
    # Multiline postal address. Optional — some offices don't publish one.
    mailing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Optional published phone number for member services.
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    # When no specific office is chosen for an artist, the default for
    # this payer is used. Exactly one row per payer should be the default.
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # The date the email + address was last cross-checked against the
    # payer's published material. Stale entries are a footgun — a
    # bouncing send hurts our Postmark deliverability reputation.
    last_verified: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Free-form operational notes (e.g. "British country writers route
    # here", "uses postal mail only since 2024").
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class PayerOfficeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payer_id: str
    name: str
    submission_email: str
    mailing_address: str | None = None
    phone: str | None = None
    is_default: bool
    last_verified: date | None = None
    notes: str | None = None


# ── BMI seed data ───────────────────────────────────────────────────────────
#
# The six BMI Writer/Publisher Relations offices, sourced from the BMI
# Writer Kit (form 3-2025). Used by the alembic migration that creates
# this table, and by test fixtures so the test SQLite has the same
# baseline as a freshly-migrated Postgres.
#
# Other PROs (ASCAP, MLC, SoundExchange) are intentionally NOT seeded
# yet — see docs/runbooks/{ascap,mlc,soundexchange}-dispute-attorney-
# brief.md for why their entries are blocked on attorney input.

BMI_OFFICES_SEED: list[dict] = [
    {
        "name": "Nashville",
        "submission_email": "nashville@bmi.com",
        "mailing_address": "Broadcast Music, Inc.\n10 Music Square East\nNashville, TN 37203",
        "phone": "1-844-BMI-4255",
        "is_default": True,
        "notes": "Default for country/Americana writers. Matt's network base.",
    },
    {
        "name": "New York",
        "submission_email": "newyork@bmi.com",
        "mailing_address": (
            "Broadcast Music, Inc.\n7 World Trade Center\n"
            "250 Greenwich Street\nNew York, NY 10007"
        ),
        "phone": "1-844-BMI-4255",
        "is_default": False,
        "notes": None,
    },
    {
        "name": "Los Angeles",
        "submission_email": "losangeles@bmi.com",
        "mailing_address": (
            "Broadcast Music, Inc.\n9420 Wilshire Blvd, Suite 200\nBeverly Hills, CA 90212"
        ),
        "phone": "1-844-BMI-4255",
        "is_default": False,
        "notes": None,
    },
    {
        "name": "Atlanta",
        "submission_email": "atlanta@bmi.com",
        "mailing_address": None,
        "phone": "1-844-BMI-4255",
        "is_default": False,
        "notes": "No published street address; kit lists email only.",
    },
    {
        "name": "Austin",
        "submission_email": "austin@bmi.com",
        "mailing_address": (
            "Broadcast Music, Inc.\n1400 S. Congress Avenue, Suite B 200\nAustin, TX 78704"
        ),
        "phone": "1-844-BMI-4255",
        "is_default": False,
        "notes": None,
    },
    {
        "name": "London",
        "submission_email": "london@bmi.com",
        "mailing_address": (
            "Broadcast Music, Inc.\n84 Harley House Marylebone Road\nLondon NW1 5HN"
        ),
        "phone": "+1-615-401-2200",
        "is_default": False,
        "notes": "International caller phone listed; routes to Nashville HQ.",
    },
]
