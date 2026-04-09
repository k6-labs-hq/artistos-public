import enum
import uuid

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class WorkType(str, enum.Enum):
    COMPOSITION = "COMPOSITION"
    RECORDING = "RECORDING"
    VERSION = "VERSION"


class Work(Base):
    __tablename__ = "works"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True)
    work_type: Mapped[str] = mapped_column(Enum(WorkType), nullable=False)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)


class WorkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    isrc: str | None = None
    iswc: str | None = None
    work_type: WorkType
    artist_id: str
