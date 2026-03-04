import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from arcos7.models.claim import Claim, ClaimStatus


class BillingEngine:
    CONTINGENCY_RATE = 0.10

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._invoices: dict[str, dict] = {}

    def calculate_contingency_fee(self, recovered_amount: float) -> float:
        return recovered_amount * self.CONTINGENCY_RATE

    def create_invoice(self, claim_id: str, recovered_amount: float, currency: str) -> dict:
        invoice_id = str(uuid.uuid4())
        contingency_fee = self.calculate_contingency_fee(recovered_amount)
        invoice = {
            "invoice_id": invoice_id,
            "claim_id": claim_id,
            "recovered_amount": recovered_amount,
            "contingency_fee": contingency_fee,
            "currency": currency,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat(),
        }
        self._invoices[invoice_id] = invoice
        return invoice

    def get_artist_billing_summary(self, artist_id: str) -> dict:
        paid_claims = (
            self.db_session.query(Claim)
            .filter(Claim.artist_id == artist_id, Claim.status == ClaimStatus.PAID)
            .all()
        )
        total_recovered = sum(c.recovered_amount or 0.0 for c in paid_claims)
        total_fees = sum(c.contingency_fee or 0.0 for c in paid_claims)
        net_to_artist = total_recovered - total_fees
        return {
            "artist_id": artist_id,
            "total_recovered": total_recovered,
            "total_fees": total_fees,
            "net_to_artist": net_to_artist,
            "claim_count": len(paid_claims),
        }

    def process_payment(self, invoice_id: str) -> dict:
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        invoice["status"] = "PAID"
        return invoice
