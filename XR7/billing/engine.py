import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.trolley_transaction import TrolleyTransaction, TrolleyTxnStatus, TrolleyTxnType
from XR7.models.metadata_issue import MetadataIssue
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.founder_program import get_or_create_platform_config, resolve_standard_fee_percent
from XR7.trolley.client import TrolleyClient, TrolleyException


class BillingEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self._invoices: dict[str, dict] = {}

    def _artist_fee_percent(self, artist_id: str) -> float:
        artist = self.db_session.query(Artist).filter(Artist.id == artist_id).first()
        if artist and artist.contingency_fee_percent is not None:
            return float(artist.contingency_fee_percent)

        cfg = get_or_create_platform_config(self.db_session)
        fallback = resolve_standard_fee_percent(cfg)
        if artist:
            artist.contingency_fee_percent = fallback
            self.db_session.flush()
        return fallback

    def calculate_contingency_fee(self, recovered_amount: float, artist_id: str) -> float:
        fee_pct = self._artist_fee_percent(artist_id)
        return recovered_amount * (fee_pct / 100.0)

    def create_invoice(self, claim_id: str, recovered_amount: float, currency: str, artist_id: str) -> dict:
        invoice_id = str(uuid.uuid4())
        contingency_fee = self.calculate_contingency_fee(recovered_amount, artist_id)
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
        leakage_prevented = (
            self.db_session.query(MetadataIssue)
            .filter(
                MetadataIssue.artist_id == artist_id,
                MetadataIssue.repair_status == "AUTO_REPAIRED",
            )
            .all()
        )
        xr7_future_leakage_prevented = round(
            sum(float(i.projected_leakage_avoided or 0.0) for i in leakage_prevented),
            2,
        )
        return {
            "artist_id": artist_id,
            "total_recovered": total_recovered,
            "total_fees": total_fees,
            "net_to_artist": net_to_artist,
            "claim_count": len(paid_claims),
            "xr7_future_leakage_prevented": xr7_future_leakage_prevented,
            "xr7_future_leakage_prevented_billable": False,
            "billing_policy": {
                "repairs_are_free": True,
                "charges_apply_only_to_recovered_money": True,
            },
        }

    def process_payment(self, invoice_id: str) -> dict:
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        invoice["status"] = "PAID"
        return invoice

    def record_manual_remittance(
        self,
        *,
        claim_id: str,
        gross_amount: float,
        remittance_method: str,
        received_date: datetime,
        reference_number: str,
    ) -> Claim:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        if gross_amount <= 0:
            raise ValueError("gross_amount must be greater than 0")

        fee_pct = self._artist_fee_percent(claim.artist_id)
        platform_fee = round(gross_amount * fee_pct / 100.0, 2)
        artist_net = round(gross_amount - platform_fee, 2)

        claim.status = ClaimStatus.FUNDS_RECEIVED
        claim.recovered_amount = gross_amount
        claim.platform_fee_percent = fee_pct
        claim.platform_fee_amount = platform_fee
        claim.contingency_fee = platform_fee
        claim.artist_net_amount = artist_net
        claim.remittance_method = remittance_method
        claim.remittance_reference_number = reference_number
        claim.remittance_received_at = received_date
        claim.updated_at = datetime.now(timezone.utc)

        self.db_session.add(
            TrolleyTransaction(
                id=str(uuid.uuid4()),
                artist_id=claim.artist_id,
                claim_id=claim.id,
                type=TrolleyTxnType.REMITTANCE,
                status=TrolleyTxnStatus.PAID,
                gross_amount=gross_amount,
                platform_fee_amount=platform_fee,
                net_amount=artist_net,
                source_currency=claim.currency or "USD",
                external_id=claim.id,
                description=f"Manual remittance recorded ({remittance_method})",
            )
        )

        ledger = ImmutableLedgerService(self.db_session)
        ledger.append(
            claim.artist_id,
            "manual_remittance_received",
            {
                "claim_id": claim.id,
                "gross_amount": gross_amount,
                "platform_fee_amount": platform_fee,
                "artist_net_amount": artist_net,
                "remittance_method": remittance_method,
                "received_date": received_date.isoformat(),
                "reference_number": reference_number,
            },
        )
        self.db_session.commit()
        self.db_session.refresh(claim)
        return claim

    def disburse_via_trolley(self, *, claim_id: str) -> TrolleyTransaction:
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        if claim.status != ClaimStatus.FUNDS_RECEIVED:
            raise ValueError("Claim must be in FUNDS_RECEIVED status before disbursement")

        from XR7.models.artist import Artist

        artist = self.db_session.query(Artist).filter(Artist.id == claim.artist_id).first()
        if not artist:
            raise ValueError("Artist not found")
        if not artist.trolley_recipient_id:
            raise ValueError("Artist is not connected to Trolley payouts")
        if artist.payout_account_status != "verified":
            raise ValueError("Artist payout account is not verified")
        if str(artist.tax_form_status or "pending") != "verified":
            raise ValueError("Tax forms required before disbursement")

        client = TrolleyClient.from_env()
        existing = client.get_payments_by_external_id(claim.id)
        existing_rows = existing.get("payments") if isinstance(existing, dict) else None
        if isinstance(existing_rows, list) and existing_rows:
            raise ValueError(f"A payout already exists for claim {claim.id}")

        amount = float(claim.artist_net_amount or 0.0)
        if amount <= 0:
            raise ValueError("Claim has no artist net amount available for payout")

        payload = {
            "recipient": {"id": artist.trolley_recipient_id},
            "sourceAmount": f"{amount:.2f}",
            "sourceCurrency": "USD",
            "memo": f"XR7 Recovery - Claim {claim.id}",
            "externalId": claim.id,
            "taxReportable": True,
            "forceUsTaxActivity": str(artist.country_code or "US").upper() == "US",
        }

        try:
            response = client.create_payment(payload)
        except TrolleyException as exc:
            claim.status = ClaimStatus.DISBURSEMENT_FAILED
            claim.payout_failure_reason = str(exc)
            claim.payout_retry_count = int(claim.payout_retry_count or 0) + 1
            self.db_session.commit()
            raise

        payment = response.get("payment") if isinstance(response, dict) else {}
        payment_id = payment.get("id") if isinstance(payment, dict) else None
        status = str(payment.get("status") or "processing").upper()

        tx = TrolleyTransaction(
            id=str(uuid.uuid4()),
            artist_id=claim.artist_id,
            claim_id=claim.id,
            type=TrolleyTxnType.DISBURSEMENT,
            status=TrolleyTxnStatus.PROCESSING,
            gross_amount=claim.recovered_amount,
            platform_fee_amount=claim.platform_fee_amount,
            net_amount=amount,
            source_currency="USD",
            trolley_payment_id=payment_id,
            external_id=claim.id,
            description=f"Trolley disbursement for claim {claim.id}",
        )
        self.db_session.add(tx)

        claim.trolley_payment_id = payment_id
        claim.trolley_payment_status = status
        claim.updated_at = datetime.now(timezone.utc)

        ledger = ImmutableLedgerService(self.db_session)
        ledger.append(
            claim.artist_id,
            "trolley_disbursement_queued",
            {
                "claim_id": claim.id,
                "trolley_payment_id": payment_id,
                "net_amount": amount,
                "currency": "USD",
            },
        )

        self.db_session.commit()
        self.db_session.refresh(tx)
        return tx
