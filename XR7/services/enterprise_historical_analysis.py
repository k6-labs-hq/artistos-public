from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(value).strip().replace(",", "").replace("$", "")
    if text in {"", "-", "N/A", "na", "None"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _risk_bucket(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"critical", "high", "urgent"}:
        return "high"
    if raw in {"medium", "watch"}:
        return "medium"
    if raw in {"low", "ok"}:
        return "low"
    return "unknown"


def _vertical(value: Any) -> str:
    raw = str(value or "MUSIC").strip().upper()
    if raw in {"TV", "FILM", "TV_FILM", "TV/FILM", "TV&FILM"}:
        return "TV_FILM"
    return "MUSIC"


def _record_recoverable(record: dict[str, Any]) -> float:
    # Supports both music and tv/film field naming conventions.
    keys = [
        "estimated_missing",
        "estimated_underpayment",
        "estimated_backend_missing",
        "estimated_royalty_gap",
        "estimated_unpaid_performance",
        "estimated_unpaid_sync",
        "estimated_unpaid_neighboring",
        "estimated_mechanical_gap",
        "estimated_residual_gap",
        "estimated_ugc_gap",
    ]
    return round(sum(max(_safe_float(record.get(k)), 0.0) for k in keys), 2)


def analyze_historical_portfolio(
    *,
    organization_name: str,
    entity_type: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    if not records:
        raise ValueError("records must not be empty")

    risk_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    vertical_summary: dict[str, dict[str, Any]] = {
        "MUSIC": {"clients": 0, "estimated_recoverable": 0.0},
        "TV_FILM": {"clients": 0, "estimated_recoverable": 0.0},
    }
    client_rows: list[dict[str, Any]] = []

    for row in records:
        client_name = str(
            row.get("client")
            or row.get("client_name")
            or row.get("artist")
            or row.get("name")
            or "Unknown Client"
        ).strip()
        vertical = _vertical(row.get("vertical"))
        recoverable = _record_recoverable(row)
        risk = _risk_bucket(row.get("sol_risk") or row.get("risk") or row.get("risk_level"))

        risk_counts[risk] += 1
        vertical_summary[vertical]["clients"] += 1
        vertical_summary[vertical]["estimated_recoverable"] = round(
            float(vertical_summary[vertical]["estimated_recoverable"]) + recoverable,
            2,
        )

        client_rows.append(
            {
                "client": client_name,
                "vertical": vertical,
                "estimated_recoverable": recoverable,
                "sol_risk": risk,
                "platform": row.get("platform"),
                "union": row.get("union"),
                "payer": row.get("payer") or row.get("distributor") or row.get("studio"),
            }
        )

    ranked = sorted(client_rows, key=lambda x: float(x["estimated_recoverable"]), reverse=True)
    total_estimated_recoverable = round(sum(float(r["estimated_recoverable"]) for r in ranked), 2)

    now = datetime.now(timezone.utc)
    return {
        "organization_name": organization_name,
        "entity_type": entity_type,
        "analysis_completed_at": now.isoformat(),
        "roster_size": len(records),
        "total_estimated_recoverable": total_estimated_recoverable,
        "by_vertical": vertical_summary,
        "sol_risk": risk_counts,
        "top_25_clients": ranked[:25],
        "execution_plan": {
            "next_24h": [
                "Ingest final roster and statement exports (CSV/TSV/XLSX) for all available clients.",
                "Run historical rollup and rank clients by recoverable value and SOL urgency.",
                "Open claim/evidence workstreams for top high-risk, high-value cohort first.",
            ],
            "next_7d": [
                "Complete anomaly and claim packet generation for top 20% of recoverable value.",
                "Parallel legal/partner outreach on key-needed connectors and external records.",
                "Stand up weekly executive rollup dashboard for agency leadership.",
            ],
        },
        "tomorrow_meeting_checklist": [
            "Client roster with vertical tag (MUSIC or TV_FILM).",
            "Historical statements/exports per client (distributor, PRO, studio/platform, ticketing where applicable).",
            "Temporary legal authorization or agency attestation for data review.",
            "Operator credentials and environment keys for any direct API connectors.",
            "Decision owners for legal escalation and payout routing.",
        ],
    }
