import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from arcos7.models.anomaly import Anomaly
from arcos7.models.claim import Claim, ClaimStatus
from arcos7.models.contract import Contract
from arcos7.models.event import Event
from arcos7.billing.engine import BillingEngine
from arcos7.models.payment import Payment


class ClaimsOrchestrator:
    CLAIM_TRANSITIONS = {
        ClaimStatus.IDENTIFIED: ClaimStatus.PREPARED,
        ClaimStatus.PREPARED: ClaimStatus.SUBMITTED,
        ClaimStatus.SUBMITTED: ClaimStatus.IN_REVIEW,
        ClaimStatus.IN_REVIEW: ClaimStatus.ACCEPTED,
        ClaimStatus.ACCEPTED: ClaimStatus.PAID,
        ClaimStatus.PAID: ClaimStatus.CLOSED,
    }

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_claim(self, anomaly_id: str, claim_type: str, evidence: dict | None = None) -> Claim:
        anomaly = self.db_session.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise ValueError(f"Anomaly {anomaly_id} not found")
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=anomaly.artist_id,
            anomaly_id=anomaly_id,
            claim_type=claim_type,
            status=ClaimStatus.IDENTIFIED,
            evidence=evidence or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db_session.add(claim)
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim

    def advance_claim(self, claim_id: str) -> Claim:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        current_status = ClaimStatus(claim.status)
        next_status = self.CLAIM_TRANSITIONS.get(current_status)
        if next_status is None:
            raise ValueError(f"No transition available from status {claim.status}")
        claim.status = next_status
        claim.updated_at = datetime.utcnow()
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim

    def generate_evidence_packet(self, claim_id: str) -> dict:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        anomaly = self.db_session.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        artist_id = claim.artist_id
        events = self.db_session.query(Event).filter(Event.artist_id == artist_id).all()
        contracts = self.db_session.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = self.db_session.query(Payment).filter(Payment.artist_id == artist_id).all()
        return {
            "claim_id": claim_id,
            "anomaly": {
                "id": anomaly.id if anomaly else None,
                "category": anomaly.category if anomaly else None,
                "subtype": anomaly.subtype if anomaly else None,
                "description": anomaly.description if anomaly else None,
            },
            "events": [{"id": e.id, "event_type": e.event_type, "timestamp": str(e.timestamp)} for e in events],
            "contracts": [{"id": c.id, "contract_type": c.contract_type} for c in contracts],
            "payments": [{"id": p.id, "amount": p.amount, "currency": p.currency} for p in payments],
            "summary": {
                "event_count": len(events),
                "contract_count": len(contracts),
                "payment_count": len(payments),
            },
        }

    def get_claim_status(self, claim_id: str) -> str:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        return str(claim.status)

    def reconcile_recovered_amount(self, claim_id: str, recovered_amount: float, currency: str) -> Claim:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        claim.recovered_amount = recovered_amount
        claim.currency = currency
        claim.contingency_fee = round(recovered_amount * BillingEngine.CONTINGENCY_RATE, 2)
        claim.updated_at = datetime.utcnow()
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim
