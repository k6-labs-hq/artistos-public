from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry, compute_entry_hash


class ImmutableLedgerService:
    def __init__(self, db: Session):
        self.db = db

    def append(self, artist_id: str, entry_type: str, payload: dict[str, Any]) -> ImmutableLedgerEntry:
        prior = (
            self.db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .first()
        )
        payload_json = json.dumps(payload, sort_keys=True)
        prior_hash = prior.entry_hash if prior else None
        entry_hash = compute_entry_hash(
            artist_id=artist_id,
            entry_type=entry_type,
            payload_json=payload_json,
            prior_hash=prior_hash,
        )
        entry = ImmutableLedgerEntry(
            artist_id=artist_id,
            entry_type=entry_type,
            payload_json=payload_json,
            prior_hash=prior_hash,
            entry_hash=entry_hash,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_entries(self, artist_id: str) -> list[ImmutableLedgerEntry]:
        return (
            self.db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .all()
        )
