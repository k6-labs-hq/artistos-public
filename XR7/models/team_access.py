from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class TeamRole(str, enum.Enum):
    ARTIST = "artist"
    MANAGER = "manager"
    ATTORNEY = "attorney"


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    user_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role: Mapped[str] = mapped_column(Enum(TeamRole), nullable=False, default=TeamRole.MANAGER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class TeamMemberSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    user_email: str
    role: TeamRole
    created_at: datetime


class TeamMemberCreate(BaseModel):
    user_email: str
    role: TeamRole
