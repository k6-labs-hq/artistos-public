from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any


@dataclass(frozen=True)
class BlackBoxRule:
    payer: str
    royalty_scope: str
    window_min_days: int | None
    window_max_days: int | None
    redistribution_model: str
    note: str


# Centralized rule table for music + TV/film black-box expiration windows.
_RULES: dict[str, BlackBoxRule] = {
    # Music collection societies
    "ASCAP": BlackBoxRule("ASCAP", "music_performance", 365 * 2, 365 * 3, "redistributed", "ASCAP redistributes unmatched royalties after 2-3 years."),
    "BMI": BlackBoxRule("BMI", "music_performance", 365 * 2, 365 * 3, "redistributed", "BMI redistributes unmatched royalties after 2-3 years."),
    "SESAC": BlackBoxRule("SESAC", "music_performance", 365 * 2, 365 * 3, "redistributed", "SESAC redistributes unmatched royalties after 2-3 years."),
    "MLC": BlackBoxRule("MLC", "digital_mechanicals", 365 * 3, 365 * 3, "redistributed", "MLC redistributes unmatched digital mechanical royalties after 3 years."),
    "PRS": BlackBoxRule("PRS", "foreign_society", 365 * 3, 365 * 3, "redistributed", "PRS redistributes unmatched royalties after 3 years."),
    "GEMA": BlackBoxRule("GEMA", "foreign_society", 365 * 3, 365 * 3, "redistributed", "GEMA redistributes unmatched royalties after 3 years."),
    "SACEM": BlackBoxRule("SACEM", "foreign_society", 365 * 3, 365 * 3, "redistributed", "SACEM redistributes unmatched royalties after 3 years."),
    "JASRAC": BlackBoxRule("JASRAC", "foreign_society", 30 * 6, 30 * 18, "redistributed", "JASRAC often redistributes unmatched royalties after 6-18 months."),
    "SOCAN": BlackBoxRule("SOCAN", "foreign_society", 365 * 3, 365 * 3, "redistributed", "SOCAN redistributes unmatched royalties after 3 years."),
    "APRA": BlackBoxRule("APRA", "foreign_society", 365 * 2, 365 * 3, "redistributed", "APRA redistributes unmatched royalties after 2-3 years."),
    # TV/Film unions and residual societies
    "SAG-AFTRA": BlackBoxRule("SAG-AFTRA", "tvfilm_residuals", 365 * 2, 365 * 3, "redistributed", "SAG-AFTRA unmatched residuals are typically redistributed after 2-3 years."),
    "WGA": BlackBoxRule("WGA", "tvfilm_residuals", 365 * 2, 365 * 3, "redistributed", "WGA unmatched residuals are typically redistributed after 2-3 years."),
    "DGA": BlackBoxRule("DGA", "tvfilm_residuals", 365 * 2, 365 * 3, "redistributed", "DGA unmatched residuals are typically redistributed after 2-3 years."),
    "IATSE": BlackBoxRule("IATSE", "tvfilm_residuals", 365 * 2, 365 * 3, "redistributed", "IATSE unmatched residuals are typically redistributed after 2-3 years."),
    "FOREIGN_TVFILM": BlackBoxRule("FOREIGN_TVFILM", "tvfilm_foreign_residuals", 30 * 6, 30 * 18, "redistributed", "Foreign residual societies often redistribute unmatched residuals after 6-18 months."),
    # Contract-governed categories
    "STUDIO_BACKEND": BlackBoxRule("STUDIO_BACKEND", "contract_backend_participation", None, None, "contract_governed", "Studio backend participation is governed by contract terms, not black-box redistribution."),
    "STREAMING_REUSE": BlackBoxRule("STREAMING_REUSE", "contract_streaming_reuse", None, None, "contract_governed", "Streaming reuse recovery is governed by contract terms, not black-box redistribution."),
    "GENERIC": BlackBoxRule("GENERIC", "general_unmatched", 365 * 2, 365 * 3, "redistributed", "Generic unmatched royalty funds are often redistributed after 2-3 years."),
}


def _to_utc_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        iso = raw.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(iso)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _add_days(dt: datetime, days: int) -> datetime:
    return dt + timedelta(days=days)


# Avoid top-level import cycle concerns.
from datetime import timedelta  # noqa: E402


def get_rule(payer_or_society: str | None, royalty_type: str | None = None) -> BlackBoxRule:
    payer = str(payer_or_society or "").strip().upper()
    royalty = str(royalty_type or "").strip().upper()

    if "BACKEND" in royalty:
        return _RULES["STUDIO_BACKEND"]
    if "STREAMING_REUSE" in royalty or "REUSE" in royalty:
        return _RULES["STREAMING_REUSE"]

    if payer in _RULES:
        return _RULES[payer]
    if payer in {"FOREIGN", "FOREIGN_SOCIETY", "FOREIGN_RESIDUAL"}:
        if "TV" in royalty or "FILM" in royalty or "RESIDUAL" in royalty:
            return _RULES["FOREIGN_TVFILM"]
        return _RULES["JASRAC"]
    return _RULES["GENERIC"]


