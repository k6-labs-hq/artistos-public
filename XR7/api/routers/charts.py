"""Dashboard chart data endpoints.

Feature #7: Dashboard Charts (Product Backlog #4)

RESTful API for chart data:
- GET /artists/{id}/charts/earnings-trend
- GET /artists/{id}/charts/leakage-by-category
- GET /artists/{id}/charts/recovery-trajectory

Returns chart.js compatible data structures for responsive visualization.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.chart_aggregation_service import (
    get_earnings_trend,
    get_leakage_by_category,
    get_recovery_trajectory,
)
from XR7.services.router_v21_phase1 import router_service_for

router = APIRouter(tags=["charts"])
_router_service = router_service_for("charts")


@router.get("/artists/{artist_id}/charts/earnings-trend")
def earnings_trend_chart(
    artist_id: str,
    days: int = Query(default=90, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
):
    """
    Get earnings trend over time for line chart visualization.
    
    Feature #7: Dashboard Charts
    
    Returns daily aggregated earnings for the specified lookback period.
    
    Args:
        artist_id: Artist identifier
        days: Lookback period in days (1-365, default: 90)
    
    Returns:
        Chart.js compatible dataset:
        - labels: Date strings (YYYY-MM-DD)
        - datasets: Single dataset with daily earnings
        - metadata: Summary statistics
    
    Example:
        GET /artists/art_123/charts/earnings-trend?days=90
        
        Response:
        {
            "labels": ["2026-01-01", "2026-01-02", ...],
            "datasets": [{
                "label": "Earnings",
                "data": [1250.50, 980.25, ...]
            }],
            "metadata": {
                "period_days": 90,
                "total_earnings": 125000.50,
                "data_points": 45
            }
        }
    
    Performance:
        - p95 < 200ms for typical artist (90 days)
        - Cached queries recommended for production
        - Uses date truncation and aggregation
    
    Responsive:
        - Works on mobile (reduced data points if needed)
        - Desktop shows full granularity
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    return get_earnings_trend(db, artist_id, days)


@router.get("/artists/{artist_id}/charts/leakage-by-category")
def leakage_by_category_chart(
    artist_id: str,
    db: Session = Depends(get_db),
):
    """
    Get leakage breakdown by anomaly category for pie/bar chart.
    
    Feature #7: Dashboard Charts
    
    Shows estimated recoverable amounts grouped by anomaly category.
    Only includes open/investigating anomalies.
    
    Args:
        artist_id: Artist identifier
    
    Returns:
        Chart.js compatible dataset:
        - labels: Category names (ROYALTY, PLATFORM, SYNC, etc.)
        - datasets: Single dataset with recoverable amounts
        - backgroundColor: Category-specific colors
        - metadata: Summary statistics
    
    Example:
        GET /artists/art_123/charts/leakage-by-category
        
        Response:
        {
            "labels": ["ROYALTY", "PLATFORM", "SYNC"],
            "datasets": [{
                "label": "Estimated Recoverable",
                "data": [15000, 8500, 3200],
                "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56"]
            }],
            "metadata": {
                "total_recoverable": 26700,
                "category_count": 3
            }
        }
    
    Performance:
        - p95 < 100ms (simple GROUP BY)
        - Indexed on (artist_id, category, status)
    
    Visualization:
        - Mobile: Pie chart (compact)
        - Desktop: Bar chart (more detail)
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    return get_leakage_by_category(db, artist_id)


@router.get("/artists/{artist_id}/charts/recovery-trajectory")
def recovery_trajectory_chart(
    artist_id: str,
    days: int = Query(default=180, ge=1, le=730, description="Number of days to look back"),
    db: Session = Depends(get_db),
):
    """
    Get recoverable vs recovered trajectory over time for line chart.
    
    Feature #7: Dashboard Charts
    
    Shows two cumulative trend lines:
    - Total recoverable (from anomalies detected)
    - Total recovered (from claims paid out)
    
    Args:
        artist_id: Artist identifier
        days: Lookback period in days (1-730, default: 180)
    
    Returns:
        Chart.js compatible dataset:
        - labels: Month strings (YYYY-MM)
        - datasets: Two datasets (recoverable, recovered)
        - metadata: Summary with recovery rate
    
    Example:
        GET /artists/art_123/charts/recovery-trajectory?days=180
        
        Response:
        {
            "labels": ["2026-01", "2026-02", "2026-03"],
            "datasets": [
                {
                    "label": "Total Recoverable",
                    "data": [10000, 25000, 42000],
                    "borderColor": "rgb(255, 99, 132)"
                },
                {
                    "label": "Total Recovered",
                    "data": [2000, 8500, 18500],
                    "borderColor": "rgb(75, 192, 192)"
                }
            ],
            "metadata": {
                "period_days": 180,
                "total_recoverable": 42000,
                "total_recovered": 18500,
                "recovery_rate": 0.44
            }
        }
    
    Performance:
        - p95 < 300ms (two queries with monthly bucketing)
        - Cumulative calculation done in Python
    
    Business value:
        - Shows recovery team effectiveness
        - Highlights gap between detected and recovered
        - Recovery rate trend visible over time
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    return get_recovery_trajectory(db, artist_id, days)
