from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from shared.utils.numbers import safe_float as _safe_float
from XR7.models.anomaly import AnomalyCategory, AnomalySeverity
from XR7.services.tvfilm_compensation_engine import calculate_expected_compensation

TVFILM_ROLE_OPTIONS = [
    "Writer (TV/Film)",
    "Screenwriter",
    "Showrunner",
    "Director",
    "Producer",
    "Actor",
    "Voice Actor",
    "Stunt Performer",
    "Editor",
    "Cinematographer",
    "Composer",
    "VFX Artist",
    "Animator",
    "Crew (Grip, Gaffer, PA, etc.)",
    "Reality TV Participant",
    "Documentary Creator",
    "Talent Agency",
    "Management Company",
    "Law Firm",
    "Production Company",
]

AGENCY_NAMES = [
    "WME",
    "CAA",
    "UTA",
    "Gersh",
    "APA",
    "Verve",
    "A3",
    "Paradigm",
    "Range Media",
    "Anonymous Content",
    "Management 360",
    "Mosaic",
]

STATEMENT_CATALOG = {
    "sag_aftra_residuals": ["sag", "aftra", "residual", "episode", "production"],
    "wga_residuals": ["wga", "residual", "writer", "episode", "production"],
    "dga_residuals": ["dga", "residual", "director", "episode", "production"],
    "iatse_residuals": ["iatse", "residual", "crew", "production", "episode"],
    "afm_aftra_music_film": ["afm", "aftra", "cue", "music", "residual"],
    "studio_residuals": ["studio", "disney", "wb", "nbcu", "paramount", "sony", "residual"],
    "streaming_residuals": ["netflix", "hulu", "amazon", "apple", "max", "stream", "residual"],
    "foreign_residuals": ["foreign", "society", "territory", "residual"],
    "production_payroll": ["call sheet", "timecard", "overtime", "meal penalty", "kit rental"],
    "distribution_licensing": ["syndication", "home video", "fast", "avod", "svod", "international"],
    "ugc_social_clips": ["content id", "youtube", "tiktok", "reels", "clip licensing", "viral"],
}

ANOMALY_RULE_CATALOG: dict[str, list[str]] = {
    "residuals": [
        "MISSING_RESIDUAL_PAYMENT",
        "UNDERPAID_RESIDUAL",
        "INCORRECT_REUSE_CATEGORY",
        "INCORRECT_MARKET_CLASSIFICATION",
        "INCORRECT_DISTRIBUTION_WINDOW",
        "MISSING_FOREIGN_RESIDUALS",
        "MISSING_STREAMING_RESIDUALS",
        "INCORRECT_EPISODE_COUNT",
        "INCORRECT_SEASON_COUNT",
        "INCORRECT_CREDITED_ROLE",
    ],
    "production_payments": [
        "MISSING_DAY_RATE",
        "INCORRECT_OVERTIME_CALCULATION",
        "INCORRECT_MEAL_PENALTIES",
        "INCORRECT_KIT_RENTAL_FEES",
        "INCORRECT_MILEAGE_REIMBURSEMENT",
        "INCORRECT_TURNAROUND_PENALTIES",
        "INCORRECT_HOLIDAY_PAY",
        "INCORRECT_STUNT_ADJUSTMENTS",
    ],
    "licensing_distribution": [
        "MISSING_SYNDICATION_REVENUE",
        "MISSING_INTERNATIONAL_DISTRIBUTION_REVENUE",
        "MISSING_HOME_VIDEO_REVENUE",
        "MISSING_FAST_AVOD_REVENUE",
        "INCORRECT_BACKEND_PARTICIPATION",
    ],
    "ugc_social": [
        "MISSING_CONTENT_ID_CLAIMS",
        "MISSING_CLIP_LICENSING_PAYOUTS",
        "MISSING_VIRAL_REUSE_MONETIZATION",
    ],
    "metadata_drift": [
        "EPISODE_SEASON_MISMATCH",
        "PRODUCTION_ID_MISMATCH",
        "CHARACTER_ROLE_MISMATCH",
        "CREDIT_ORDER_INCONSISTENCY",
        "MISSING_ROLE_METADATA",
    ],
}

