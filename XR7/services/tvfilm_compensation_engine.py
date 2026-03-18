"""
TV/Film Compensation Engine — per-union MBA schedule logic.

Each union function implements the residual/compensation formula from the
applicable Minimum Basic Agreement (MBA) as of the 2023 negotiating cycle.
Rates are expressed in USD. Where a range applies the midpoint is used unless
the caller supplies a budget_tier hint.

Union coverage:
  SAG-AFTRA  — 2023 Theatrical & Television MBA
  WGA        — 2023 Minimum Basic Agreement (SVOD, network TV, syndication)
  DGA        — 2023 DGA Basic Agreement (TV and theatrical)
  IATSE      — 2021 Production Basic Agreement (crew classifications)
  AFM/AFTRA  — American Federation of Musicians side-letter schedules
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _safe_float(value: Any, *, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip().replace(",", "").replace("$", "")
    if text in {"", "-", "N/A", "na", "None"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def _label(value: Any) -> str:
    return str(value or "").strip().upper()


def _match_key(label: str, keys: list[str]) -> str | None:
    for k in keys:
        if k.upper() in label:
            return k
    return None


# ---------------------------------------------------------------------------
# SAG-AFTRA 2023 MBA — streaming (SVOD/AVOD) and traditional TV residuals
#
# Sources: SAG-AFTRA 2023 Theatrical and Television Basic Agreement;
#          2020 SVOD Supplement (updated 2023).
#
# SVOD/AVOD flat residuals per episode (actors at scale):
#   Budget tier LOW   (<$1M/ep)   : $1,600/half-hr  | $3,200/hour
#   Budget tier MID   ($1-2.5M/ep): $2,200/half-hr  | $4,400/hour
#   Budget tier HIGH  (>$2.5M/ep) : $4,080/half-hr  | $8,160/hour  (2023)
#
# Traditional network TV reruns (per run percentage of initial compensation):
#   Run 1: 100 %   Run 2: 75 %   Run 3: 50 %   Runs 4 +: 40 %
#
# Syndication domestic: 30 % of initial per episode per run
# Foreign residuals:   15 % of initial per episode per market per run
# Home video (phys.):   4.5 % of distributor's gross above break-even
# ---------------------------------------------------------------------------

_SAGAFTRA_SVOD_FLAT: dict[str, dict[str, float]] = {
    "LOW":  {"half_hour": 1_600.0, "hour": 3_200.0},
    "MID":  {"half_hour": 2_200.0, "hour": 4_400.0},
    "HIGH": {"half_hour": 4_080.0, "hour": 8_160.0},
}

_SAGAFTRA_RERUN_PCT: dict[int, float] = {1: 1.0, 2: 0.75, 3: 0.50}
_SAGAFTRA_RERUN_DEFAULT = 0.40

_SAGAFTRA_SYNDICATION_PCT = 0.30
_SAGAFTRA_FOREIGN_PCT = 0.15
_SAGAFTRA_HOME_VIDEO_PCT = 0.045


def _sagaftra_expected(row: dict[str, Any], paid: float, stated: float, window: str, role: str) -> tuple[float, float, list[str]]:
    budget_tier = str(row.get("budget_tier") or "MID").upper()
    if budget_tier not in _SAGAFTRA_SVOD_FLAT:
        budget_tier = "MID"

    ep_runtime = str(row.get("episode_runtime") or "hour").lower()
    runtime_key = "half_hour" if "30" in ep_runtime or "half" in ep_runtime else "hour"
    ep_count = max(1, int(_safe_float(row.get("episode_count") or 1)))
    run_number = max(1, int(_safe_float(row.get("run_number") or 1)))

    confidence = 0.82
    notes: list[str] = []

    if "STREAM" in window or "SVOD" in window or "AVOD" in window:
        flat_rate = _SAGAFTRA_SVOD_FLAT[budget_tier][runtime_key]
        expected = flat_rate * ep_count
        notes.append(f"SAG-AFTRA 2023 SVOD flat residual: ${flat_rate:,.0f}/{runtime_key} × {ep_count} ep(s) = ${expected:,.0f}")
        confidence += 0.10
    elif "SYNDICATION" in window or "DOMESTIC" in window:
        run_pct = _SAGAFTRA_RERUN_PCT.get(run_number, _SAGAFTRA_RERUN_DEFAULT)
        expected = stated * run_pct * ep_count if stated else paid * 1.30 * ep_count
        notes.append(f"SAG-AFTRA syndication: {run_pct*100:.0f}% of initial per ep × {ep_count} ep(s) — run #{run_number}")
        confidence += 0.08
    elif "FOREIGN" in window:
        expected = stated * _SAGAFTRA_FOREIGN_PCT * ep_count if stated else paid * 1.15 * ep_count
        notes.append(f"SAG-AFTRA foreign residual: {_SAGAFTRA_FOREIGN_PCT*100:.1f}% of initial × {ep_count} ep(s)")
        confidence += 0.07
    elif "HOME VIDEO" in window or "DVD" in window:
        distributor_gross = _safe_float(row.get("distributor_gross"), default=paid * 2.5)
        expected = distributor_gross * _SAGAFTRA_HOME_VIDEO_PCT
        notes.append(f"SAG-AFTRA home video: {_SAGAFTRA_HOME_VIDEO_PCT*100:.1f}% of distributor gross ${distributor_gross:,.0f} = ${expected:,.0f}")
        confidence += 0.06
    else:
        # Network TV / cable — use stated or inflate paid
        run_pct = _SAGAFTRA_RERUN_PCT.get(run_number, _SAGAFTRA_RERUN_DEFAULT)
        expected = max(stated, paid * (1.0 + run_pct * 0.25))
        notes.append(f"SAG-AFTRA network/cable run #{run_number}: {run_pct*100:.0f}% rerun rate applied")
        confidence += 0.06

    # Stunt performer premium (10 % above scale)
    if "STUNT" in role:
        expected *= 1.10
        notes.append("SAG-AFTRA stunt performer premium: +10% above scale")
        confidence += 0.04

    return expected, confidence, notes


# ---------------------------------------------------------------------------
# WGA 2023 MBA — SVOD, network TV, syndication, theatrical
#
# SVOD supplement (2023): 2 % of "applicable minimum" allocated per episode
#   counted against writer's credited participation.
# Network TV reruns: 100 % first rerun, 75 % second, 50 % third–fifth.
# Syndication: 4 % of applicable minimum per episode per run.
# Theatrical: separated rights — 1.5 % of distributor's gross >=$1.2M.
# Script/story fees: guaranteed minimum $45,000 (TV half-hr), $90,000 (hour)
# ---------------------------------------------------------------------------

_WGA_TV_MIN: dict[str, float] = {"half_hour": 45_000.0, "hour": 90_000.0}
_WGA_SVOD_PCT = 0.02
_WGA_SYNDICATION_PCT = 0.04
_WGA_THEATRICAL_PCT = 0.015
_WGA_THEATRICAL_THRESHOLD = 1_200_000.0
_WGA_RERUN_PCT: dict[int, float] = {1: 1.0, 2: 0.75, 3: 0.50, 4: 0.50, 5: 0.50}
_WGA_RERUN_DEFAULT = 0.40


def _wga_expected(row: dict[str, Any], paid: float, stated: float, window: str, role: str) -> tuple[float, float, list[str]]:
    runtime_key = "half_hour" if "30" in str(row.get("episode_runtime") or "").lower() or "half" in str(row.get("episode_runtime") or "").lower() else "hour"
    ep_count = max(1, int(_safe_float(row.get("episode_count") or 1)))
    run_number = max(1, int(_safe_float(row.get("run_number") or 1)))
    is_theatrical = "FILM" in _label(row.get("production_type") or "") or "THEATRICAL" in window

    confidence = 0.80
    notes: list[str] = []

    if is_theatrical:
        dist_gross = _safe_float(row.get("distributor_gross"), default=max(stated, paid) * 3.0)
        if dist_gross > _WGA_THEATRICAL_THRESHOLD:
            expected = dist_gross * _WGA_THEATRICAL_PCT
        else:
            expected = max(stated, paid)
        notes.append(f"WGA theatrical separate rights: {_WGA_THEATRICAL_PCT*100:.1f}% of dist. gross ${dist_gross:,.0f} = ${expected:,.0f}")
        confidence += 0.08
    elif "STREAM" in window or "SVOD" in window or "AVOD" in window:
        applicable_min = _WGA_TV_MIN[runtime_key]
        svod_per_ep = applicable_min * _WGA_SVOD_PCT
        expected = svod_per_ep * ep_count
        notes.append(f"WGA 2023 SVOD: {_WGA_SVOD_PCT*100:.0f}% of ${applicable_min:,.0f} applicable min × {ep_count} ep(s) = ${expected:,.0f}")
        confidence += 0.09
    elif "SYNDICATION" in window:
        applicable_min = _WGA_TV_MIN[runtime_key]
        expected = applicable_min * _WGA_SYNDICATION_PCT * ep_count
        notes.append(f"WGA syndication: {_WGA_SYNDICATION_PCT*100:.0f}% of ${applicable_min:,.0f} × {ep_count} ep(s) = ${expected:,.0f}")
        confidence += 0.08
    else:
        run_pct = _WGA_RERUN_PCT.get(run_number, _WGA_RERUN_DEFAULT)
        applicable_min = _WGA_TV_MIN[runtime_key]
        expected = applicable_min * run_pct * ep_count
        notes.append(f"WGA network rerun #{run_number}: {run_pct*100:.0f}% of ${applicable_min:,.0f} × {ep_count} = ${expected:,.0f}")
        confidence += 0.07

    return expected, confidence, notes


# ---------------------------------------------------------------------------
# DGA 2023 Basic Agreement — television and theatrical
#
# Television (network + cable):
#   First rerun: 45 % of minimum; reruns 2–5: 22.5 % each; 6+: 15 %.
# SVOD (2023 supplement):
#   5 % of "applicable minimum" per episode for credited director.
# Theatrical:
#   1.5 % of distributor's gross >$1M for feature directors.
# Pay TV / Streaming bonus: $4,000 per episode for qualifying SVOD (2023).
# ---------------------------------------------------------------------------

_DGA_TV_MIN_PER_EP: dict[str, float] = {"half_hour": 38_000.0, "hour": 76_000.0}
_DGA_RERUN_PCT: dict[int, float] = {1: 0.45, 2: 0.225, 3: 0.225, 4: 0.225, 5: 0.225}
_DGA_RERUN_DEFAULT = 0.15
_DGA_SVOD_PCT = 0.05
_DGA_SVOD_BONUS_PER_EP = 4_000.0
_DGA_THEATRICAL_PCT = 0.015
_DGA_THEATRICAL_THRESHOLD = 1_000_000.0


def _dga_expected(row: dict[str, Any], paid: float, stated: float, window: str, role: str) -> tuple[float, float, list[str]]:
    runtime_key = "half_hour" if "30" in str(row.get("episode_runtime") or "").lower() or "half" in str(row.get("episode_runtime") or "").lower() else "hour"
    ep_count = max(1, int(_safe_float(row.get("episode_count") or 1)))
    run_number = max(1, int(_safe_float(row.get("run_number") or 1)))
    is_theatrical = "FILM" in _label(row.get("production_type") or "") or "THEATRICAL" in window

    confidence = 0.81
    notes: list[str] = []

    if is_theatrical:
        dist_gross = _safe_float(row.get("distributor_gross"), default=max(stated, paid) * 4.0)
        if dist_gross > _DGA_THEATRICAL_THRESHOLD:
            expected = dist_gross * _DGA_THEATRICAL_PCT
        else:
            expected = max(stated, paid)
        notes.append(f"DGA theatrical: {_DGA_THEATRICAL_PCT*100:.1f}% of dist. gross ${dist_gross:,.0f} = ${expected:,.0f}")
        confidence += 0.07
    elif "STREAM" in window or "SVOD" in window or "AVOD" in window:
        applicable_min = _DGA_TV_MIN_PER_EP[runtime_key]
        per_ep = applicable_min * _DGA_SVOD_PCT + _DGA_SVOD_BONUS_PER_EP
        expected = per_ep * ep_count
        notes.append(
            f"DGA 2023 SVOD: {_DGA_SVOD_PCT*100:.0f}% of ${applicable_min:,.0f} + ${_DGA_SVOD_BONUS_PER_EP:,.0f} bonus × {ep_count} ep(s) = ${expected:,.0f}"
        )
        confidence += 0.10
    else:
        run_pct = _DGA_RERUN_PCT.get(run_number, _DGA_RERUN_DEFAULT)
        applicable_min = _DGA_TV_MIN_PER_EP[runtime_key]
        expected = applicable_min * run_pct * ep_count
        notes.append(f"DGA TV rerun #{run_number}: {run_pct*100:.1f}% of ${applicable_min:,.0f} × {ep_count} = ${expected:,.0f}")
        confidence += 0.07

    return expected, confidence, notes


# ---------------------------------------------------------------------------
# IATSE 2021 Production Basic Agreement — crew classifications
#
# Overtime: time-and-a-half past 8 hrs/day, double-time past 12 hrs/day.
# Meal penalty: $7.50 per violation (6-hr max without meal break).
# Kit rental: listed minimum $30/day for specific departments.
# Turnaround violation: $100 per hour (<9-hr turnaround for IATSE).
# Holiday pay: 1.5× daily rate.
# Flat daily rates vary by classification — using journeyman DP scale (2021).
# ---------------------------------------------------------------------------

_IATSE_DAILY_RATE_BY_ROLE: dict[str, float] = {
    "CINEMATOGRAPHER": 790.0,
    "EDITOR": 720.0,
    "VFX ARTIST": 680.0,
    "GAFFER": 650.0,
    "GRIP": 600.0,
    "PA": 250.0,
    "CREW": 420.0,
}
_IATSE_OVERTIME_MULT = 1.5
_IATSE_DOUBLETIME_MULT = 2.0
_IATSE_MEAL_PENALTY = 7.50
_IATSE_KIT_RENTAL_MIN = 30.0
_IATSE_TURNAROUND_PENALTY = 100.0
_IATSE_HOLIDAY_MULT = 1.5


def _iatse_expected(row: dict[str, Any], paid: float, stated: float, window: str, role: str) -> tuple[float, float, list[str]]:
    role_upper = role.upper()
    role_key = _match_key(role_upper, list(_IATSE_DAILY_RATE_BY_ROLE.keys())) or "CREW"
    daily_rate = _IATSE_DAILY_RATE_BY_ROLE[role_key]

    shoot_days = max(1, int(_safe_float(row.get("shoot_days") or 1)))
    overtime_hours = _safe_float(row.get("overtime_hours"))
    meal_violations = int(_safe_float(row.get("meal_violations") or 0))
    kit_days = int(_safe_float(row.get("kit_rental_days") or 0))
    turnaround_violations_hrs = _safe_float(row.get("turnaround_violation_hours") or 0.0)
    holiday_days = int(_safe_float(row.get("holiday_days") or 0))

    base = daily_rate * shoot_days
    ot_component = overtime_hours * (daily_rate / 8.0) * _IATSE_OVERTIME_MULT
    meal_component = meal_violations * _IATSE_MEAL_PENALTY
    kit_component = kit_days * _IATSE_KIT_RENTAL_MIN
    turnaround_component = turnaround_violations_hrs * _IATSE_TURNAROUND_PENALTY
    holiday_component = holiday_days * daily_rate * (_IATSE_HOLIDAY_MULT - 1.0)

    expected = base + ot_component + meal_component + kit_component + turnaround_component + holiday_component
    expected = max(expected, stated, paid)

    notes = [
        f"IATSE 2021 PBA: ${daily_rate:.0f}/day × {shoot_days} days = ${base:,.0f}",
    ]
    if ot_component:
        notes.append(f"Overtime: {overtime_hours}h @ 1.5× = ${ot_component:,.2f}")
    if meal_component:
        notes.append(f"Meal penalties: {meal_violations} × ${_IATSE_MEAL_PENALTY} = ${meal_component:,.2f}")
    if kit_component:
        notes.append(f"Kit rental: {kit_days} days × ${_IATSE_KIT_RENTAL_MIN} = ${kit_component:,.2f}")
    if turnaround_component:
        notes.append(f"Turnaround violations: {turnaround_violations_hrs}h × ${_IATSE_TURNAROUND_PENALTY} = ${turnaround_component:,.2f}")
    if holiday_component:
        notes.append(f"Holiday premium: {holiday_days} days @ 0.5× = ${holiday_component:,.2f}")

    confidence = 0.78 + (0.08 if role_key != "CREW" else 0.0)
    return expected, confidence, notes


# ---------------------------------------------------------------------------
# AFM/AFTRA — music side letters (TV/Film scoring and recording)
#
# Network TV session rates (2022): $430/3-hr session per musician.
# Streaming step-up: 20 % above scale for qualifying SVOD productions.
# Theatrical reuse: 25 % of original session fee.
# Foreign reuse: 15 % of original session fee per territory.
# ---------------------------------------------------------------------------

_AFM_SESSION_RATE = 430.0
_AFM_SVOD_PREMIUM_PCT = 0.20
_AFM_THEATRICAL_REUSE_PCT = 0.25
_AFM_FOREIGN_REUSE_PCT = 0.15


def _afm_expected(row: dict[str, Any], paid: float, stated: float, window: str, role: str) -> tuple[float, float, list[str]]:
    sessions = max(1, int(_safe_float(row.get("recording_sessions") or 1)))
    territories = max(1, int(_safe_float(row.get("foreign_territories") or 1)))

    confidence = 0.76
    notes: list[str] = []

    base = _AFM_SESSION_RATE * sessions
    if "STREAM" in window or "SVOD" in window:
        expected = base * (1 + _AFM_SVOD_PREMIUM_PCT)
        notes.append(f"AFM SVOD step-up: ${_AFM_SESSION_RATE:.0f}/session × {sessions} sessions × 1.20 = ${expected:,.0f}")
        confidence += 0.10
    elif "FOREIGN" in window:
        expected = base * _AFM_FOREIGN_REUSE_PCT * territories
        notes.append(f"AFM foreign reuse: {_AFM_FOREIGN_REUSE_PCT*100:.0f}% × {territories} territories = ${expected:,.0f}")
        confidence += 0.07
    elif "THEATRICAL" in window:
        expected = base * _AFM_THEATRICAL_REUSE_PCT
        notes.append(f"AFM theatrical reuse: {_AFM_THEATRICAL_REUSE_PCT*100:.0f}% of ${base:,.0f} = ${expected:,.0f}")
        confidence += 0.08
    else:
        expected = base
        notes.append(f"AFM session rate: ${_AFM_SESSION_RATE:.0f} × {sessions} sessions = ${base:,.0f}")
        confidence += 0.05

    expected = max(expected, stated, paid)
    return expected, confidence, notes


# ---------------------------------------------------------------------------
# Router: pick the right union engine, then apply payroll adjustments
# ---------------------------------------------------------------------------

_UNION_ORDER = [
    ("SAG-AFTRA", _sagaftra_expected),
    ("WGA", _wga_expected),
    ("DGA", _dga_expected),
    ("IATSE", _iatse_expected),
    ("AFM", _afm_expected),
]

# Platform tier escalation — studios with established step-up agreements
_PLATFORM_STEP_UP: dict[str, float] = {
    "NETFLIX": 0.08,
    "APPLE TV+": 0.07,
    "AMAZON": 0.05,
    "DISNEY": 0.06,
    "HBO": 0.06,
    "MAX": 0.05,
    "HULU": 0.03,
    "WB": 0.04,
    "NBCU": 0.03,
    "PARAMOUNT": 0.03,
    "SONY": 0.02,
}


def calculate_expected_compensation(row: dict[str, Any]) -> dict[str, Any]:
    """
    Run union-engine residual calculation for a single statement row.

    Required row keys (at minimum):
      union, role, distribution_window, amount_paid
    Optional but impactful:
      expected_amount, episode_count, run_number, episode_runtime,
      budget_tier, production_type, distributor_gross, shoot_days,
      overtime_hours, meal_violations, kit_rental_days,
      turnaround_violation_hours, holiday_days, recording_sessions
    """
    paid = _safe_float(row.get("amount_paid"))
    stated = _safe_float(row.get("expected_amount"), default=paid)

    union_label = _label(row.get("union"))
    role_label = _label(row.get("role"))
    window_label = _label(row.get("distribution_window") or row.get("market"))
    platform_label = _label(row.get("platform") or row.get("studio"))

    # Dispatch to union-specific engine
    union_matched = "STUDIO_GENERIC"
    expected_from_schedule = max(stated, paid)
    schedule_confidence = 0.72
    schedule_notes: list[str] = []
    for union_key, fn in _UNION_ORDER:
        if union_key in union_label:
            union_matched = union_key
            expected_from_schedule, schedule_confidence, schedule_notes = fn(row, paid, stated, window_label, role_label)
            break

    # Platform step-up escalation (separate from union schedule)
    platform_matched = "GENERIC"
    platform_step = 0.0
    for plat_key, step_pct in _PLATFORM_STEP_UP.items():
        if plat_key in platform_label:
            platform_matched = plat_key
            platform_step = step_pct
            break
    expected_after_platform = expected_from_schedule * (1.0 + platform_step)
    if platform_step > 0:
        schedule_notes.append(f"Platform step-up ({platform_matched}): +{platform_step*100:.0f}% = ${expected_after_platform:,.0f}")

    # Payroll adjustments (union-agnostic)
    overtime_hours = _safe_float(row.get("overtime_hours"))
    mileage = _safe_float(row.get("mileage_reimbursement"))
    kit_rental = _safe_float(row.get("kit_rental_fee"))
    meal_penalties = _safe_float(row.get("meal_penalties"))
    stunt_adjustment = _safe_float(row.get("stunt_adjustment"))
    turnaround_penalties = _safe_float(row.get("turnaround_penalties"))
    holiday_pay = _safe_float(row.get("holiday_pay"))
    overtime_component = overtime_hours * max(paid * 0.08, 35.0)
    payroll_adjustments = (
        mileage + kit_rental + meal_penalties + stunt_adjustment
        + turnaround_penalties + holiday_pay + overtime_component
    )
    if payroll_adjustments > 0:
        schedule_notes.append(f"Payroll adjustments: ${payroll_adjustments:,.2f}")

    final_expected = round(max(expected_after_platform + payroll_adjustments, stated, paid), 2)
    delta = round(max(final_expected - paid, 0.0), 2)

    # Confidence boost for complete data
    if payroll_adjustments > 0:
        schedule_confidence = min(schedule_confidence + 0.03, 0.98)

    recommended_template = union_matched if union_matched != "STUDIO_GENERIC" else "STUDIO_GENERIC"

    return {
        "union_rule": union_matched,
        "studio_rule": platform_matched,
        "window_rule": window_label or "GENERIC",
        "role_rule": role_label or "GENERIC",
        "expected_amount": final_expected,
        "baseline_expected_amount": round(max(stated, paid), 2),
        "actual_amount": round(paid, 2),
        "delta": delta,
        "confidence": round(min(schedule_confidence, 0.98), 4),
        "recommended_template": recommended_template,
        "calculation_notes": schedule_notes,
        "adjustments": {
            "overtime_component": round(overtime_component, 2),
            "mileage": round(mileage, 2),
            "kit_rental": round(kit_rental, 2),
            "meal_penalties": round(meal_penalties, 2),
            "stunt_adjustment": round(stunt_adjustment, 2),
            "turnaround_penalties": round(turnaround_penalties, 2),
            "holiday_pay": round(holiday_pay, 2),
        },
    }
