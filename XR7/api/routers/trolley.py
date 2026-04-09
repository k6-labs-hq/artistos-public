from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.auth.event_notifications import send_event_notification
from XR7.billing.engine import BillingEngine
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.notification_preference import NotificationPreference
from XR7.models.trolley_transaction import (
    TrolleyTransaction,
    TrolleyTransactionSchema,
    TrolleyTxnStatus,
    TrolleyTxnType,
)
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.branding import inject_branding_metadata
from XR7.tasks.hubspot import hubspot_sync_recovery_update
from XR7.trolley.client import TrolleyClient, TrolleyException, verify_trolley_signature
from xr7_common.logging import get_logger

router = APIRouter(tags=["trolley"])
logger = get_logger(__name__)


class ManualRemittanceRequest(BaseModel):
    gross_amount: float
    remittance_method: str
    received_date: datetime
    reference_number: str


class DisburseClaimRequest(BaseModel):
    claim_id: str


def _split_name(name: str) -> tuple[str, str]:
    parts = [p for p in (name or "").strip().split(" ") if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


@router.post("/artists/{artist_id}/trolley/recipient")
def create_trolley_recipient(artist_id: str, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)
    if artist.trolley_recipient_id:
        return inject_branding_metadata(db, {
            "artist_id": artist_id,
            "trolley_recipient_id": artist.trolley_recipient_id,
            "status": artist.payout_account_status,
        })

    first_name = artist.first_name
    last_name = artist.last_name
    if not first_name and not last_name:
        first_name, last_name = _split_name(artist.name)

    payload = {
        "type": "individual",
        "email": artist.email,
        "name": artist.name,
        "firstName": first_name,
        "lastName": last_name,
        "country": (artist.country_code or "US").upper(),
        "referenceId": artist.id,
    }
    try:
        client = TrolleyClient.from_env()
        response = client.create_recipient(payload)
    except TrolleyException as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    recipient = response.get("recipient") if isinstance(response, dict) else {}
    recipient_id = recipient.get("id") or response.get("id")
    if not recipient_id:
        raise HTTPException(status_code=502, detail="Trolley recipient creation did not return an ID")

    artist.trolley_recipient_id = recipient_id
    artist.payout_account_status = "pending"
    db.commit()
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "trolley_recipient_id": recipient_id,
        "status": artist.payout_account_status,
    })


@router.get("/artists/{artist_id}/trolley/widget-url")
def get_trolley_widget_url(artist_id: str, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)
    if not artist.trolley_recipient_id:
        raise HTTPException(status_code=400, detail="Artist has no Trolley recipient")

    try:
        response = TrolleyClient.from_env().get_recipient_widget_url(artist.trolley_recipient_id)
    except TrolleyException as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "trolley_recipient_id": artist.trolley_recipient_id,
        "url": response.get("url"),
    })


@router.get("/artists/{artist_id}/trolley/status")
def get_trolley_status(artist_id: str, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)

    if not artist.trolley_recipient_id:
        return inject_branding_metadata(db, {
            "artist_id": artist.id,
            "status": "not_started",
            "recipient_id": None,
            "payout_method": None,
            "tax_form_status": artist.tax_form_status,
        })

    try:
        response = TrolleyClient.from_env().get_recipient(artist.trolley_recipient_id)
    except TrolleyException as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    recipient = response.get("recipient") if isinstance(response, dict) else response
    payout_method = recipient.get("payoutMethod") if isinstance(recipient, dict) else None
    compliance = (recipient or {}).get("compliance") if isinstance(recipient, dict) else None
    verified = bool(payout_method) and (compliance or {}).get("status") == "verified"

    artist.payout_account_status = "verified" if verified else "pending"
    if isinstance(payout_method, dict):
        artist.payout_method_type = payout_method.get("type")
        artist.payout_last4 = payout_method.get("last4")
    artist.tax_form_status = "verified" if (compliance or {}).get("status") == "verified" else "pending"
    db.commit()

    return inject_branding_metadata(db, {
        "artist_id": artist.id,
        "status": artist.payout_account_status,
        "recipient_id": artist.trolley_recipient_id,
        "payout_method": {
            "type": artist.payout_method_type,
            "last4": artist.payout_last4,
            "country": artist.country_code,
        },
        "tax_form_status": artist.tax_form_status,
    })


