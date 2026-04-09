from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class AgentHandoffRecord(Base):
    __tablename__ = "agent_handoffs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    handoff_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    from_agent: Mapped[str] = mapped_column(String, nullable=False)
    to_agent: Mapped[str] = mapped_column(String, nullable=False)
    readiness_score: Mapped[float] = mapped_column(nullable=False)
    readiness_threshold: Mapped[float] = mapped_column(nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