EVIDENCE_PACKET_TEMPLATES: dict[str, dict[str, Any]] = {
    "WGA": {"required_sections": ["writer_contract_excerpt", "residual_schedule", "episode_credit_sheet", "payment_delta_table"]},
    "SAG-AFTRA": {"required_sections": ["performer_contract_excerpt", "reuse_category_table", "market_window_matrix", "payment_delta_table"]},
    "DGA": {"required_sections": ["directorial_terms", "distribution_window_matrix", "residual_calc_sheet", "payment_delta_table"]},
    "IATSE": {"required_sections": ["crew_timesheet", "overtime_penalty_grid", "turnaround_penalty_grid", "payment_delta_table"]},
    "AFM/AFTRA": {"required_sections": ["cue_sheet", "usage_logs", "distribution_usage_table", "payment_delta_table"]},
    "STUDIO_GENERIC": {"required_sections": ["deal_memo", "platform_distribution_extract", "territory_breakdown", "payment_delta_table"]},
}

ANOMALY_TO_CATEGORY = {
    "residuals": AnomalyCategory.ROYALTY,
    "production_payments": AnomalyCategory.PLATFORM,
    "licensing_distribution": AnomalyCategory.SYNC,
    "ugc_social": AnomalyCategory.PLATFORM,
    "metadata_drift": AnomalyCategory.BRAND,
}


@dataclass
class ParsePreview:
    statement_type: str
    normalized_rows: list[dict[str, Any]]
    repaired_fields: list[str]
    warnings: list[str]


def list_all_anomaly_rules() -> list[str]:
    rules: list[str] = []
    for values in ANOMALY_RULE_CATALOG.values():
        rules.extend(values)
    return rules


def detect_statement_type(headers: list[str]) -> str:
    normalized = " ".join(h.lower() for h in headers)
    best_type = "unknown_tvfilm_statement"
    best_score = 0
    for statement_type, markers in STATEMENT_CATALOG.items():
        score = sum(1 for marker in markers if marker in normalized)
        if score > best_score:
            best_score = score
            best_type = statement_type
    return best_type


def _normalize_production_id(raw: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]", "", raw or "")
    if not text:
        return "UNKNOWN_PRODUCTION"
    return text.upper()


def _normalize_episode(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"[^0-9]", "", value)
    return f"E{digits}" if digits else None


def _normalize_season(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"[^0-9]", "", value)
    return f"S{digits}" if digits else None


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def parse_statement_preview(raw_bytes: bytes, *, filename: str) -> ParsePreview:
    text = _decode_text(raw_bytes)
    delimiter = "\t" if filename.lower().endswith(".tsv") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    headers = list(reader.fieldnames or [])
    statement_type = detect_statement_type(headers)

    normalized_rows: list[dict[str, Any]] = []
    repaired_fields: list[str] = []
    warnings: list[str] = []

    for row in reader:
        production_id = _normalize_production_id(str(row.get("production_id") or row.get("production") or row.get("show_id") or ""))
        role_value = str(row.get("role") or row.get("credited_role") or "").strip() or "Unspecified"
        episode = _normalize_episode(str(row.get("episode") or row.get("episode_number") or ""))
        season = _normalize_season(str(row.get("season") or row.get("season_number") or ""))

        amount_paid = _safe_float(row.get("amount_paid"))
        expected_amount = _safe_float(row.get("expected_amount"), default=amount_paid)
        if expected_amount < amount_paid:
            expected_amount = amount_paid
            repaired_fields.append("expected_amount_clamped")

        normalized_row = {
            "production_id": production_id,
            "production_title": str(row.get("production_title") or row.get("title") or "Unknown Production").strip(),
            "season": season,
            "episode": episode,
            "role": role_value,
            "union": str(row.get("union") or "").strip() or None,
            "market": str(row.get("market") or "").strip() or None,
            "distribution_window": str(row.get("distribution_window") or "").strip() or None,
            "platform": str(row.get("platform") or "").strip() or None,
            "expected_amount": round(expected_amount, 2),
            "amount_paid": round(amount_paid, 2),
            "delta": round(expected_amount - amount_paid, 2),
            "source_row": row,
        }

        calculation = calculate_expected_compensation({**row, **normalized_row})
        normalized_row["stated_expected_amount"] = normalized_row["expected_amount"]
        normalized_row["expected_amount"] = float(calculation["expected_amount"])
        normalized_row["delta"] = round(float(calculation["delta"]), 2)
        normalized_row["recommended_template"] = calculation["recommended_template"]
        normalized_row["calculation_confidence"] = float(calculation["confidence"])
        normalized_row["calculation_notes"] = list(calculation["calculation_notes"])
        normalized_row["calculation_breakdown"] = calculation

        normalized_rows.append(normalized_row)

    if not normalized_rows:
        warnings.append("No parseable rows were found in file.")
    if statement_type == "unknown_tvfilm_statement":
        warnings.append("Format not confidently recognized; parser used generic TV/Film normalization.")

    return ParsePreview(
        statement_type=statement_type,
        normalized_rows=normalized_rows,
        repaired_fields=sorted(set(repaired_fields)),
        warnings=warnings,
    )


