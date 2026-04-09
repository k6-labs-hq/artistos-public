"""Data Residency Policy — per-tenant region enforcement.

Stores the data residency policy for each org/tenant, and provides a
guard that raises HTTP 451 (Unavailable For Legal Reasons) when a
cross-region storage operation would violate the policy.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class DataRegion(str, enum.Enum):
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"
    EU_CENTRAL = "eu-central-1"
    AP_SOUTHEAST = "ap-southeast-1"
    AP_NORTHEAST = "ap-northeast-1"
    GLOBAL = "global"  # no restriction


class DataResidencyPolicy(Base):
    __tablename__ = "data_residency_policies"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    org_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    # Primary region where data must reside
    primary_region: Mapped[str] = mapped_column(
        Enum(DataRegion), nullable=False, default=DataRegion.GLOBAL
    )
    # Comma-separated list of permitted regions (empty = only primary)
    permitted_regions: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Whether AI/LLM processing is allowed to leave the primary region
    allow_cross_region_ai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Whether audit logs must stay in the primary region
    audit_log_region_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DataResidencyPolicySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    primary_region: str
    permitted_regions: str | None
    allow_cross_region_ai: bool
    audit_log_region_locked: bool
    active: bool
    created_by: str | None
    created_at: datetime
    updated_at: datetime


class DataResidencyPolicyUpsert(BaseModel):
    primary_region: DataRegion = DataRegion.GLOBAL
    permitted_regions: str | None = None
    allow_cross_region_ai: bool = True
    audit_log_region_locked: bool = False
