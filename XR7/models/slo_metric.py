"""SLO Metric and Tenant Cost Ledger models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


# ---------------------------------------------------------------------------
# SloMetric
# ---------------------------------------------------------------------------

class SloMetric(Base):
    __tablename__ = "slo_metrics"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    org_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    # Measurement window in seconds, e.g. 3600 = 1 h, 86400 = 1 d
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)
    # Latency target in milliseconds for p95
    threshold_ms: Mapped[float] = mapped_column(Float, nullable=False, default=2000.0)
    current_p95_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Remaining error budget as a percentage (0-100)
    error_budget_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Burn rate: multiples of the acceptable error rate
    burn_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    breached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class SloMetricCreate(BaseModel):
    metric_name: str
    window_seconds: int = 3600
    threshold_ms: float = 2000.0
    description: str | None = None


class SloMetricUpdate(BaseModel):
    current_p95_ms: float | None = None
    error_budget_pct: float | None = None
    burn_rate: float | None = None
    breached: bool | None = None


class SloMetricSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    metric_name: str
    window_seconds: int
    threshold_ms: float
    current_p95_ms: float | None
    error_budget_pct: float | None
    burn_rate: float | None
    breached: bool
    description: str | None
    measured_at: datetime
    created_at: datetime


# ---------------------------------------------------------------------------
# TenantCostLedger
# ---------------------------------------------------------------------------

class TenantCostLedger(Base):
    __tablename__ = "tenant_cost_ledger"
    __table_args__ = (UniqueConstraint("org_id", "period_start", name="uq_cost_org_period"),)

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    org_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pipeline_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compute_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    storage_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    llm_tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    llm_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    budget_limit_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    # 0-100; alert fires when total_cost_usd / budget_limit_usd * 100 >= this
    budget_alert_pct: Mapped[float] = mapped_column(Float, nullable=False, default=80.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TenantCostLedgerCreate(BaseModel):
    period_start: datetime
    period_end: datetime
    pipeline_cost_usd: float = 0.0
    compute_cost_usd: float = 0.0
    storage_cost_usd: float = 0.0
    llm_tokens_used: int = 0
    llm_cost_usd: float = 0.0
    budget_limit_usd: float | None = None
    budget_alert_pct: float = 80.0
    notes: str | None = None


class TenantCostLedgerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    period_start: datetime
    period_end: datetime
    pipeline_cost_usd: float
    compute_cost_usd: float
    storage_cost_usd: float
    llm_tokens_used: int
    llm_cost_usd: float
    total_cost_usd: float
    budget_limit_usd: float | None
    budget_alert_pct: float
    notes: str | None
    created_at: datetime
    updated_at: datetime
