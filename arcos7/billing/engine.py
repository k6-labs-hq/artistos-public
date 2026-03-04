import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from arcos7.models.claim import Claim, ClaimStatus
from arcos7.models.celero_transaction import CeleroTransaction, CeleroTxnType, CeleroTxnStatus


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
            "created_at": datetime.now(timezone.utc).isoformat(),
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

    # ------------------------------------------------------------------
    # Celero Commerce integration
    # ------------------------------------------------------------------

    def charge_via_celero(
        self,
        claim_id: str,
        customer_vault_id: str,
        ip_address: str = "",
    ) -> CeleroTransaction:
        """
        Charge the artist's Celero-vaulted payment method for the
        contingency fee associated with a reconciled claim.

        Creates a :class:`~arcos7.models.celero_transaction.CeleroTransaction`
        record (initially PENDING) then calls the Celero gateway.  The record
        is updated to APPROVED / DECLINED / ERROR based on the response.

        The actual gateway call is only made when ``CELERO_SECURITY_KEY`` is
        set.  If it is not set, ``NotImplementedError`` is raised with setup
        instructions — the same behaviour as all other credential-gated
        connectors in this codebase.

        Parameters
        ----------
        claim_id:
            ARCOS7 claim UUID.  Must be in PAID status with a
            ``recovered_amount`` set.
        customer_vault_id:
            Celero Customer Vault ID stored on the artist record.
        ip_address:
            Optional IP address of the request for fraud screening.
        """
        from arcos7.celero.client import CeleroClient

        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        if not claim.recovered_amount:
            raise ValueError(f"Claim {claim_id} has no recovered_amount set")

        fee = self.calculate_contingency_fee(claim.recovered_amount)
        currency = (claim.currency or "USD").lower()

        # Create a PENDING transaction record before calling the gateway
        txn = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=claim.artist_id,
            claim_id=claim_id,
            type=CeleroTxnType.CHARGE,
            amount=fee,
            currency=currency.upper(),
            status=CeleroTxnStatus.PENDING,
            celero_customer_vault_id=customer_vault_id,
            order_id=claim_id,
            description=f"ARCOS7 recovery fee — claim {claim_id}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db_session.add(txn)
        self.db_session.commit()

        # Call Celero
        client = CeleroClient()
        response = client.charge(
            amount=fee,
            customer_vault_id=customer_vault_id,
            currency=currency,
            order_id=claim_id,
            order_description=f"ARCOS7 recovery fee — claim {claim_id}",
            ip_address=ip_address,
        )

        # Update transaction record with gateway response
        if response.approved:
            txn.status = CeleroTxnStatus.APPROVED
        elif response.declined:
            txn.status = CeleroTxnStatus.DECLINED
        else:
            txn.status = CeleroTxnStatus.ERROR

        txn.celero_transaction_id = response.transaction_id or None
        txn.celero_auth_code = response.auth_code or None
        txn.celero_response_code = response.response_code or None
        txn.celero_response_text = response.response_text or None
        txn.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(txn)

        # Also update the claim's contingency_fee field
        claim.contingency_fee = fee
        self.db_session.commit()

        return txn

    def disburse_via_celero(
        self,
        artist_id: str,
        claim_id: str | None,
        amount: float,
        currency: str,
        customer_vault_id: str,
        description: str = "",
    ) -> CeleroTransaction:
        """
        Disburse the net recovery amount to the artist via ACH credit
        through Celero Commerce.

        Creates a :class:`~arcos7.models.celero_transaction.CeleroTransaction`
        (type=DISBURSEMENT) and calls ``CeleroClient.disburse()``.

        Parameters
        ----------
        artist_id:
            ARCOS7 artist UUID.
        claim_id:
            Associated claim UUID, or ``None`` for ad-hoc disbursements.
        amount:
            Net amount to disburse to the artist in USD.
        currency:
            ISO 4217 currency code.
        customer_vault_id:
            Artist's Celero vault ID (must have a bank account on file).
        description:
            Optional description shown on the artist's bank statement.
        """
        from arcos7.celero.client import CeleroClient

        txn = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            claim_id=claim_id,
            type=CeleroTxnType.DISBURSEMENT,
            amount=amount,
            currency=currency.upper(),
            status=CeleroTxnStatus.PENDING,
            celero_customer_vault_id=customer_vault_id,
            order_id=claim_id or artist_id,
            description=description or f"ARCOS7 royalty disbursement to {artist_id}",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db_session.add(txn)
        self.db_session.commit()

        client = CeleroClient()
        response = client.disburse(
            amount=amount,
            customer_vault_id=customer_vault_id,
            currency=currency.lower(),
            order_id=claim_id or artist_id,
            order_description=description or "ARCOS7 royalty disbursement",
        )

        if response.approved:
            txn.status = CeleroTxnStatus.APPROVED
        elif response.declined:
            txn.status = CeleroTxnStatus.DECLINED
        else:
            txn.status = CeleroTxnStatus.ERROR

        txn.celero_transaction_id = response.transaction_id or None
        txn.celero_auth_code = response.auth_code or None
        txn.celero_response_code = response.response_code or None
        txn.celero_response_text = response.response_text or None
        txn.updated_at = datetime.now(timezone.utc)
        self.db_session.commit()
        self.db_session.refresh(txn)
        return txn
