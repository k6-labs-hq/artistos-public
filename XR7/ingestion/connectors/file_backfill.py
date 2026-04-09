from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from XR7.ingestion.statement_parser import parse_statement_file
from XR7.utils.datetime_utils import as_utc as _as_utc


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return _as_utc(value)

    text = str(value).strip()
    if not text:
        return None

    # Common statement formats: YYYY-MM-DD, YYYY-MM, ISO8601.
    for candidate in (text, f"{text}-01"):
        try:
            dt = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            return _as_utc(dt)
        except Exception:  # noqa: BLE001
            continue
    return None


def _within_range(ts: datetime | None, start: datetime | None, end: datetime | None) -> bool:
    if ts is None:
        return True
    start_utc = _as_utc(start)
    end_utc = _as_utc(end)
    if start_utc and ts < start_utc:
        return False
    if end_utc and ts > end_utc:
        return False
    return True


def _coerce_row(event: dict[str, Any], *, source_name: str) -> dict[str, Any]:
    return {
        "artist_id": event.get("artist_id"),
        "work_id": event.get("isrc") or event.get("work_id"),
        "quantity": float(event.get("quantity") or 0.0),
        "unit_value": float(event.get("unit_value") or 0.0),
        "currency": event.get("currency") or "USD",
        "territory": event.get("territory"),
        "timestamp": event.get("timestamp"),
        "platform": event.get("platform") or source_name,
        "event_type": event.get("event_type") or "STREAM",
    }


def _read_paths(config: dict[str, Any], env_name: str) -> list[Path]:
    raw: list[str] = []
    cfg_files = config.get("statement_files")
    cfg_file = config.get("statement_file")
    env_files = config.get("statement_files_env")

    if isinstance(cfg_files, list):
        raw.extend(str(x) for x in cfg_files if str(x).strip())
    elif isinstance(cfg_files, str) and cfg_files.strip():
        raw.extend([x.strip() for x in cfg_files.split(",") if x.strip()])

    if cfg_file:
        raw.append(str(cfg_file))

    if env_files:
        raw.extend([x.strip() for x in str(env_files).split(",") if x.strip()])

    env_value = config.get("env_override")
    if not env_value:
        import os

        env_value = os.environ.get(env_name, "")
    if env_value:
        raw.extend([x.strip() for x in str(env_value).split(",") if x.strip()])

    paths: list[Path] = []
    for item in raw:
        p = Path(item)
        if p.exists() and p.is_file():
            paths.append(p)
    return paths


def load_statement_rows(
    *,
    config: dict[str, Any],
    source_name: str,
    env_name: str,
    artist_id: str,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[dict[str, Any]]:
    """Load normalized connector rows from configured local statement files.

    This allows production-safe fallback ingestion for connectors that do not
    yet have direct partner APIs, while avoiding hard stubs.
    """

    rows: list[dict[str, Any]] = []
    paths = _read_paths(config, env_name)
    for path in paths:
        content = path.read_bytes()
        parsed = parse_statement_file(content, artist_id, filename=path.name)
        for event in parsed.events:
            row = _coerce_row(event, source_name=source_name)
            ts = _parse_timestamp(row.get("timestamp"))
            if _within_range(ts, start, end):
                rows.append(row)
    return rows
