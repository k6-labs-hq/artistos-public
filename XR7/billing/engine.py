import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.trolley_transaction import TrolleyTransaction, TrolleyTxnStatus, TrolleyTxnType
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.founder_program import get_or_create_platform_config, resolve_standard_fee_percent
from XR7.trolley.client import TrolleyClient, TrolleyException
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class BillingEngine:
    CONTINGENCY_RATE = 0.12

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

    def calculate_contingency_fee(
        self, recovered_amount: float, artist_id: str | None = None
    ) -> float:
        if artist_id:
            fee_pct = self._artist_fee_percent(artist_id)
        else:
            # Compatibility path used by legacy tests and callers without artist context.
            fee_pct = self.CONTINGENCY_RATE * 100.0
        return recovered_amount * (fee_pct / 100.0)

    def create_invoice(
        self, claim_id: str, recovered_amount: float, currency: str, artist_id: str | None = None
    ) -> dict:
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

        fee_pct = (
            float(claim.platform_fee_percent)
            if claim.platform_fee_percent is not None
            else self._artist_fee_percent(claim.artist_id)
        )
        platform_fee = round(gross_amount * fee_pct / 100.0, 2)
        artist_net = round(gross_amount - platform_fee, 2)

        # CRITICAL VALIDATION: Prevent fee overcharges and negative payouts
        if platform_fee >= gross_amount:
            raise ValueError(
                f"Platform fee (${platform_fee:.2f}) cannot be >= gross amount (${gross_amount:.2f}). "
                f"Fee percentage ({fee_pct}%) is too high for this remittance."
            )
        if artist_net <= 0:
            raise ValueError(
                f"Artist net amount (${artist_net:.2f}) must be positive. "
                f"Fee (${platform_fee:.2f}) exceeds or equals gross (${gross_amount:.2f})."
            )

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

        artist = get_artist_or_404(claim.artist_id, self.db_session)
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

            # Queue automatic retry with exponential backoff
            # Import here to avoid circular dependency
            from XR7.tasks.billing_tasks import retry_failed_disbursement

            retry_failed_disbursement.delay(claim.id)
            logger.info(
                f"Disbursement failed for claim {claim.id}, queued for automatic retry "
                f"(attempt {claim.payout_retry_count}/5)"
            )

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

    def process_refund(
        self,
        *,
        claim_id: str,
        refund_amount: float,
        reason: str,
        refund_type: str = "REFUND",
        trolley_refund_id: str | None = None,
        notes: str | None = None,
    ) -> TrolleyTransaction:
        """
        Process a refund or chargeback for a previously paid claim.

        Critical for production dispute handling. Creates:
        - Negative TrolleyTransaction (REFUND or CHARGEBACK type)
        - Immutable ledger audit trail entry
        - Claim status update if fully refunded

        Args:
            claim_id: ID of the claim being refunded
            refund_amount: Amount to refund (positive number, will be stored as negative)
            reason: Reason for refund (e.g., "Payer dispute", "Duplicate payment")
            refund_type: "REFUND" (voluntary) or "CHARGEBACK" (forced)
            trolley_refund_id: External Trolley transaction ID if applicable
            notes: Additional context for audit purposes

        Returns:
            TrolleyTransaction: The refund transaction record

        Raises:
            ValueError: If claim not found, amount invalid, or claim not in refundable status
        """
        claim = self.db_session.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        if refund_amount <= 0:
            raise ValueError("refund_amount must be greater than 0")

        if refund_type not in ["REFUND", "CHARGEBACK"]:
            raise ValueError(f"refund_type must be 'REFUND' or 'CHARGEBACK', got {refund_type}")

        # Verify claim is in a refundable state
        refundable_statuses = {
            ClaimStatus.FUNDS_RECEIVED,
            ClaimStatus.PAID,
            ClaimStatus.DISBURSEMENT_FAILED,
        }
        if claim.status not in refundable_statuses:
            raise ValueError(
                f"Claim {claim_id} is in status {claim.status}, "
                f"not eligible for refund (must be in {refundable_statuses})"
            )

        # Validate refund amount doesn't exceed recovered amount
        recovered = float(claim.recovered_amount or 0.0)
        if refund_amount > recovered:
            raise ValueError(f"Refund amount {refund_amount} exceeds recovered amount {recovered}")

        # Calculate adjusted amounts after refund
        remaining_recovered = recovered - refund_amount
        fee_pct = float(claim.platform_fee_percent or self._artist_fee_percent(claim.artist_id))
        adjusted_platform_fee = round(remaining_recovered * fee_pct / 100.0, 2)
        adjusted_artist_net = round(remaining_recovered - adjusted_platform_fee, 2)

        # Create refund transaction record (negative amount for accounting)
        tx_type = (
            TrolleyTxnType.CHARGEBACK if refund_type == "CHARGEBACK" else TrolleyTxnType.REFUND
        )
        tx = TrolleyTransaction(
            id=str(uuid.uuid4()),
            artist_id=claim.artist_id,
            claim_id=claim.id,
            type=tx_type,
            status=TrolleyTxnStatus.PAID,  # Refund is completed when recorded
            gross_amount=-refund_amount,  # Negative for refund
            platform_fee_amount=-round(refund_amount * fee_pct / 100.0, 2),
            net_amount=-round(refund_amount * (1 - fee_pct / 100.0), 2),
            source_currency=claim.currency or "USD",
            trolley_payment_id=trolley_refund_id,
            external_id=claim.id,
            description=f"{refund_type}: {reason}" + (f" - {notes}" if notes else ""),
            failure_reason=reason if refund_type == "CHARGEBACK" else None,
        )
        self.db_session.add(tx)

        # Update claim with adjusted amounts
        claim.recovered_amount = remaining_recovered
        claim.platform_fee_amount = adjusted_platform_fee
        claim.contingency_fee = adjusted_platform_fee
        claim.artist_net_amount = adjusted_artist_net
        claim.updated_at = datetime.now(timezone.utc)

        # If fully refunded, revert claim status
        if remaining_recovered == 0:
            # Reset to the status before payment was received
            if claim.status == ClaimStatus.PAID:
                claim.status = ClaimStatus.FUNDS_RECEIVED
            elif claim.status == ClaimStatus.FUNDS_RECEIVED:
                claim.status = ClaimStatus.SUBMITTED
            claim.trolley_payment_id = None
            claim.trolley_payment_status = None

        # Create immutable audit trail entry
        ledger = ImmutableLedgerService(self.db_session)
        ledger.append(
            claim.artist_id,
            f"{refund_type.lower()}_processed",
            {
                "claim_id": claim.id,
                "refund_amount": refund_amount,
                "refund_type": refund_type,
                "reason": reason,
                "trolley_refund_id": trolley_refund_id,
                "notes": notes,
                "remaining_recovered_amount": remaining_recovered,
                "adjusted_platform_fee": adjusted_platform_fee,
                "adjusted_artist_net": adjusted_artist_net,
                "claim_status_after_refund": claim.status.value,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        self.db_session.commit()
        self.db_session.refresh(tx)
        self.db_session.refresh(claim)
        return tx
