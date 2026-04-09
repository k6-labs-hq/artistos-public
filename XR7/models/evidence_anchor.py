from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class EvidenceAnchor(Base):
    __tablename__ = "evidence_anchors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    packet_hash: Mapped[str] = mapped_column(String, nullable=False)
    chain_hash: Mapped[str] = mapped_column(String, nullable=False)
    anchor_provider: Mapped[str] = mapped_column(String, default="INTERNAL_IMMUTABLE_LOG")
    anchor_reference: Mapped[str] = mapped_column(String, nullable=False)
    cid: Mapped[str | None] = mapped_column(String, nullable=True)
    tx_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    blockchain_status: Mapped[str] = mapped_column(String, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class EvidenceAnchorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    claim_id: str
    packet_hash: str
    chain_hash: str
    anchor_provider: str
    anchor_reference: str
    cid: str | None = None
    tx_hash: str | None = None
    blockchain_status: str
    created_at: datetime
