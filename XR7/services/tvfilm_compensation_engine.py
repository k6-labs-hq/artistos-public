from __future__ import annotations

from typing import Any


UNION_BASE_RATES: dict[str, float] = {
    "SAG-AFTRA": 1.0,
    "WGA": 1.08,
    "DGA": 1.12,
    "IATSE": 0.98,
    "AFM/AFTRA": 1.05,
}

STUDIO_FACTORS: dict[str, float] = {
    "DISNEY": 1.06,
    "WB": 1.04,
    "NBCU": 1.03,
    "PARAMOUNT": 1.03,
    "SONY": 1.02,
    "NETFLIX": 1.08,
    "HULU": 1.03,
    "AMAZON": 1.05,
    "APPLE TV+": 1.07,
    "MAX": 1.04,
}

WINDOW_FACTORS: dict[str, float] = {
    "streaming": 1.1,
    "syndication": 1.18,
    "foreign": 1.16,
    "home video": 1.12,
    "fast": 1.09,
    "avod": 1.07,
    "svod": 1.11,
    "airline": 1.05,
    "educational": 1.03,
}

ROLE_FACTORS: dict[str, float] = {
    "showrunner": 1.2,
    "screenwriter": 1.14,
    "writer": 1.12,
    "director": 1.16,
    "producer": 1.12,
    "actor": 1.1,
    "voice actor": 1.08,
    "stunt performer": 1.22,
    "editor": 1.06,
    "cinematographer": 1.08,
    "composer": 1.1,
    "vfx artist": 1.04,
    "animator": 1.03,
    "crew": 1.0,
    "gaffer": 1.03,
    "grip": 1.03,
    "pa": 0.96,
}


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


def _normalized_label(value: Any) -> str:
    return str(value or "").strip().upper()


def _contains_factor(value: Any, catalog: dict[str, float], *, fallback: float = 1.0) -> tuple[str, float]:
    label = _normalized_label(value)
    for key, factor in catalog.items():
        if key in label:
            return key, factor
    return "GENERIC", fallback


def calculate_expected_compensation(row: dict[str, Any]) -> dict[str, Any]:
    paid_amount = _safe_float(row.get("amount_paid"))
    stated_expected = _safe_float(row.get("expected_amount"), default=paid_amount)
    overtime_hours = _safe_float(row.get("overtime_hours"))
    mileage = _safe_float(row.get("mileage_reimbursement"))
    kit_rental = _safe_float(row.get("kit_rental_fee"))
    meal_penalties = _safe_float(row.get("meal_penalties"))
    stunt_adjustment = _safe_float(row.get("stunt_adjustment"))
    turnaround_penalties = _safe_float(row.get("turnaround_penalties"))
    holiday_pay = _safe_float(row.get("holiday_pay"))

    union_name, union_factor = _contains_factor(row.get("union"), UNION_BASE_RATES)
    studio_name, studio_factor = _contains_factor(row.get("platform") or row.get("studio"), STUDIO_FACTORS)
    window_name, window_factor = _contains_factor(row.get("distribution_window") or row.get("market"), WINDOW_FACTORS)
    role_name, role_factor = _contains_factor(row.get("role"), ROLE_FACTORS)

    overtime_component = overtime_hours * max(paid_amount * 0.08, 35.0)
    variable_adjustments = mileage + kit_rental + meal_penalties + stunt_adjustment + turnaround_penalties + holiday_pay + overtime_component

    baseline = max(stated_expected, paid_amount)
    modeled_expected = round((baseline * union_factor * studio_factor * window_factor * role_factor) + variable_adjustments, 2)
    final_expected = round(max(modeled_expected, stated_expected, paid_amount), 2)
    delta = round(max(final_expected - paid_amount, 0.0), 2)

    confidence = 0.79
    if union_name != "GENERIC":
        confidence += 0.05
    if studio_name != "GENERIC":
        confidence += 0.04
    if window_name != "GENERIC":
        confidence += 0.04
    if role_name != "GENERIC":
        confidence += 0.03
    if variable_adjustments > 0:
        confidence += 0.04

    recommended_template = "STUDIO_GENERIC"
    if union_name in {"SAG-AFTRA", "WGA", "DGA", "IATSE", "AFM/AFTRA"}:
        recommended_template = union_name

    notes = [
        f"Union rule applied: {union_name} x {union_factor:.2f}",
        f"Studio/platform factor applied: {studio_name} x {studio_factor:.2f}",
        f"Distribution window factor applied: {window_name} x {window_factor:.2f}",
        f"Role factor applied: {role_name} x {role_factor:.2f}",
    ]
    if variable_adjustments > 0:
        notes.append(f"Payroll adjustments added: {variable_adjustments:.2f}")

    return {
        "union_rule": union_name,
        "studio_rule": studio_name,
        "window_rule": window_name,
        "role_rule": role_name,
        "expected_amount": final_expected,
        "baseline_expected_amount": round(baseline, 2),
        "actual_amount": round(paid_amount, 2),
        "delta": delta,
        "confidence": round(min(confidence, 0.98), 4),
        "recommended_template": recommended_template,
        "calculation_notes": notes,
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
