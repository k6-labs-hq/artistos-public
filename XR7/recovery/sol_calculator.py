from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from XR7.utils.datetime_utils import as_utc as _as_utc


SOL_DISCLAIMER = "Statute windows are informational only and may vary by forum, tolling rules, and contract terms. Consult qualified counsel before filing."


def _normalize_code(value: str | None, fallback: str) -> str:
    raw = (value or "").strip().upper()
    if not raw:
        return fallback
    return raw


def _normalize_contract_type(value: str | None, fallback: str) -> str:
    raw = (value or "").strip().lower()
    if raw in {"recording", "publishing", "distribution"}:
        return raw
    return fallback


def _load_rules() -> dict[str, Any]:
    path = Path(__file__).with_name("sol_jurisdictions.json")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def calculate_sol(
    *,
    governing_law_state: str | None,
    contract_type: str | None,
    infringement_date: datetime | str | None,
    discovery_date: datetime | str | None,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    rules = _load_rules()
    jurisdictions = rules.get("jurisdictions") or {}
    default_jurisdiction = str(rules.get("default_jurisdiction") or "USA")
    default_contract_type = str(rules.get("default_contract_type") or "recording")

    jurisdiction = _normalize_code(governing_law_state, default_jurisdiction)
    if jurisdiction not in jurisdictions:
        jurisdiction = default_jurisdiction

    ctype = _normalize_contract_type(contract_type, default_contract_type)
    j_rules = jurisdictions.get(jurisdiction) or {}
    c_rules = j_rules.get(ctype) or (jurisdictions.get(default_jurisdiction) or {}).get(default_contract_type) or {}

    years = int(c_rules.get("years") or 3)
    citation = str(c_rules.get("citation") or "Rule unavailable")

    discovered = _as_utc(discovery_date)
    infringed = _as_utc(infringement_date)
    anchor = discovered or infringed
    if anchor is None:
        return {
            "governing_law_state": jurisdiction,
            "contract_type": ctype,
            "sol_window_years": years,
            "sol_citation_source": citation,
            "sol_deadline": None,
            "sol_days_remaining": None,
            "sol_status": "UNKNOWN",
            "legal_disclaimer": SOL_DISCLAIMER,
        }

    deadline = anchor + timedelta(days=years * 365)
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    days = int((deadline - now).total_seconds() // 86400)

    if days < 0:
        status = "EXPIRED"
    elif days <= 90:
        status = "URGENT"
    elif days <= 180:
        status = "AT_RISK"
    else:
        status = "OK"

    return {
        "governing_law_state": jurisdiction,
        "contract_type": ctype,
        "sol_window_years": years,
        "sol_citation_source": citation,
        "sol_deadline": deadline,
        "sol_days_remaining": days,
        "sol_status": status,
        "legal_disclaimer": SOL_DISCLAIMER,
    }