@router.post("/artists/{artist_id}/claims/{claim_id}/manual-remittance")
def manual_remittance(artist_id: str, claim_id: str, body: ManualRemittanceRequest, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.artist_id == artist_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    updated = BillingEngine(db).record_manual_remittance(
        claim_id=claim_id,
        gross_amount=body.gross_amount,
        remittance_method=body.remittance_method,
        received_date=body.received_date,
        reference_number=body.reference_number,
    )

    return {
        "claim_id": updated.id,
        "status": updated.status,
        "gross_amount": updated.recovered_amount,
        "fee_percent": updated.platform_fee_percent,
        "platform_fee_amount": updated.platform_fee_amount,
        "artist_net_amount": updated.artist_net_amount,
        "fee_copy": (
            f"XR7 retains {float(updated.platform_fee_percent or 0.0):.2f}% "
            f"(${float(updated.platform_fee_amount or 0.0):,.2f}) You receive "
            f"${float(updated.artist_net_amount or 0.0):,.2f}"
        ),
    }


@router.post("/claims/{claim_id}/disburse", response_model=TrolleyTransactionSchema)
def disburse_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    try:
        return BillingEngine(db).disburse_via_trolley(claim_id=claim_id)
    except (ValueError, TrolleyException) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/webhooks/trolley")
async def trolley_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("x-trolley-signature")
    secret = os.environ.get("TROLLEY_SECRET_KEY", "")
    if not verify_trolley_signature(body, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid Trolley signature")

    payload = await request.json()
    event_type = str(payload.get("type") or "")
    payment = payload.get("payment") or {}
    claim_id = payment.get("externalId")

    if claim_id:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            if event_type == "payment.paid":
                claim.status = ClaimStatus.PAID
                claim.trolley_payment_status = "PAID"
                claim.trolley_payment_id = payment.get("id") or claim.trolley_payment_id
                claim.trolley_fx_rate = payment.get("exchangeRate")
                claim.trolley_local_amount = payment.get("targetAmount")
                claim.trolley_local_currency = payment.get("targetCurrency")
                claim.updated_at = datetime.now(timezone.utc)
                ImmutableLedgerService(db).append(
                    claim.artist_id,
                    "trolley_disbursement_paid",
                    {
                        "claim_id": claim.id,
                        "trolley_payment_id": claim.trolley_payment_id,
                        "exchange_rate": claim.trolley_fx_rate,
                        "local_amount": claim.trolley_local_amount,
                        "local_currency": claim.trolley_local_currency,
                    },
                )
                try:
                    hubspot_sync_recovery_update.delay(claim.artist_id, event="recovery_disbursement_paid")
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to enqueue HubSpot disbursement paid sync", extra={"claim_id": claim.id})

                pref = db.query(NotificationPreference).filter(NotificationPreference.artist_id == claim.artist_id).first()
                method = payment.get("method") or "payout"
                eta = payment.get("estimatedDelivery") or "pending"
                send_event_notification(
                    pref,
                    "claim_paid",
                    "XR7 disbursement sent",
                    f"${float(claim.artist_net_amount or 0.0):,.2f} has been sent to your {method} account. Estimated arrival: {eta}.",
                    current_hour_utc=datetime.now(timezone.utc).hour,
                    db=db,
                )
            elif event_type == "payment.failed":
                claim.status = ClaimStatus.DISBURSEMENT_FAILED
                claim.trolley_payment_status = "FAILED"
                claim.payout_failure_reason = payment.get("failureReason") or "payment.failed"
                claim.payout_retry_count = int(claim.payout_retry_count or 0) + 1
                claim.updated_at = datetime.now(timezone.utc)
            elif event_type == "payment.returned":
                claim.status = ClaimStatus.DISBURSEMENT_FAILED
                claim.trolley_payment_status = "RETURNED"
                claim.payout_failure_reason = payment.get("failureReason") or "payment.returned"
                claim.payout_retry_count = int(claim.payout_retry_count or 0) + 1
                claim.updated_at = datetime.now(timezone.utc)
                ImmutableLedgerService(db).append(
                    claim.artist_id,
                    "trolley_disbursement_returned",
                    {
                        "claim_id": claim.id,
                        "retry_count": claim.payout_retry_count,
                        "failure_reason": claim.payout_failure_reason,
                    },
                )

                if claim.payout_retry_count <= 3:
                    claim.updated_at = datetime.now(timezone.utc) + timedelta(hours=24)
            db.commit()

    if event_type == "recipient.updated":
        recipient = payload.get("recipient") or {}
        artist_id = recipient.get("referenceId")
        if artist_id:
            artist = db.query(Artist).filter(Artist.id == artist_id).first()
            if artist:
                payout_method = recipient.get("payoutMethod") or {}
                compliance = recipient.get("compliance") or {}
                verified = bool(payout_method) and compliance.get("status") == "verified"
                artist.payout_account_status = "verified" if verified else "pending"
                artist.payout_method_type = payout_method.get("type")
                artist.payout_last4 = payout_method.get("last4")
                artist.tax_form_status = "verified" if compliance.get("status") == "verified" else "pending"
                db.commit()

    if claim_id:
        txn = db.query(TrolleyTransaction).filter(TrolleyTransaction.claim_id == claim_id, TrolleyTransaction.type == TrolleyTxnType.DISBURSEMENT).first()
        if txn:
            if event_type == "payment.paid":
                txn.status = TrolleyTxnStatus.PAID
            elif event_type == "payment.failed":
                txn.status = TrolleyTxnStatus.FAILED
                txn.failure_reason = payment.get("failureReason")
                txn.retry_count = int(txn.retry_count or 0) + 1
            elif event_type == "payment.returned":
                txn.status = TrolleyTxnStatus.RETURNED
                txn.failure_reason = payment.get("failureReason")
                txn.retry_count = int(txn.retry_count or 0) + 1
            txn.exchange_rate = payment.get("exchangeRate") or txn.exchange_rate
            txn.local_amount = payment.get("targetAmount") or txn.local_amount
            txn.local_currency = payment.get("targetCurrency") or txn.local_currency
            db.commit()

    return {"received": True}
