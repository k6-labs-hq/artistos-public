from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AdvanceRecoveryPacket(Base):
    __tablename__ = "advance_recovery_packets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    offer_id: Mapped[str] = mapped_column(
        String, ForeignKey("advance_offers.id"), nullable=False, index=True
    )
    artist_id: Mapped[str] = mapped_column(
        String, ForeignKey("artists.id"), nullable=False, index=True
    )
    chain_of_custody: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    required_signers: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    collected_signatures: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    legal_basis: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    failure_reason: Mapped[str] = mapped_column(Text, nullable=False)
    immutable_ledger_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="READY")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
