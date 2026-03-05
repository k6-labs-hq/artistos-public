import enum
import uuid
from datetime import date
from typing import Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class ContractType(str, enum.Enum):
    LABEL = "LABEL"
    PUBLISHING = "PUBLISHING"
    TOURING = "TOURING"
    MERCH = "MERCH"
    SYNC = "SYNC"
    BRAND = "BRAND"
    GRANT = "GRANT"


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_type: Mapped[str] = mapped_column(Enum(ContractType), nullable=False)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), nullable=False)
    counterparty: Mapped[str] = mapped_column(String, nullable=False)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    terms: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)


class ContractSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    contract_type: ContractType
    artist_id: str
    counterparty: str
    effective_date: date | None = None
    expiry_date: date | None = None
    terms: dict | None = None
    territory: str | None = None
