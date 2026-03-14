from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_universal_royalty_event(
    *,
    artist_id: str,
    source_type: str,
    source_name: str,
    record_type: str,
    event_type: str,
    amount: float,
    quantity: float,
    currency: str = "USD",
    territory: str | None = None,
    work_id: str | None = None,
    work_title: str | None = None,
    isrc: str | None = None,
    ipi: str | None = None,
    statement_period: str | None = None,
    source_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    unit_value = (amount / quantity) if quantity else 0.0
    return {
        "schema_version": "xr7.universal.royalty_event.v1",
        "artist_id": artist_id,
        "source_type": source_type,
        "source_name": source_name,
        "record_type": record_type,
        "event_type": event_type,
        "amount": round(float(amount), 6),
        "quantity": round(float(quantity), 6),
        "unit_value": round(float(unit_value), 6),
        "currency": currency,
        "territory": territory,
        "work_id": work_id,
        "work_title": work_title,
        "isrc": isrc,
        "ipi": ipi,
        "statement_period": statement_period,
        "source_ref": source_ref,
        "ingested_at": utc_now().isoformat(),
        "metadata": metadata or {},
    }
