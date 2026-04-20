from sqlalchemy import Column, String, Float, DateTime, Integer, Text
from pydantic import BaseModel
from XR7.models.base import Base
from datetime import datetime


class SloMetric(Base):
    __tablename__ = 'slo_metrics'
    id = Column(String, primary_key=True)
    metric_name = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class SloMetricCreate(BaseModel):
    """Schema for creating SLO metric."""
    metric_name: str
    value: float


class SloMetricUpdate(BaseModel):
    """Schema for updating SLO metric."""
    value: float | None = None


class SloMetricSchema(BaseModel):
    """Schema for SLO metric response."""
    id: str
    metric_name: str
    value: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TenantCostLedger(Base):
    """Model for tracking per-tenant infrastructure costs."""
    __tablename__ = 'tenant_cost_ledger'
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    cost_usd = Column(Float, nullable=False)
    cost_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cost_metadata = Column(Text, nullable=True)


class TenantCostLedgerCreate(BaseModel):
    """Schema for creating tenant cost entry."""
    tenant_id: str
    cost_usd: float
    cost_type: str
    metadata: str | None = None


class TenantCostLedgerSchema(BaseModel):
    """Schema for tenant cost response."""
    id: int
    tenant_id: str
    cost_usd: float
    cost_type: str
    timestamp: datetime
    metadata: str | None = None
    
    class Config:
        from_attributes = True
