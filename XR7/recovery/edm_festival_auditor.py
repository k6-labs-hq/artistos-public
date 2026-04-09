from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.llm.claim_drafter import claim_drafter


class EDMFestivalAuditor:
    def detect_settlement_and_merch_discrepancies(
        self, settlements: list[dict[str, Any]], merch: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        total_settlement = sum(float(x.get("amount") or 0.0) for x in settlements)
        total_merch = sum(float(x.get("amount") or 0.0) for x in merch)
        delta = round(abs(total_settlement - total_merch), 2)
        if delta < 1:
            return []
        return [{"type": "edm_festival_delta", "delta": delta}]

    def analyze_recoupment_for_tour_packages(
        self, package_rows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        overage = round(
            sum(
                max(0.0, float(r.get("charged") or 0.0) - float(r.get("allowed") or 0.0))
                for r in package_rows
            ),
            2,
        )
        return {"recoupment_overage": overage, "rows": len(package_rows)}

    async def generate_audit_letter(self, artist_id: str, details: dict[str, Any]) -> str:
        return await claim_drafter.async_generate_demand_letter(
            {
                "id": "edm-audit",
                "artist_id": artist_id,
                "category": "TOURING",
                "subtype": "edm_festival",
                "severity": "HIGH",
                "confidence_score": 0.77,
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {"details": details, "integrity": {"packet_hash": "pending"}},
            artist_id,
        )
