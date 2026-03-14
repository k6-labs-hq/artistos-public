from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.payer_risk_model import payer_risk_score

router = APIRouter(tags=["payers"])


def _claim_payer(claim: Claim) -> str:
    evidence = claim.evidence or {}
    if isinstance(evidence, dict):
        legal = evidence.get("legal_support", {})
        contracts = legal.get("contract_basis", []) if isinstance(legal, dict) else []
        if contracts and isinstance(contracts, list):
            counterparty = str((contracts[0] or {}).get("counterparty") or "").strip().lower()
            if counterparty:
                return counterparty
    return "generic"


@router.get("/payers/{payer_id}/behavior")
def payer_behavior(payer_id: str, db: Session = Depends(get_db)):
    claims = db.query(Claim).all()
    rows = [
        {
            "id": c.id,
            "payer": _claim_payer(c),
            "status": str(c.status),
            "settlement_days": 45,
            "settlement_percent": min(1.0, max(0.1, float(c.recovered_amount or 0.0) / max(float(c.recovered_amount or 1.0), 1.0))),
        }
        for c in claims
    ]
    return payer_behavior_profile(payer_id, rows)


@router.get("/payers/{payer_id}/risk")
def payer_risk(payer_id: str, db: Session = Depends(get_db)):
    claims = db.query(Claim).all()
    rows = [
        {
            "id": c.id,
            "payer": _claim_payer(c),
            "status": str(c.status),
            "settlement_days": 45,
            "settlement_percent": min(1.0, max(0.1, float(c.recovered_amount or 0.0) / max(float(c.recovered_amount or 1.0), 1.0))),
        }
        for c in claims
    ]
    behavior = payer_behavior_profile(payer_id, rows)
    return payer_risk_score(payer_id, behavior)
