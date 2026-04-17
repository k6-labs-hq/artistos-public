"""Claim status audit event listener.

Automatically logs claim status transitions to immutable_ledger_entries table
to provide tamper-proof audit trail for legal compliance and dispute resolution.

This uses SQLAlchemy event listeners instead of database triggers, making it:
  - Database-agnostic (works with PostgreSQL, SQLite, MySQL)
  - Testable in local development
  - Easier to debug and maintain
  - Consistent with application code patterns

The listener fires BEFORE UPDATE on claim objects and creates an immutable
ledger entry when status changes, with hash chaining for tamper detection.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.orm import Session

from XR7.models.claim import Claim
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry, compute_entry_hash


def log_claim_status_change(mapper, connection, target: Claim) -> None:  # noqa: ARG001
    """
    Log claim status changes to immutable ledger.

    This event listener fires before a claim is updated. If the status has changed,
    it creates an immutable ledger entry with:
      - claim_id, old_status, new_status, timestamp
      - Hash chain linking to previous ledger entry for this artist
      - SHA256 hash preventing tampering

    Args:
        mapper: SQLAlchemy mapper (unused)
        connection: Database connection
        target: Claim object being updated
    """
    # Get the old status from database state
    history = target.__dict__.get("_sa_instance_state").attrs.get("status").history
    if not history.has_changes():
        return  # Status didn't change, nothing to log

    old_status = history.deleted[0] if history.deleted else None
    new_status = target.status

    if old_status == new_status:
        return  # No actual change

    # Get session from connection
    session = Session(bind=connection)

    # Get most recent ledger entry for this artist to maintain hash chain
    prior_entry = (
        session.query(ImmutableLedgerEntry)
        .filter(ImmutableLedgerEntry.artist_id == target.artist_id)
        .order_by(ImmutableLedgerEntry.created_at.desc())
        .first()
    )

    prior_hash = prior_entry.entry_hash if prior_entry else None

    # Build payload with transition details
    payload = {
        "claim_id": target.id,
        "old_status": old_status,
        "new_status": new_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claim_type": target.claim_type,
        "recovered_amount": float(target.recovered_amount) if target.recovered_amount else None,
        "currency": target.currency,
    }
    payload_json = json.dumps(payload, sort_keys=True)

    # Compute hash for tamper detection
    entry_hash = compute_entry_hash(
        artist_id=target.artist_id,
        entry_type="CLAIM_STATUS_CHANGE",
        payload_json=payload_json,
        prior_hash=prior_hash,
    )

    # Create immutable ledger entry
    ledger_entry = ImmutableLedgerEntry(
        artist_id=target.artist_id,
        entry_type="CLAIM_STATUS_CHANGE",
        payload_json=payload_json,
        prior_hash=prior_hash,
        entry_hash=entry_hash,
    )

    session.add(ledger_entry)
    session.flush()  # Ensure entry is written before claim update completes


# Register event listener to fire before claim updates
event.listen(Claim, "before_update", log_claim_status_change)
