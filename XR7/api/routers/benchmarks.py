"""
Peer Benchmark Percentiles — XR7 Engine 2.

GET /artists/{artist_id}/recovery/benchmark-percentiles

Returns the artist's percentile rank for:
  - overall leakage %
  - streaming recovery efficiency (recovery rate)
  - average $ recovered per claim

Uses pre-seeded ``BenchmarkAggregate`` cohort rows (genre × role_type ×
catalog_size_bucket).  If no exact cohort match exists, the nearest bucket
is used; if the table is empty the endpoint returns a calibrated placeholder.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.benchmark_aggregate import BenchmarkAggregate, _DEFAULT_AGGREGATES
from XR7.models.claim import Claim
from XR7.services.branding import inject_branding_metadata
from xr7_common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["benchmarks"])

# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class PercentileResult(BaseModel):
    metric: str
    value: float = Field(..., description="Artist's raw metric value")
    percentile: int = Field(..., ge=0, le=100, description="Artist's percentile rank (0–100)")
    label: str = Field(..., description="Human-readable label e.g. 'Top 18%'")
    comparison: str = Field(..., description="Comparison sentence for UI display")
    cohort_p50: float = Field(..., description="Cohort median for this metric")


class BenchmarkPercentileResponse(BaseModel):
    artist_id: str
    cohort: dict[str, str] = Field(..., description="genre, role_type, catalog_size_bucket")
    cohort_sample_size: int
    metrics: list[PercentileResult]
    computed_at: datetime
    note: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _catalog_size_bucket(n: int) -> str:
    if n < 50:
        return "small"
    if n < 200:
        return "medium"
    if n < 1000:
        return "large"
    return "enterprise"


def _percentile_from_p_values(
    artist_value: float,
    p25: float,
    p50: float,
    p75: float,
    *,
    higher_is_better: bool = True,
) -> int:
    """
    Approximate artist's percentile rank using the three known percentile
    anchors from the cohort aggregate.

    For ``higher_is_better=True`` metrics (recovery rate, avg recovered):
      - Artist value > p75  → ~top 25%  → percentile ≈ 75–100
      - Artist value in p50–p75 → percentile ≈ 50–75
      - Artist value in p25–p50 → percentile ≈ 25–50
      - Artist value < p25  → percentile ≈ 0–25

    For ``higher_is_better=False`` metrics (leakage %):
      - A lower artist value is *better*, so percentiles are inverted.
    """
    anchors = sorted([p25, p50, p75])
    lo, mid, hi = anchors

    # Normalise to 0–1 by interpolating within the known range extended ±50% beyond hi
    value_range_low = max(0.0, lo - (hi - lo) * 0.5)
    value_range_high = hi + (hi - lo) * 0.5

    if value_range_high <= value_range_low:
        frac = 0.5
    else:
        frac = (artist_value - value_range_low) / (value_range_high - value_range_low)
        frac = max(0.0, min(1.0, frac))

    if higher_is_better:
        return int(round(frac * 100))
    else:
        return int(round((1.0 - frac) * 100))


def _label_and_comparison(percentile: int, metric_display: str) -> tuple[str, str]:
    """Return a (label, comparison) pair for a given percentile."""
    top_pct = 100 - percentile
    if top_pct <= 0:
        top_pct = 1
    label = f"Top {top_pct}%"
    if percentile >= 75:
        tier = "significantly better"
    elif percentile >= 50:
        tier = "better"
    elif percentile >= 25:
        tier = "slightly below"
    else:
        tier = "well below"
    comparison = (
        f"{tier} than {percentile}% of similar artists in {metric_display}"
    )
    return label, comparison


def _ensure_seed_data(db: Session) -> None:
    """Seed default aggregate rows if the table is empty."""
    existing = db.query(BenchmarkAggregate).first()
    if existing:
        return
    logger.info("Seeding benchmark_aggregates table with default data")
    for row in _DEFAULT_AGGREGATES:
        agg = BenchmarkAggregate(
            id=__import__("uuid").uuid4().__str__(),
            **row,
            updated_at=datetime.now(timezone.utc),
        )
        db.add(agg)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to seed benchmark_aggregates")


def _find_cohort(
    db: Session,
    genre: str,
    role_type: str,
    catalog_size_bucket: str,
) -> BenchmarkAggregate | None:
    """Find the best-matching cohort row, relaxing constraints progressively."""
    # Exact match
    row = (
        db.query(BenchmarkAggregate)
        .filter(
            BenchmarkAggregate.genre == genre,
            BenchmarkAggregate.role_type == role_type,
            BenchmarkAggregate.catalog_size_bucket == catalog_size_bucket,
        )
        .first()
    )
    if row:
        return row

    # Relax catalog_size_bucket
    row = (
        db.query(BenchmarkAggregate)
        .filter(
            BenchmarkAggregate.genre == genre,
            BenchmarkAggregate.role_type == role_type,
        )
        .first()
    )
    if row:
        return row

    # Relax genre
    row = (
        db.query(BenchmarkAggregate)
        .filter(BenchmarkAggregate.role_type == role_type)
        .first()
    )
    if row:
        return row

    # Fall back to any row (global average)
    return db.query(BenchmarkAggregate).first()


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/recovery/benchmark-percentiles",
    response_model=BenchmarkPercentileResponse,
    summary="Artist's percentile rank vs. anonymised peer cohort",
)
def get_benchmark_percentiles(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> BenchmarkPercentileResponse:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    _ensure_seed_data(db)

    # ── Derive cohort dimensions from artist profile ──
    genre = str(artist.primary_vertical or "pop").lower()
    role_type = str(artist.role or "recording_artist").lower().replace(" ", "_")

    from XR7.models.work import Work
    work_count = db.query(Work).filter(Work.artist_id == artist_id).count()
    bucket = _catalog_size_bucket(work_count)

    cohort = _find_cohort(db, genre, role_type, bucket)

    note: str | None = None
    if cohort is None:
        # No aggregate data at all — return neutral 50th percentile
        note = "Benchmark data not yet available; showing estimated peer averages."
        return BenchmarkPercentileResponse(
            artist_id=artist_id,
            cohort={"genre": genre, "role_type": role_type, "catalog_size_bucket": bucket},
            cohort_sample_size=0,
            metrics=[
                PercentileResult(
                    metric="leakage_pct",
                    value=0.0,
                    percentile=50,
                    label="Top 50%",
                    comparison="Insufficient data to rank leakage %.",
                    cohort_p50=0.0,
                ),
            ],
            computed_at=datetime.now(timezone.utc),
            note=note,
        )

    # ── Compute artist's actual metrics ──────────────────────────────────
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

    total_expected = sum(float(a.expected_amount or 0.0) for a in anomalies)
    total_recoverable = sum(float(a.estimated_recoverable or 0.0) for a in anomalies)
    artist_leakage_pct = (
        (total_recoverable / total_expected * 100.0) if total_expected > 0 else 0.0
    )

    closed_claims = [
        c for c in claims if str(c.status).upper() in ("PAID", "CLOSED", "SETTLED")
    ]
    artist_recovery_rate = (
        len(closed_claims) / len(claims) if claims else 0.0
    )

    total_recovered = sum(
        float(c.amount_recovered or 0.0) for c in closed_claims
        if hasattr(c, "amount_recovered")
    )
    if not total_recovered:
        # Fallback: sum estimated_recoverable from paid claims' linked anomalies
        closed_anomalies = [
            a for a in anomalies
            if str(a.status).upper() in ("CLOSED",)
        ]
        total_recovered = sum(float(a.estimated_recoverable or 0.0) for a in closed_anomalies)

    artist_avg_recovered = (
        total_recovered / len(closed_claims) if closed_claims else 0.0
    )

    # ── Compute percentiles ───────────────────────────────────────────────
    leakage_pct = _percentile_from_p_values(
        artist_leakage_pct,
        cohort.leakage_pct_p25,
        cohort.leakage_pct_p50,
        cohort.leakage_pct_p75,
        higher_is_better=False,  # lower leakage % = better
    )
    recovery_pct = _percentile_from_p_values(
        artist_recovery_rate,
        cohort.recovery_rate_p25,
        cohort.recovery_rate_p50,
        cohort.recovery_rate_p75,
        higher_is_better=True,
    )
    avg_recovered_pct = _percentile_from_p_values(
        artist_avg_recovered,
        cohort.avg_recovered_per_anomaly_p25,
        cohort.avg_recovered_per_anomaly_p50,
        cohort.avg_recovered_per_anomaly_p75,
        higher_is_better=True,
    )

    lk_label, lk_cmp = _label_and_comparison(leakage_pct, "earnings leakage")
    rr_label, rr_cmp = _label_and_comparison(recovery_pct, "streaming recovery efficiency")
    ar_label, ar_cmp = _label_and_comparison(avg_recovered_pct, "average $ recovered per claim")

    if cohort.genre != genre or cohort.role_type != role_type or cohort.catalog_size_bucket != bucket:
        note = (
            f"Exact cohort ({genre}/{role_type}/{bucket}) not found; "
            f"using nearest match ({cohort.genre}/{cohort.role_type}/{cohort.catalog_size_bucket})."
        )

    metrics = [
        PercentileResult(
            metric="leakage_pct",
            value=round(artist_leakage_pct, 2),
            percentile=leakage_pct,
            label=lk_label,
            comparison=lk_cmp,
            cohort_p50=cohort.leakage_pct_p50,
        ),
        PercentileResult(
            metric="streaming_recovery_efficiency",
            value=round(artist_recovery_rate, 4),
            percentile=recovery_pct,
            label=rr_label,
            comparison=rr_cmp,
            cohort_p50=cohort.recovery_rate_p50,
        ),
        PercentileResult(
            metric="avg_recovered_per_claim",
            value=round(artist_avg_recovered, 2),
            percentile=avg_recovered_pct,
            label=ar_label,
            comparison=ar_cmp,
            cohort_p50=cohort.avg_recovered_per_anomaly_p50,
        ),
    ]

    return BenchmarkPercentileResponse(
        artist_id=artist_id,
        cohort={
            "genre": cohort.genre,
            "role_type": cohort.role_type,
            "catalog_size_bucket": cohort.catalog_size_bucket,
        },
        cohort_sample_size=cohort.sample_size,
        metrics=metrics,
        computed_at=datetime.now(timezone.utc),
        note=note,
    )
