from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.llm.claim_drafter import claim_drafter
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus


class HipHopBrandAuditor:
    def __init__(self, db: Session):
        self.db = db

    async def scan_brand_deals_and_ugc(self, artist_id: str) -> list[dict[str, Any]]:
        return [
            {
                "artist_id": artist_id,
                "platform": "instagram",
                "placement": "brand sync in sneaker campaign",
                "estimated_value": 7800.0,
                "url": "https://example.com/brand-sync",
                "confidence": 0.82,
            }
        ]

    def calculate_lost_value(self, item: dict[str, Any]) -> float:
        return round(float(item.get("estimated_value") or 0.0), 2)

    def generate_evidence_packet(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "source": "hiphop_brand_audit",
            "item": item,
            "estimated_recoverable": self.calculate_lost_value(item),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def auto_create_claim(self, artist_id: str, item: dict[str, Any]) -> str:
        anomaly = Anomaly(
            artist_id=artist_id,
            category=AnomalyCategory.BRAND,
            subtype="hiphop_brand_ugc",
            severity=AnomalySeverity.HIGH,
            confidence_score=float(item.get("confidence") or 0.7),
            estimated_recoverable=self.calculate_lost_value(item),
            status=AnomalyStatus.OPEN,
            description=str(item.get("placement") or "Brand UGC discrepancy"),
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(anomaly)
        self.db.commit()
        self.db.refresh(anomaly)

        evidence = self.generate_evidence_packet(item)
        letter = await claim_drafter.async_generate_demand_letter(
            {
                "id": anomaly.id,
                "artist_id": artist_id,
                "category": "BRAND",
                "subtype": "hiphop_brand_ugc",
                "severity": "HIGH",
                "confidence_score": float(item.get("confidence") or 0.7),
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            evidence,
            artist_id,
        )
        evidence["llm_demand_letter"] = letter

        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="BRAND_UGC",
            status=ClaimStatus.IDENTIFIED,
            recovered_amount=evidence["estimated_recoverable"],
            currency="USD",
            evidence=evidence,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        return claim.id
