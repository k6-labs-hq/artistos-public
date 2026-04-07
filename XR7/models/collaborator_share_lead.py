"""Tracks collaborators (co-writers, producers, publishers) identified during an
artist's analysis so they can be invited to the platform (viral growth loop) and
logged in the CRM.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CollaboratorRole(str, Enum):
    CO_WRITER = "co_writer"
    PRODUCER = "producer"
    PUBLISHER = "publisher"
    MANAGER = "manager"
    LABEL = "label"
    OTHER = "other"


class CollaboratorShareLead(Base):
    """One row per collaborator identified from a creator's analysis session."""

    __tablename__ = "collaborator_share_leads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # The creator who ran the analysis that revealed this collaborator
    source_artist_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("artists.id"), nullable=False, index=True
    )
    # Human-readable name of the collaborator (required)
    collaborator_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Optional contact info — filled in by the creator or enriched later
    collaborator_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    collaborator_role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=CollaboratorRole.CO_WRITER.value
    )
    # Invite token generated for this collaborator, if one was created
    invite_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("invites.id"), nullable=True, index=True
    )
    # HubSpot contact ID logged for this lead
    hubspot_contact_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # The text message the creator sent / copied
    share_message_text: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
