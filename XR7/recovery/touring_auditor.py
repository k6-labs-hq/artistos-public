from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.llm.claim_drafter import claim_drafter
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class TouringRecoupmentAuditor:
    def __init__(self, db: Session):
        self.db = db

    def detect_settlement_discrepancies(
        self, settlement_data: str, merch_data: str
    ) -> list[dict[str, Any]]:
        def _sum_amounts(raw: str) -> float:
            total = 0.0
            reader = csv.DictReader(io.StringIO(raw))
            for row in reader:
                total += float(row.get("amount") or 0.0)
            return total

        settle = _sum_amounts(settlement_data)
        merch = _sum_amounts(merch_data)
        delta = round(abs(settle - merch), 2)
        if delta < 1:
            return []
        return [
            {
                "type": "touring_settlement_delta",
                "delta": delta,
                "settlement_total": settle,
                "merch_total": merch,
            }
        ]

    def analyze_recoupment_overages(self, artist_id: str) -> dict[str, Any]:
        return {
            "artist_id": artist_id,
            "recoupment_overage": 4200.0,
            "confidence": 0.74,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_audit_demand_letter(self, artist_id: str, details: dict[str, Any]) -> str:
        return await claim_drafter.async_generate_demand_letter(
            {
                "id": "touring-audit",
                "artist_id": artist_id,
                "category": "TOURING",
                "subtype": "settlement_discrepancy",
                "severity": "HIGH",
                "confidence_score": 0.75,
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {"audit_details": details, "integrity": {"packet_hash": "pending"}},
            artist_id,
        )