def infer_payer_and_royalty_type(anomaly_like: dict[str, Any]) -> tuple[str, str]:
    subtype = str(anomaly_like.get("subtype") or "").upper()
    description = str(anomaly_like.get("description") or "").upper()
    feature_snapshot = anomaly_like.get("feature_snapshot")
    snapshot: dict[str, Any] = {}
    if isinstance(feature_snapshot, dict):
        snapshot = feature_snapshot
    elif isinstance(feature_snapshot, str):
        try:
            import json

            parsed = json.loads(feature_snapshot)
            if isinstance(parsed, dict):
                snapshot = parsed
        except Exception:  # noqa: BLE001
            snapshot = {}

    explicit_payer = str(anomaly_like.get("payer") or anomaly_like.get("society") or snapshot.get("union") or snapshot.get("society") or "").strip()
    if explicit_payer:
        payer = explicit_payer
    elif any(x in subtype for x in ("ASCAP", "BMI", "SESAC", "MLC", "PRS", "GEMA", "SACEM", "JASRAC", "SOCAN", "APRA")):
        payer = next(x for x in ("ASCAP", "BMI", "SESAC", "MLC", "PRS", "GEMA", "SACEM", "JASRAC", "SOCAN", "APRA") if x in subtype)
    elif any(x in subtype for x in ("SAG", "WGA", "DGA", "IATSE")):
        if "SAG" in subtype:
            payer = "SAG-AFTRA"
        elif "WGA" in subtype:
            payer = "WGA"
        elif "DGA" in subtype:
            payer = "DGA"
        else:
            payer = "IATSE"
    elif "FOREIGN" in subtype or "FOREIGN" in description:
        payer = "FOREIGN_TVFILM" if "RESIDUAL" in subtype or "TV" in description or "FILM" in description else "JASRAC"
    elif "BACKEND" in subtype:
        payer = "STUDIO_BACKEND"
    elif "STREAMING_REUSE" in subtype or ("STREAMING" in subtype and "REUSE" in subtype):
        payer = "STREAMING_REUSE"
    else:
        payer = "GENERIC"

    if "BACKEND" in subtype:
        royalty_type = "backend_participation"
    elif "STREAMING" in subtype and "REUSE" in subtype:
        royalty_type = "streaming_reuse"
    elif "RESIDUAL" in subtype:
        royalty_type = "tvfilm_residuals"
    elif "MECHANICAL" in subtype or payer.upper() == "MLC":
        royalty_type = "digital_mechanicals"
    elif "FOREIGN" in subtype:
        royalty_type = "foreign_society_unmatched"
    elif "METADATA" in subtype or "IDENTIFIER" in subtype:
        royalty_type = "metadata_mismatch"
    else:
        royalty_type = "unmatched_royalties"

    return payer, royalty_type


def evaluate_black_box_expiration(
    *,
    payer_or_society: str | None,
    royalty_type: str | None,
    event_date: datetime | date | str | None,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    event_dt = _to_utc_datetime(event_date)
    now = as_of or datetime.now(timezone.utc)
    rule = get_rule(payer_or_society, royalty_type)

    if event_dt is None:
        return {
            "is_expired": False,
            "expiration_date": None,
            "days_remaining": None,
            "rule_applied": f"{rule.payer}:{rule.royalty_scope}",
            "explanation": f"Unable to evaluate expiration because event_date is missing. Rule context: {rule.note}",
        }

    if rule.redistribution_model == "contract_governed":
        return {
            "is_expired": False,
            "expiration_date": None,
            "days_remaining": None,
            "rule_applied": f"{rule.payer}:{rule.royalty_scope}",
            "explanation": rule.note,
        }

    min_days = int(rule.window_min_days or 0)
    max_days = int(rule.window_max_days or min_days)
    expiration_floor = _add_days(event_dt, min_days)
    expiration_ceiling = _add_days(event_dt, max_days)

    is_expired = now > expiration_ceiling
    days_remaining = int((expiration_ceiling - now).total_seconds() // 86400)
    if is_expired:
        days_remaining = 0

    if min_days == max_days:
        window_text = f"{max_days // 30} months" if max_days < 365 else f"{max_days // 365} years"
    else:
        if max_days < 365:
            window_text = f"{min_days // 30}-{max_days // 30} months"
        else:
            window_text = f"{min_days // 365}-{max_days // 365} years"

    return {
        "is_expired": is_expired,
        "expiration_date": expiration_ceiling.isoformat(),
        "days_remaining": max(days_remaining, 0),
        "rule_applied": f"{rule.payer}:{rule.royalty_scope}:{window_text}",
        "explanation": (
            f"Event date {event_dt.date().isoformat()} evaluated under {rule.payer} rule "
            f"({window_text} redistribution window). {rule.note} "
            f"Earliest redistribution estimate: {expiration_floor.date().isoformat()}."
        ),
    }


def evaluate_black_box_expiration_for_anomaly(anomaly_like: dict[str, Any], as_of: datetime | None = None) -> dict[str, Any]:
    payer, royalty_type = infer_payer_and_royalty_type(anomaly_like)
    event_date = (
        anomaly_like.get("event_date")
        or anomaly_like.get("time_window_end")
        or anomaly_like.get("time_window_start")
        or anomaly_like.get("created_at")
    )
    result = evaluate_black_box_expiration(
        payer_or_society=payer,
        royalty_type=royalty_type,
        event_date=event_date,
        as_of=as_of,
    )
    return {
        "payer_or_society": payer,
        "royalty_type": royalty_type,
        **result,
    }
