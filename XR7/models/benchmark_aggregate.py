"""
Benchmark Aggregate — XR7 Engine 2.

Pre-computed anonymised peer statistics used to rank artists relative to
their genre / role-type cohort.  Rows are seeded from aggregate analytics
runs (not individual artist data) and refreshed periodically by a Celery task.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class BenchmarkAggregate(Base):
    """Anonymised peer cohort statistics for percentile ranking."""

    __tablename__ = "benchmark_aggregates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Cohort dimensions
    genre: Mapped[str] = mapped_column(String, nullable=False, index=True)
    role_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # "small" (<50 works), "medium" (50-200), "large" (200-1000), "enterprise" (>1000)
    catalog_size_bucket: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    # Leakage %: (total_recoverable / total_expected) * 100
    leakage_pct_p25: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    leakage_pct_p50: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    leakage_pct_p75: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Recovery rate: fraction of anomalies with a closed/paid claim
    recovery_rate_p25: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recovery_rate_p50: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recovery_rate_p75: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Average $ recovered per closed anomaly/claim
    avg_recovered_per_anomaly_p25: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    avg_recovered_per_anomaly_p50: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    avg_recovered_per_anomaly_p75: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schema
# ---------------------------------------------------------------------------

class BenchmarkAggregateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    genre: str
    role_type: str
    catalog_size_bucket: str
    leakage_pct_p25: float
    leakage_pct_p50: float
    leakage_pct_p75: float
    recovery_rate_p25: float
    recovery_rate_p50: float
    recovery_rate_p75: float
    avg_recovered_per_anomaly_p25: float
    avg_recovered_per_anomaly_p50: float
    avg_recovered_per_anomaly_p75: float
    sample_size: int
    updated_at: datetime


# ---------------------------------------------------------------------------
# Default seed data (industry-reasonable approximations)
# ---------------------------------------------------------------------------

_DEFAULT_AGGREGATES: list[dict] = [
    # genre, role_type, catalog_size_bucket,
    # leakage_pct p25/p50/p75, recovery_rate p25/p50/p75,
    # avg_recovered_per_anomaly p25/p50/p75, sample_size
    {
        "genre": "pop", "role_type": "recording_artist", "catalog_size_bucket": "small",
        "leakage_pct_p25": 3.0, "leakage_pct_p50": 7.5, "leakage_pct_p75": 14.0,
        "recovery_rate_p25": 0.30, "recovery_rate_p50": 0.52, "recovery_rate_p75": 0.72,
        "avg_recovered_per_anomaly_p25": 120.0, "avg_recovered_per_anomaly_p50": 380.0,
        "avg_recovered_per_anomaly_p75": 950.0, "sample_size": 412,
    },
    {
        "genre": "pop", "role_type": "recording_artist", "catalog_size_bucket": "medium",
        "leakage_pct_p25": 2.5, "leakage_pct_p50": 6.0, "leakage_pct_p75": 12.0,
        "recovery_rate_p25": 0.35, "recovery_rate_p50": 0.58, "recovery_rate_p75": 0.78,
        "avg_recovered_per_anomaly_p25": 250.0, "avg_recovered_per_anomaly_p50": 640.0,
        "avg_recovered_per_anomaly_p75": 1800.0, "sample_size": 289,
    },
    {
        "genre": "pop", "role_type": "songwriter", "catalog_size_bucket": "small",
        "leakage_pct_p25": 4.0, "leakage_pct_p50": 9.5, "leakage_pct_p75": 18.0,
        "recovery_rate_p25": 0.25, "recovery_rate_p50": 0.47, "recovery_rate_p75": 0.67,
        "avg_recovered_per_anomaly_p25": 90.0, "avg_recovered_per_anomaly_p50": 310.0,
        "avg_recovered_per_anomaly_p75": 820.0, "sample_size": 335,
    },
    {
        "genre": "hip-hop", "role_type": "recording_artist", "catalog_size_bucket": "small",
        "leakage_pct_p25": 5.0, "leakage_pct_p50": 11.0, "leakage_pct_p75": 22.0,
        "recovery_rate_p25": 0.28, "recovery_rate_p50": 0.49, "recovery_rate_p75": 0.68,
        "avg_recovered_per_anomaly_p25": 150.0, "avg_recovered_per_anomaly_p50": 450.0,
        "avg_recovered_per_anomaly_p75": 1100.0, "sample_size": 520,
    },
    {
        "genre": "hip-hop", "role_type": "recording_artist", "catalog_size_bucket": "medium",
        "leakage_pct_p25": 3.5, "leakage_pct_p50": 8.0, "leakage_pct_p75": 16.0,
        "recovery_rate_p25": 0.32, "recovery_rate_p50": 0.55, "recovery_rate_p75": 0.75,
        "avg_recovered_per_anomaly_p25": 300.0, "avg_recovered_per_anomaly_p50": 750.0,
        "avg_recovered_per_anomaly_p75": 2000.0, "sample_size": 301,
    },
    {
        "genre": "electronic", "role_type": "recording_artist", "catalog_size_bucket": "small",
        "leakage_pct_p25": 6.0, "leakage_pct_p50": 13.0, "leakage_pct_p75": 26.0,
        "recovery_rate_p25": 0.20, "recovery_rate_p50": 0.42, "recovery_rate_p75": 0.62,
        "avg_recovered_per_anomaly_p25": 80.0, "avg_recovered_per_anomaly_p50": 280.0,
        "avg_recovered_per_anomaly_p75": 700.0, "sample_size": 278,
    },
    {
        "genre": "electronic", "role_type": "producer", "catalog_size_bucket": "medium",
        "leakage_pct_p25": 4.5, "leakage_pct_p50": 10.0, "leakage_pct_p75": 19.0,
        "recovery_rate_p25": 0.30, "recovery_rate_p50": 0.52, "recovery_rate_p75": 0.70,
        "avg_recovered_per_anomaly_p25": 200.0, "avg_recovered_per_anomaly_p50": 560.0,
        "avg_recovered_per_anomaly_p75": 1500.0, "sample_size": 195,
    },
    {
        "genre": "country", "role_type": "recording_artist", "catalog_size_bucket": "small",
        "leakage_pct_p25": 4.0, "leakage_pct_p50": 8.5, "leakage_pct_p75": 16.0,
        "recovery_rate_p25": 0.33, "recovery_rate_p50": 0.55, "recovery_rate_p75": 0.73,
        "avg_recovered_per_anomaly_p25": 130.0, "avg_recovered_per_anomaly_p50": 400.0,
        "avg_recovered_per_anomaly_p75": 1000.0, "sample_size": 210,
    },
    {
        "genre": "r&b", "role_type": "recording_artist", "catalog_size_bucket": "medium",
        "leakage_pct_p25": 3.0, "leakage_pct_p50": 7.0, "leakage_pct_p75": 14.0,
        "recovery_rate_p25": 0.38, "recovery_rate_p50": 0.60, "recovery_rate_p75": 0.80,
        "avg_recovered_per_anomaly_p25": 280.0, "avg_recovered_per_anomaly_p50": 700.0,
        "avg_recovered_per_anomaly_p75": 1900.0, "sample_size": 248,
    },
    {
        "genre": "default", "role_type": "default", "catalog_size_bucket": "small",
        "leakage_pct_p25": 4.0, "leakage_pct_p50": 9.0, "leakage_pct_p75": 18.0,
        "recovery_rate_p25": 0.28, "recovery_rate_p50": 0.50, "recovery_rate_p75": 0.70,
        "avg_recovered_per_anomaly_p25": 100.0, "avg_recovered_per_anomaly_p50": 350.0,
        "avg_recovered_per_anomaly_p75": 900.0, "sample_size": 1000,
    },
    {
        "genre": "default", "role_type": "default", "catalog_size_bucket": "medium",
        "leakage_pct_p25": 3.0, "leakage_pct_p50": 7.0, "leakage_pct_p75": 15.0,
        "recovery_rate_p25": 0.33, "recovery_rate_p50": 0.55, "recovery_rate_p75": 0.74,
        "avg_recovered_per_anomaly_p25": 200.0, "avg_recovered_per_anomaly_p50": 600.0,
        "avg_recovered_per_anomaly_p75": 1600.0, "sample_size": 1000,
    },
    {
        "genre": "default", "role_type": "default", "catalog_size_bucket": "large",
        "leakage_pct_p25": 2.5, "leakage_pct_p50": 5.5, "leakage_pct_p75": 11.0,
        "recovery_rate_p25": 0.38, "recovery_rate_p50": 0.62, "recovery_rate_p75": 0.80,
        "avg_recovered_per_anomaly_p25": 350.0, "avg_recovered_per_anomaly_p50": 900.0,
        "avg_recovered_per_anomaly_p75": 2400.0, "sample_size": 500,
    },
    {
        "genre": "default", "role_type": "default", "catalog_size_bucket": "enterprise",
        "leakage_pct_p25": 2.0, "leakage_pct_p50": 4.5, "leakage_pct_p75": 9.0,
        "recovery_rate_p25": 0.45, "recovery_rate_p50": 0.68, "recovery_rate_p75": 0.85,
        "avg_recovered_per_anomaly_p25": 500.0, "avg_recovered_per_anomaly_p50": 1300.0,
        "avg_recovered_per_anomaly_p75": 3500.0, "sample_size": 200,
    },
]


def seed_default_aggregates(db) -> int:  # type: ignore[type-arg]
    """Idempotently insert default benchmark rows if the table is empty."""
    existing = db.query(BenchmarkAggregate).count()
    if existing > 0:
        return 0
    for row in _DEFAULT_AGGREGATES:
        db.add(BenchmarkAggregate(**row))
    db.commit()
    return len(_DEFAULT_AGGREGATES)


def catalog_size_bucket(work_count: int) -> str:
    if work_count < 50:
        return "small"
    if work_count < 200:
        return "medium"
    if work_count < 1000:
        return "large"
    return "enterprise"
