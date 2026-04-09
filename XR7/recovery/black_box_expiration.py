from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
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


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    qq = _clamp(q)
    idx = qq * (len(sorted_values) - 1)
    lower = int(math.floor(idx))
    upper = int(math.ceil(idx))
    if lower == upper:
        return sorted_values[lower]
    frac = idx - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * frac


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


@dataclass
class SocietyFreezeEvent:
    payer_or_society: str
    freeze_started_at: datetime
    freeze_ended_at: datetime | None = None
    source: str = "manual"
    note: str = ""


class BlackBoxExpirationProbabilityModel:
    """Probabilistic expiration model using empirical survival curves per society/royalty type."""

    def __init__(self) -> None:
        self._durations_by_key: dict[tuple[str, str], list[float]] = {}
        self._freeze_events: dict[tuple[str, str], SocietyFreezeEvent] = {}
        self.model_version = "xr7-blackbox-prob-v1"

    def ingest_rows(self, rows: list[dict[str, Any]]) -> int:
        count = 0
        for row in rows:
            payer = str(row.get("payer_or_society") or row.get("society") or row.get("payer") or "").strip().upper()
            royalty_type = str(row.get("royalty_type") or "unmatched_royalties").strip().lower()
            event_dt = _to_utc_datetime(row.get("event_date"))
            redist_dt = _to_utc_datetime(row.get("redistributed_at"))
            if not payer or event_dt is None or redist_dt is None or redist_dt <= event_dt:
                continue
            duration_days = float((redist_dt - event_dt).total_seconds() / 86400.0)
            key = (payer, royalty_type)
            self._durations_by_key.setdefault(key, []).append(duration_days)
            count += 1
        for durations in self._durations_by_key.values():
            durations.sort()
        return count

    def ingest_csv(self, csv_path: str) -> int:
        rows: list[dict[str, Any]] = []
        with open(csv_path, encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                rows.append(dict(row))
        return self.ingest_rows(rows)

    def set_freeze_event(
        self,
        *,
        payer_or_society: str,
        royalty_type: str,
        freeze_started_at: datetime | str,
        freeze_ended_at: datetime | str | None = None,
        source: str = "manual",
        note: str = "",
    ) -> None:
        start_dt = _to_utc_datetime(freeze_started_at)
        if start_dt is None:
            return
        end_dt = _to_utc_datetime(freeze_ended_at)
        key = (str(payer_or_society).strip().upper(), str(royalty_type).strip().lower())
        self._freeze_events[key] = SocietyFreezeEvent(
            payer_or_society=key[0],
            freeze_started_at=start_dt,
            freeze_ended_at=end_dt,
            source=source,
            note=note,
        )

    def _durations_for_key(self, payer_or_society: str, royalty_type: str) -> list[float]:
        key = (payer_or_society.strip().upper(), royalty_type.strip().lower())
        if key in self._durations_by_key:
            return list(self._durations_by_key[key])
        payer_only_matches: list[float] = []
        for (payer, _rt), values in self._durations_by_key.items():
            if payer == key[0]:
                payer_only_matches.extend(values)
        if payer_only_matches:
            return sorted(payer_only_matches)
        rule = get_rule(payer_or_society, royalty_type)
        if rule.redistribution_model == "contract_governed":
            return []
        low = float(rule.window_min_days or 365 * 2)
        high = float(rule.window_max_days or low)
        if high < low:
            high = low
        return sorted([low, (low + high) / 2.0, high])

    def _elapsed_days_with_freeze(
        self,
        *,
        payer_or_society: str,
        royalty_type: str,
        event_dt: datetime,
        as_of: datetime,
    ) -> tuple[float, dict[str, Any] | None]:
        key = (payer_or_society.strip().upper(), royalty_type.strip().lower())
        freeze = self._freeze_events.get(key)
        if freeze is None:
            elapsed = float(max(0.0, (as_of - event_dt).total_seconds() / 86400.0))
            return elapsed, None

        start = freeze.freeze_started_at
        end = freeze.freeze_ended_at
        if end is None or end > as_of:
            effective_anchor = start if start > event_dt else event_dt
            elapsed = float(max(0.0, (as_of - effective_anchor).total_seconds() / 86400.0))
        else:
            frozen_days = max(0.0, (end - start).total_seconds() / 86400.0)
            base_elapsed = max(0.0, (as_of - event_dt).total_seconds() / 86400.0)
            elapsed = max(0.0, base_elapsed - frozen_days)

        return elapsed, {
            "freeze_started_at": start.isoformat(),
            "freeze_ended_at": end.isoformat() if end else None,
            "source": freeze.source,
            "note": freeze.note,
        }

    def predict(
        self,
        *,
        payer_or_society: str,
        royalty_type: str,
        event_date: datetime | date | str | None,
        as_of: datetime | None = None,
    ) -> dict[str, Any]:
        now = as_of or datetime.now(timezone.utc)
        event_dt = _to_utc_datetime(event_date)
        if event_dt is None:
            return {
                "P_already_redistributed": 0.0,
                "P_still_recoverable": 1.0,
                "p10_expiration_date": None,
                "p50_expiration_date": None,
                "p90_expiration_date": None,
                "redistribution_risk_score": 0,
                "days_remaining": None,
                "probability_narrative": "Insufficient event date data; XR7 defaults to recoverable pending additional evidence.",
                "model_version": self.model_version,
            }

        rule = get_rule(payer_or_society, royalty_type)
        if rule.redistribution_model == "contract_governed":
            return {
                "P_already_redistributed": 0.0,
                "P_still_recoverable": 1.0,
                "p10_expiration_date": None,
                "p50_expiration_date": None,
                "p90_expiration_date": None,
                "redistribution_risk_score": 0,
                "days_remaining": None,
                "probability_narrative": rule.note,
                "model_version": self.model_version,
            }

        durations = self._durations_for_key(payer_or_society, royalty_type)
        elapsed_days, freeze_context = self._elapsed_days_with_freeze(
            payer_or_society=payer_or_society,
            royalty_type=royalty_type,
            event_dt=event_dt,
            as_of=now,
        )

        n = max(len(durations), 1)
        redistributed_count = sum(1 for d in durations if d <= elapsed_days)
        p_redistributed = _clamp(redistributed_count / n)
        p_recoverable = _clamp(1.0 - p_redistributed)

        q10_days = _quantile(durations, 0.10)
        q50_days = _quantile(durations, 0.50)
        q90_days = _quantile(durations, 0.90)
        p10_date = _add_days(event_dt, int(round(q10_days))).isoformat()
        p50_date = _add_days(event_dt, int(round(q50_days))).isoformat()
        p90_date = _add_days(event_dt, int(round(q90_days))).isoformat()

        p50_exp_dt = _add_days(event_dt, int(round(q50_days)))
        days_remaining = max(0, int((p50_exp_dt - now).total_seconds() // 86400))

        redistribution_risk_score = int(round(_clamp(p_redistributed) * 100.0))
        if freeze_context:
            narrative = (
                f"{payer_or_society} has an active redistribution freeze signal. XR7 reset the timing clock to the freeze context "
                f"and currently estimates {p_recoverable:.1%} recoverability ({p_redistributed:.1%} redistributed risk)."
            )
        else:
            narrative = (
                f"XR7 estimates {p_recoverable:.1%} that funds are still recoverable and {p_redistributed:.1%} already redistributed, "
                f"using historical {payer_or_society} timing behavior for {royalty_type}."
            )

        out = {
            "P_already_redistributed": round(p_redistributed, 6),
            "P_still_recoverable": round(p_recoverable, 6),
            "p10_expiration_date": p10_date,
            "p50_expiration_date": p50_date,
            "p90_expiration_date": p90_date,
            "redistribution_risk_score": redistribution_risk_score,
            "days_remaining": days_remaining,
            "probability_narrative": narrative,
            "model_version": self.model_version,
        }
        if freeze_context:
            out["freeze_event"] = freeze_context
        return out


class SocietyBehaviorCalibrationJob:
    """Quarterly recalibration from confirmed redistribution events."""

    def __init__(self, model: BlackBoxExpirationProbabilityModel) -> None:
        self.model = model

    def recalibrate(self, confirmed_events: list[dict[str, Any]]) -> dict[str, Any]:
        ingested = self.model.ingest_rows(confirmed_events)
        societies = len({str((e.get("payer_or_society") or e.get("society") or "")).upper() for e in confirmed_events if e.get("payer_or_society") or e.get("society")})
        return {
            "job": "society_behavior_calibration",
            "ingested_events": ingested,
            "unique_societies": societies,
            "model_version": self.model.model_version,
            "recalibrated_at": datetime.now(timezone.utc).isoformat(),
        }


_DEFAULT_PROB_MODEL = BlackBoxExpirationProbabilityModel()


def evaluate_black_box_expiration_for_anomaly(anomaly_like: dict[str, Any], as_of: datetime | None = None) -> dict[str, Any]:
    payer, royalty_type = infer_payer_and_royalty_type(anomaly_like)
    event_date = (
        anomaly_like.get("event_date")
        or anomaly_like.get("time_window_end")
        or anomaly_like.get("time_window_start")
        or anomaly_like.get("created_at")
    )
    static_result = evaluate_black_box_expiration(
        payer_or_society=payer,
        royalty_type=royalty_type,
        event_date=event_date,
        as_of=as_of,
    )
    probability_result = _DEFAULT_PROB_MODEL.predict(
        payer_or_society=payer,
        royalty_type=royalty_type,
        event_date=event_date,
        as_of=as_of,
    )

    is_expired = static_result.get("is_expired")
    if not is_expired and probability_result.get("P_already_redistributed", 0.0) >= 0.9:
        is_expired = True

    return {
        "payer_or_society": payer,
        "royalty_type": royalty_type,
        **static_result,
        "is_expired": bool(is_expired),
        **probability_result,
    }


def register_society_freeze_event(
    *,
    payer_or_society: str,
    royalty_type: str,
    freeze_started_at: datetime | str,
    freeze_ended_at: datetime | str | None = None,
    source: str = "manual",
    note: str = "",
) -> None:
    _DEFAULT_PROB_MODEL.set_freeze_event(
        payer_or_society=payer_or_society,
        royalty_type=royalty_type,
        freeze_started_at=freeze_started_at,
        freeze_ended_at=freeze_ended_at,
        source=source,
        note=note,
    )


def train_black_box_expiration_probability_model_from_csv(csv_path: str) -> dict[str, Any]:
    ingested = _DEFAULT_PROB_MODEL.ingest_csv(csv_path)
    return {
        "ingested_events": ingested,
        "model_version": _DEFAULT_PROB_MODEL.model_version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }


def export_black_box_model_snapshot() -> dict[str, Any]:
    keys = [
        {"payer_or_society": payer, "royalty_type": rt, "samples": len(vals)}
        for (payer, rt), vals in sorted(_DEFAULT_PROB_MODEL._durations_by_key.items())
    ]
    return {
        "model_version": _DEFAULT_PROB_MODEL.model_version,
        "society_royalty_keys": keys,
        "freeze_events": {
            f"{k[0]}::{k[1]}": {
                "freeze_started_at": v.freeze_started_at.isoformat(),
                "freeze_ended_at": v.freeze_ended_at.isoformat() if v.freeze_ended_at else None,
                "source": v.source,
                "note": v.note,
            }
            for k, v in _DEFAULT_PROB_MODEL._freeze_events.items()
        },
    }
