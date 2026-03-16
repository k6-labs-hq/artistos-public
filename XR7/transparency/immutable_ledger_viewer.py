from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.llm.claim_drafter import claim_drafter
from XR7.models.anomaly import Anomaly
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry
from XR7.models.universal_royalty_event import UniversalRoyaltyEvent


class ImmutableLedgerViewer:
    def __init__(self, db: Session):
        self.db = db

    def get_full_ledger(self, artist_id: str, include_raw_statements: bool = True) -> dict[str, Any]:
        ledger_rows = (
            self.db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .all()
        )
        events = (
            self.db.query(UniversalRoyaltyEvent)
            .filter(UniversalRoyaltyEvent.artist_id == artist_id)
            .order_by(UniversalRoyaltyEvent.ingested_at.desc())
            .limit(500)
            .all()
        )
        return {
            "artist_id": artist_id,
            "entries": [
                {
                    "id": r.id,
                    "entry_type": r.entry_type,
                    "payload_json": r.payload_json if include_raw_statements else "{}",
                    "entry_hash": r.entry_hash,
                    "prior_hash": r.prior_hash,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in ledger_rows
            ],
            "universal_events": [
                {
                    "id": e.id,
                    "source_name": e.source_name,
                    "work_id": e.work_id,
                    "amount": e.amount,
                    "metadata_json": e.metadata_json if include_raw_statements else "{}",
                }
                for e in events
            ],
        }

    async def explain_anomaly(self, anomaly_id: str) -> dict[str, Any]:
        anomaly = self.db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise ValueError("Anomaly not found")
        question = (
            "Explain in simple terms exactly why this anomaly was flagged and the math behind the estimated recoverable amount"
        )
        response = await claim_drafter.async_generate_personalized_advice(
            {
                "anomaly": {
                    "id": anomaly.id,
                    "category": str(anomaly.category),
                    "subtype": anomaly.subtype,
                    "estimated_recoverable": anomaly.estimated_recoverable,
                    "confidence": anomaly.confidence_score,
                },
                "question": question,
            }
        )
        return {"anomaly_id": anomaly_id, "explanation": response}

    def generate_math_proof_pdf(self, artist_id: str) -> dict[str, Any]:
        return {
            "artist_id": artist_id,
            "pdf_note": "PDF generation delegated to existing claim evidence export pipeline.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
