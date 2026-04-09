from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.llm.claim_drafter import claim_drafter
from XR7.models.claim import Claim
from XR7.recovery.immutable_ledger import ImmutableLedgerService


class AttorneyNetworkEscalator:
    def __init__(self, db: Session):
        self.db = db

    def partner_matching(self, claim: Claim) -> dict[str, Any]:
        amount = float(claim.recovered_amount or 0.0)
        if amount >= 25000:
            firm = "Nashville IP Litigation Group"
        elif amount >= 10000:
            firm = "Music Rights Counsel Nashville"
        else:
            firm = "Boutique Royalty Counsel"
        return {"firm": firm, "region": "Nashville", "tier": "A" if amount >= 10000 else "B"}

    async def auto_escalate_claim(self, claim_id: str) -> dict[str, Any]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError("Claim not found")

        letter = await claim_drafter.async_generate_demand_letter(
            {
                "id": claim.anomaly_id,
                "artist_id": claim.artist_id,
                "category": "ROYALTY",
                "subtype": "legal_escalation",
                "severity": "HIGH",
                "confidence_score": 0.8,
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            claim.evidence or {},
            claim.artist_id,
        )

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "claim.json", json.dumps({"id": claim.id, "artist_id": claim.artist_id}, indent=2)
            )
            zf.writestr("evidence.json", json.dumps(claim.evidence or {}, indent=2))
            zf.writestr("demand_letter.md", letter)

        attorney = self.partner_matching(claim)
        packet = {
            "claim_id": claim.id,
            "attorney": attorney,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bundle_bytes": len(zip_buf.getvalue()),
        }
        ImmutableLedgerService(self.db).append(claim.artist_id, "legal_escalation", packet)
        return packet

    def track_legal_outcomes(self, claim_id: str, settlement_amount: float) -> dict[str, Any]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError("Claim not found")
        claim.recovered_amount = float(settlement_amount)
        claim.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        ImmutableLedgerService(self.db).append(
            claim.artist_id,
            "legal_outcome",
            {
                "claim_id": claim_id,
                "settlement_amount": settlement_amount,
                "at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return {"claim_id": claim_id, "settlement_amount": settlement_amount, "updated": True}
