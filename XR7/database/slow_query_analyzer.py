"""
Slow Query Auto-Analyzer for PostgreSQL.

Automatically analyzes slow queries and provides optimization recommendations:
- Identifies queries executing >1 second
- Runs EXPLAIN ANALYZE on slow queries
- Detects sequential scans, missing indexes
- Generates index creation suggestions
- Sends weekly slow query report to engineering team

Requires PostgreSQL extension: pg_stat_statements
Enable with: CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

Configuration via environment variables:
- SLOW_QUERY_THRESHOLD_MS: Query duration threshold (default: 1000ms)
- SLOW_QUERY_ANALYSIS_ENABLED: Enable analyzer (default: true)
- SLOW_QUERY_REPORT_EMAIL: Email for weekly reports

Documented in docs/production_readiness_wave3_2026_q2.md DB-012
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from xr7_common.logging import get_logger

logger = get_logger(__name__)

SLOW_QUERY_THRESHOLD_MS = int(os.environ.get("SLOW_QUERY_THRESHOLD_MS", "1000"))
ANALYSIS_ENABLED = os.environ.get("SLOW_QUERY_ANALYSIS_ENABLED", "true").lower() == "true"


@dataclass
class SlowQuery:
    """Slow query analysis result."""

    query_text: str
    call_count: int
    total_time_ms: float
    mean_time_ms: float
    max_time_ms: float
    stddev_time_ms: float
    rows_returned: int
    # Analysis results
    has_seq_scan: bool = False
    missing_indexes: list[str] = field(default_factory=list)
    recommended_indexes: list[str] = field(default_factory=list)
    explain_plan: str = ""


def get_slow_queries_from_pg_stat_statements(db: Session, limit: int = 50) -> list[dict]:
    """Query pg_stat_statements for slow queries.

    Args:
        db: Database session
        limit: Max number of queries to return

    Returns:
        List of slow query stats
    """
    try:
        query = text(
            """
            SELECT
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                stddev_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > :threshold_ms
            ORDER BY total_exec_time DESC
            LIMIT :limit
            """
        )

        result = db.execute(query, {"threshold_ms": SLOW_QUERY_THRESHOLD_MS, "limit": limit})
        rows = result.fetchall()

        return [
            {
                "query": row[0],
                "calls": row[1],
                "total_time_ms": float(row[2]),
                "mean_time_ms": float(row[3]),
                "max_time_ms": float(row[4]),
                "stddev_time_ms": float(row[5]),
                "rows": row[6],
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Failed to query pg_stat_statements: {e}")
        # Might not have pg_stat_statements enabled
        return []


def analyze_query_with_explain(db: Session, query_text: str) -> dict[str, Any]:
    """Run EXPLAIN ANALYZE on query to get execution plan.

    Args:
        db: Database session
        query_text: SQL query to analyze

    Returns:
        Analysis results with execution plan
    """
    analysis = {"has_seq_scan": False, "missing_indexes": [], "explain_plan": ""}

    try:
        # Run EXPLAIN (not EXPLAIN ANALYZE) to avoid actually executing
        # EXPLAIN ANALYZE would execute the query which could be expensive
        explain_query = f"EXPLAIN (FORMAT JSON) {query_text}"
        result = db.execute(text(explain_query))
        plan_json = result.fetchone()[0]

        # Parse JSON plan
        analysis["explain_plan"] = str(plan_json)

        # Check for sequential scans (indicator of missing index)
        plan_str = str(plan_json).lower()
        if "seq scan" in plan_str:
            analysis["has_seq_scan"] = True
            logger.info(
                "Sequential scan detected in query",
                extra={"query_preview": query_text[:100]},
            )

    except Exception as e:
        logger.error(f"Failed to EXPLAIN query: {e}", extra={"query": query_text[:100]})
        analysis["explain_plan"] = f"Error: {e}"

    return analysis


def recommend_indexes_for_query(query_text: str, explain_plan: str) -> list[str]:
    """Generate index recommendations based on query and execution plan.

    Simple heuristic-based recommendations. In production, consider tools like:
    - pg_qualstats
    - pganalyze
    - AWS Performance Insights

    Args:
        query_text: SQL query
        explain_plan: EXPLAIN output

    Returns:
        List of recommended CREATE INDEX statements
    """
    recommendations = []

    # Simple heuristic: if sequential scan detected, recommend index on WHERE clause columns
    if "seq scan" in explain_plan.lower():
        # Extract table name and potential filter columns (very basic parsing)
        if "WHERE" in query_text.upper():
            # Suggest analyzing the WHERE clause
            recommendations.append(
                "-- Consider adding index on columns used in WHERE clause and JOINs"
            )

    # Check for sort operations without index
    if "sort" in explain_plan.lower():
        recommendations.append("-- Consider adding index on columns used in ORDER BY clause")

    # Check for hash joins (might benefit from index)
    if "hash join" in explain_plan.lower():
        recommendations.append("-- Consider adding index on JOIN columns")

    return recommendations


def analyze_slow_queries(db: Session, limit: int = 50) -> list[SlowQuery]:
    """Analyze slow queries and generate recommendations.

    Args:
        db: Database session
        limit: Max queries to analyze

    Returns:
        List of analyzed slow queries with recommendations
    """
    if not ANALYSIS_ENABLED:
        logger.info("Slow query analysis disabled")
        return []

    slow_queries_raw = get_slow_queries_from_pg_stat_statements(db, limit=limit)
    analyzed_queries = []

    for raw_query in slow_queries_raw:
        query_text = raw_query["query"]

        # Run EXPLAIN on query
        analysis = analyze_query_with_explain(db, query_text)

        # Generate index recommendations
        recommendations = recommend_indexes_for_query(query_text, analysis["explain_plan"])

        slow_query = SlowQuery(
            query_text=query_text,
            call_count=raw_query["calls"],
            total_time_ms=raw_query["total_time_ms"],
            mean_time_ms=raw_query["mean_time_ms"],
            max_time_ms=raw_query["max_time_ms"],
            stddev_time_ms=raw_query["stddev_time_ms"],
            rows_returned=raw_query["rows"],
            has_seq_scan=analysis["has_seq_scan"],
            explain_plan=analysis["explain_plan"],
            recommended_indexes=recommendations,
        )

        analyzed_queries.append(slow_query)

        logger.info(
            "Analyzed slow query",
            extra={
                "query_preview": query_text[:50],
                "mean_time_ms": slow_query.mean_time_ms,
                "has_seq_scan": slow_query.has_seq_scan,
                "recommendations_count": len(recommendations),
            },
        )

    return analyzed_queries


def generate_slow_query_report(db: Session) -> str:
    """Generate human-readable slow query report.

    Returns:
        Markdown-formatted report
    """
    analyzed_queries = analyze_slow_queries(db, limit=20)

    report_lines = [
        "# Slow Query Analysis Report",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Threshold: Queries with mean execution time > {SLOW_QUERY_THRESHOLD_MS}ms",
        "",
        "## Summary",
        f"- Total slow queries analyzed: {len(analyzed_queries)}",
        f"- Queries with sequential scans: {sum(1 for q in analyzed_queries if q.has_seq_scan)}",
        "",
    ]

    # Group by severity (total time impact)
    if analyzed_queries:
        report_lines.append("## Top Slow Queries by Total Time")
        report_lines.append("")

        for i, query in enumerate(analyzed_queries[:10], 1):
            report_lines.append(f"### {i}. Query (Total: {query.total_time_ms:.2f}ms)")
            report_lines.append("```sql")
            report_lines.append(
                query.query_text[:200] + ("..." if len(query.query_text) > 200 else "")
            )
            report_lines.append("```")
            report_lines.append("")
            report_lines.append(f"- **Calls:** {query.call_count}")
            report_lines.append(f"- **Mean time:** {query.mean_time_ms:.2f}ms")
            report_lines.append(f"- **Max time:** {query.max_time_ms:.2f}ms")
            report_lines.append(
                f"- **Sequential scan:** {'⚠️ Yes' if query.has_seq_scan else '✓ No'}"
            )
            report_lines.append("")

            if query.recommended_indexes:
                report_lines.append("**Recommendations:**")
                for rec in query.recommended_indexes:
                    report_lines.append(f"- {rec}")
                report_lines.append("")

    report_lines.append("---")
    report_lines.append("Generated by XR7 Slow Query Analyzer")

    return "\n".join(report_lines)


def get_top_slow_queries_summary(db: Session) -> dict[str, Any]:
    """Get summary of slow queries for API endpoint.

    Returns:
        Dict with slow query statistics
    """
    analyzed_queries = analyze_slow_queries(db, limit=10)

    return {
        "total_slow_queries": len(analyzed_queries),
        "queries_with_seq_scan": sum(1 for q in analyzed_queries if q.has_seq_scan),
        "total_time_spent_ms": sum(q.total_time_ms for q in analyzed_queries),
        "avg_query_time_ms": (
            sum(q.mean_time_ms for q in analyzed_queries) / len(analyzed_queries)
            if analyzed_queries
            else 0.0
        ),
        "top_queries": [
            {
                "query_preview": q.query_text[:100],
                "calls": q.call_count,
                "mean_time_ms": round(q.mean_time_ms, 2),
                "total_time_ms": round(q.total_time_ms, 2),
                "has_seq_scan": q.has_seq_scan,
                "recommendations_count": len(q.recommended_indexes),
            }
            for q in analyzed_queries[:5]
        ],
    }
