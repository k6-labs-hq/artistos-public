"""Chart data aggregation service for dashboard visualizations.

Feature #7: Dashboard Charts (Product Backlog #4)

Provides pre-aggregated data for:
- Earnings trend chart (time series)
- Leakage by category breakdown (pie/bar chart)
- Recoverable vs recovered trajectory (line chart)

Optimized for mobile + desktop with p95 < 500ms cached queries.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.payment import Payment

if TYPE_CHECKING:
    pass


def get_earnings_trend(db: Session, artist_id: str, days: int = 90) -> dict:
    """
    Get earnings trend over time for line chart visualization.

    Args:
        db: Database session
        artist_id: Artist identifier
        days: Number of days to look back (default: 90)

    Returns:
        Dict with:
        - labels: List of date strings (YYYY-MM-DD)
        - datasets: List with single dataset containing daily earnings

    Example response:
        {
            "labels": ["2026-01-01", "2026-01-02", ...],
            "datasets": [{
                "label": "Earnings",
                "data": [1250.50, 980.25, ...]
            }]
        }

    Performance: Uses date truncation and aggregation (p95 < 200ms typical).
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Aggregate payments by date
    results = (
        db.query(
            func.date(Payment.received_at).label("payment_date"),
            func.sum(Payment.amount).label("total_amount"),
        )
        .filter(
            Payment.artist_id == artist_id,
            Payment.received_at >= cutoff_date,
        )
        .group_by(func.date(Payment.received_at))
        .order_by(func.date(Payment.received_at))
        .all()
    )

    # Format for chart.js compatible structure
    labels = []
    data = []

    for row in results:
        labels.append(row.payment_date.isoformat() if row.payment_date else "")
        data.append(float(row.total_amount or 0))

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Earnings",
                "data": data,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "tension": 0.1,
            }
        ],
        "metadata": {
            "period_days": days,
            "total_earnings": sum(data),
            "data_points": len(data),
        },
    }


def get_leakage_by_category(db: Session, artist_id: str) -> dict:
    """
    Get leakage breakdown by anomaly category for pie/bar chart.

    Args:
        db: Database session
        artist_id: Artist identifier

    Returns:
        Dict with:
        - labels: List of category names
        - datasets: List with single dataset containing estimated recoverable amounts

    Example response:
        {
            "labels": ["ROYALTY", "PLATFORM", "SYNC"],
            "datasets": [{
                "label": "Estimated Recoverable",
                "data": [15000, 8500, 3200],
                "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56"]
            }]
        }

    Performance: Simple GROUP BY with index on (artist_id, category).
    """
    # Aggregate open anomalies by category
    results = (
        db.query(
            Anomaly.category,
            func.sum(Anomaly.estimated_recoverable).label("total_recoverable"),
            func.count(Anomaly.id).label("anomaly_count"),
        )
        .filter(
            Anomaly.artist_id == artist_id,
            Anomaly.status.in_([AnomalyStatus.OPEN, AnomalyStatus.INVESTIGATING]),
            Anomaly.deleted_at.is_(None),
        )
        .group_by(Anomaly.category)
        .all()
    )

    # Color palette for categories
    category_colors = {
        AnomalyCategory.ROYALTY: "#FF6384",
        AnomalyCategory.PLATFORM: "#36A2EB",
        AnomalyCategory.SYNC: "#FFCE56",
        AnomalyCategory.TOURING: "#4BC0C0",
        AnomalyCategory.MERCH: "#9966FF",
        AnomalyCategory.BRAND: "#FF9F40",
        AnomalyCategory.GRANT: "#C9CBCF",
    }

    labels = []
    data = []
    colors = []

    for row in results:
        category_name = row.category
        labels.append(category_name)
        data.append(float(row.total_recoverable or 0))
        colors.append(category_colors.get(AnomalyCategory(category_name), "#CCCCCC"))

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Estimated Recoverable",
                "data": data,
                "backgroundColor": colors,
                "borderWidth": 1,
            }
        ],
        "metadata": {
            "total_recoverable": sum(data),
            "category_count": len(labels),
        },
    }


def get_recovery_trajectory(db: Session, artist_id: str, days: int = 180) -> dict:
    """
    Get recoverable vs recovered trajectory over time for line chart.

    Shows two lines:
    - Total potential recovery (cumulative)
    - Total recovered (cumulative)

    Args:
        db: Database session
        artist_id: Artist identifier
        days: Number of days to look back (default: 180)

    Returns:
        Dict with:
        - labels: List of date strings
        - datasets: Two datasets (recoverable, recovered)

    Example response:
        {
            "labels": ["2026-01-01", "2026-02-01", ...],
            "datasets": [
                {"label": "Recoverable", "data": [10000, 25000, ...]},
                {"label": "Recovered", "data": [2000, 8500, ...]}
            ]
        }

    Performance: Two queries with date bucketing (monthly aggregation).
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Query 1: Anomalies detected over time (potential recovery)
    anomaly_results = (
        db.query(
            func.date_trunc("month", Anomaly.created_at).label("month"),
            func.sum(Anomaly.estimated_recoverable).label("total_recoverable"),
        )
        .filter(
            Anomaly.artist_id == artist_id,
            Anomaly.created_at >= cutoff_date,
            Anomaly.deleted_at.is_(None),
        )
        .group_by(func.date_trunc("month", Anomaly.created_at))
        .order_by(func.date_trunc("month", Anomaly.created_at))
        .all()
    )

    # Query 2: Claims recovered over time (actual recovery)
    claim_results = (
        db.query(
            func.date_trunc("month", Claim.updated_at).label("month"),
            func.sum(Claim.recovered_amount).label("total_recovered"),
        )
        .filter(
            Claim.artist_id == artist_id,
            Claim.status.in_([ClaimStatus.FUNDS_RECEIVED, ClaimStatus.PAID]),
            Claim.updated_at >= cutoff_date,
        )
        .group_by(func.date_trunc("month", Claim.updated_at))
        .order_by(func.date_trunc("month", Claim.updated_at))
        .all()
    )

    # Build cumulative time series
    recoverable_by_month = {}
    for row in anomaly_results:
        month_str = row.month.strftime("%Y-%m") if row.month else ""
        recoverable_by_month[month_str] = float(row.total_recoverable or 0)

    recovered_by_month = {}
    for row in claim_results:
        month_str = row.month.strftime("%Y-%m") if row.month else ""
        recovered_by_month[month_str] = float(row.total_recovered or 0)

    # Merge and sort months
    all_months = sorted(set(recoverable_by_month.keys()) | set(recovered_by_month.keys()))

    # Calculate cumulative sums
    cumulative_recoverable = 0
    cumulative_recovered = 0

    recoverable_data = []
    recovered_data = []

    for month in all_months:
        cumulative_recoverable += recoverable_by_month.get(month, 0)
        cumulative_recovered += recovered_by_month.get(month, 0)
        recoverable_data.append(cumulative_recoverable)
        recovered_data.append(cumulative_recovered)

    return {
        "labels": all_months,
        "datasets": [
            {
                "label": "Total Recoverable",
                "data": recoverable_data,
                "borderColor": "rgb(255, 99, 132)",
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "tension": 0.1,
            },
            {
                "label": "Total Recovered",
                "data": recovered_data,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "tension": 0.1,
            },
        ],
        "metadata": {
            "period_days": days,
            "total_recoverable": cumulative_recoverable,
            "total_recovered": cumulative_recovered,
            "recovery_rate": (
                cumulative_recovered / cumulative_recoverable if cumulative_recoverable > 0 else 0
            ),
        },
    }
