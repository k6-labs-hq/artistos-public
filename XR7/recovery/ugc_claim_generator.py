from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.llm.claim_drafter import claim_drafter
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from XR7.recovery.attorney_escalation import AttorneyNetworkEscalator
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class UGCClaimGenerator:
    def __init__(self, db: Session):
        self.db = db

    def generate_from_ugc(
        self, use_data: dict[str, Any], platform: str, artist_id: str
    ) -> dict[str, Any]:
        lower_platform = platform.lower()
        if lower_platform in {"tiktok", "instagram"}:
            subtype = "UGC_SYNC"
        elif lower_platform == "soundcloud":
            subtype = "SOUNDCLOUD_REPOST_RECONCILIATION"
        else:
            subtype = "CONTENT_ID"
        views = float(use_data.get("views") or 0.0)
        estimated = round(views * 0.0013, 2)
        return {
            "artist_id": artist_id,
            "platform": platform,
            "subtype": subtype,
            "estimated_recoverable": estimated,
            "use_data": use_data,
        }

    def auto_attach_evidence(self, use_data: dict[str, Any]) -> dict[str, Any]:
        packet = {
            "ugc_use": use_data,
            "evidence_links": [use_data.get("url")],
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "chain_of_custody": {
                "source": "ugc_capture_pipeline",
                "integrity_mode": "hash_linked",
                "captured_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        packet["evidence_packet_id"] = f"ugc-packet-{abs(hash(str(packet))) % 10_000_000}"
        return packet

    async def draft_claim_letter(self, use_data: dict[str, Any], artist_id: str) -> str:
        return await claim_drafter.async_generate_demand_letter(
            {
                "id": "ugc-anomaly",
                "artist_id": artist_id,
                "category": "ROYALTY",
                "subtype": "ugc_sync",
                "severity": "HIGH",
                "confidence_score": 0.8,
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            {"ugc_use": use_data, "integrity": {"packet_hash": "pending"}},
            artist_id,
        )

    async def auto_escalate_if_high_value(
        self, claim_id: str, threshold: float = 5000.0
    ) -> dict[str, Any]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            return {"escalated": False, "reason": "claim_not_found"}
        if float(claim.recovered_amount or 0.0) < threshold:
            return {"escalated": False, "reason": "below_threshold"}
        packet = await AttorneyNetworkEscalator(self.db).auto_escalate_claim(claim_id)
        return {"escalated": True, "packet": packet}

    async def create_claim(self, artist_id: str, platform: str, use_data: dict[str, Any]) -> str:
        claim_dict = self.generate_from_ugc(use_data, platform, artist_id)
        anomaly = Anomaly(
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype=str(claim_dict["subtype"]).lower(),
            severity=AnomalySeverity.HIGH,
            status=AnomalyStatus.OPEN,
            confidence_score=0.79,
            estimated_recoverable=claim_dict["estimated_recoverable"],
            description=f"Unreported {platform} usage detected",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(anomaly)
        self.db.commit()
        self.db.refresh(anomaly)

        evidence = self.auto_attach_evidence(use_data)
        evidence["draft_letter"] = await self.draft_claim_letter(use_data, artist_id)

        claim = Claim(
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="UGC_RECOVERY",
            status=ClaimStatus.IDENTIFIED,
            recovered_amount=claim_dict["estimated_recoverable"],
            currency="USD",
            evidence=evidence,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)

        await self.auto_escalate_if_high_value(claim.id)
        return claim.id