def infer_anomaly_subtype(row: dict[str, Any]) -> tuple[str, str]:
    delta = float(row.get("delta") or 0.0)
    distribution_window = str(row.get("distribution_window") or "").lower()
    market = str(row.get("market") or "").lower()
    platform = str(row.get("platform") or "").lower()
    role = str(row.get("role") or "").lower()

    if delta <= 0.0:
        if "clip" in platform or "youtube" in platform or "tiktok" in platform:
            return "ugc_social", "MISSING_CLIP_LICENSING_PAYOUTS"
        return "metadata_drift", "MISSING_ROLE_METADATA"

    if "foreign" in market:
        return "residuals", "MISSING_FOREIGN_RESIDUALS"
    if "stream" in distribution_window or "netflix" in platform or "hulu" in platform:
        return "residuals", "MISSING_STREAMING_RESIDUALS"
    if "synd" in distribution_window:
        return "licensing_distribution", "MISSING_SYNDICATION_REVENUE"
    if "stunt" in role:
        return "production_payments", "INCORRECT_STUNT_ADJUSTMENTS"
    if "crew" in role or "gaffer" in role or "grip" in role:
        return "production_payments", "INCORRECT_OVERTIME_CALCULATION"
    return "residuals", "UNDERPAID_RESIDUAL"


def severity_for_delta(delta: float) -> AnomalySeverity:
    amount = abs(float(delta))
    if amount >= 50000:
        return AnomalySeverity.CRITICAL
    if amount >= 10000:
        return AnomalySeverity.HIGH
    if amount >= 2000:
        return AnomalySeverity.MEDIUM
    return AnomalySeverity.LOW


def forecast_from_amounts(*, base_amount: float, confidence: float) -> dict[str, Any]:
    conf = max(0.35, min(0.99, float(confidence)))

    def _band(multiplier: float) -> dict[str, float]:
        expected = round(base_amount * multiplier, 2)
        spread = round(expected * (1.0 - conf) * 0.6, 2)
        return {
            "low": round(max(expected - spread, 0.0), 2),
            "expected": expected,
            "high": round(expected + spread, 2),
        }

    return {
        "30_day": _band(0.15),
        "60_day": _band(0.32),
        "90_day": _band(0.49),
        "180_day": _band(0.85),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def portfolio_rollup(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_missing = 0.0
    total_underpayments = 0.0
    total_backend_missing = 0.0
    by_role: dict[str, dict[str, float]] = {}
    by_union: dict[str, dict[str, float]] = {}
    by_platform: dict[str, dict[str, float]] = {}

    for row in rows:
        est = _safe_float(row.get("estimated_missing"))
        underpay = _safe_float(row.get("estimated_underpayment"))
        backend = _safe_float(row.get("estimated_backend_missing"))
        role = str(row.get("role") or "Unspecified")
        union_name = str(row.get("union") or "Unspecified")
        platform = str(row.get("platform") or "Unspecified")

        total_missing += est
        total_underpayments += underpay
        total_backend_missing += backend

        role_bucket = by_role.setdefault(role, {"total": 0.0, "clients": 0.0})
        role_bucket["total"] += est + underpay + backend
        role_bucket["clients"] += 1.0

        union_bucket = by_union.setdefault(union_name, {"total": 0.0, "clients": 0.0})
        union_bucket["total"] += est + underpay + backend
        union_bucket["clients"] += 1.0

        platform_bucket = by_platform.setdefault(platform, {"total": 0.0, "clients": 0.0})
        platform_bucket["total"] += est + underpay + backend
        platform_bucket["clients"] += 1.0

    sol_risk_ratio = 0.0
    if rows:
        risky = sum(1 for row in rows if str(row.get("sol_risk") or "").lower() in {"high", "expired", "urgent"})
        sol_risk_ratio = round(risky / max(len(rows), 1), 4)

    return {
        "roster_size": len(rows),
        "total_residuals_missing": round(total_missing, 2),
        "total_underpayments": round(total_underpayments, 2),
        "total_backend_participation_missing": round(total_backend_missing, 2),
        "sol_risk_ratio": sol_risk_ratio,
        "role_level_insights": {k: {"total": round(v["total"], 2), "clients": int(v["clients"])} for k, v in by_role.items()},
        "union_level_insights": {k: {"total": round(v["total"], 2), "clients": int(v["clients"])} for k, v in by_union.items()},
        "platform_level_insights": {k: {"total": round(v["total"], 2), "clients": int(v["clients"])} for k, v in by_platform.items()},
    }


def to_json(value: Any) -> str:
    return json.dumps(value, default=str, separators=(",", ":"))
