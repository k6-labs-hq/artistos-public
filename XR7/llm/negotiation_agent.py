from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.claim import Claim
from XR7.recovery.attorney_escalation import AttorneyNetworkEscalator
from XR7.recovery.immutable_ledger import ImmutableLedgerService


class AutonomousNegotiatorAgent:
    def __init__(self, db: Session):
        self.db = db

    def auto_draft_and_submit_claim(self, claim_id: str) -> dict[str, Any]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError("Claim not found")
        payload = {
            "claim_id": claim_id,
            "submitted_via": "simulated_email_api",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        ImmutableLedgerService(self.db).append(claim.artist_id, "negotiator_submit", payload)
        return payload

    def run_negotiation_rounds(self, claim_id: str, rounds: int = 3) -> dict[str, Any]:
        rounds_log = []
        for idx in range(1, rounds + 1):
            rounds_log.append(
                {
                    "round": idx,
                    "counter_offer": f"{max(40, 100 - idx*12)}% of demand",
                    "status": "simulated",
                }
            )
        return {"claim_id": claim_id, "rounds": rounds_log}

    async def escalate_to_attorney_network(self, claim_id: str) -> dict[str, Any]:
        return await AttorneyNetworkEscalator(self.db).auto_escalate_claim(claim_id)
