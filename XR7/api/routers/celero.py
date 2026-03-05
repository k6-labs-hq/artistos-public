"""
Celero Commerce merchant-of-record API endpoints for XR7 Engine 2.

These endpoints provide the full integration surface for Celero Commerce
acting as the Merchant of Record (MoR) for XR7's payment operations.

Payment flow overview
---------------------
1.  **Register artist** — ``POST /artists/{id}/celero/register``
    Creates a Customer Vault record in Celero and stores the
    ``celero_customer_vault_id`` on the Artist.  The artist's payment
    details (card / bank) are added via Celero's hosted Collect.js form
    on the front-end — XR7 never touches raw payment data (PCI scope
    stays with Celero).

2.  **Charge contingency fee** — ``POST /artists/{id}/celero/charge``
    When a claim is reconciled (``PAID`` status), call this endpoint to
    charge the artist the 10% contingency fee through Celero.

3.  **Disburse net recovery** — ``POST /artists/{id}/celero/disburse``
    Pay the artist their net recovery share (recovered amount minus fee)
    via ACH credit through Celero.

4.  **Track transactions** — ``GET /artists/{id}/celero/transactions``
    Full Celero transaction history for an artist.

5.  **Webhook receiver** — ``POST /celero/webhook``
    Celero sends real-time status updates here.  Configure this URL in
    the Celero merchant dashboard under Settings → Webhooks.

Setup
-----
Set the following environment variables:

``CELERO_SECURITY_KEY``  — Merchant API key from Celero onboarding.
``CELERO_WEBHOOK_SECRET`` — Webhook signing secret from Celero dashboard.
``CELERO_API_URL``  (optional) — Override gateway URL (sandbox vs production).

Request a sandbox key at https://celerocommerce.com/developers/
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.billing.engine import BillingEngine
from XR7.celero.client import CeleroClient
from XR7.celero.webhook import CeleroWebhookHandler, validate_signature, parse_event
from XR7.models.artist import Artist, ArtistSchema
from XR7.models.base import get_db
from XR7.models.celero_transaction import (
    CeleroTransaction,
    CeleroTxnStatus,
    CeleroTxnType,
    CeleroTransactionSchema,
)
from XR7.models.claim import Claim, ClaimStatus

router = APIRouter(tags=["celero"])


# ---------------------------------------------------------------------------
# Request/response schemas
# ---------------------------------------------------------------------------

class CeleroRegisterRequest(BaseModel):
    """
    Information needed to create an artist as a Celero customer.

    Card / bank account details are collected separately via Celero's
    hosted Collect.js form and never pass through XR7 servers.
    """
    first_name: str
    last_name: str
    email: str
    company: str = ""
    address1: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "US"
    phone: str = ""


class CeleroChargeRequest(BaseModel):
    """Charge the artist's Celero vault for a specific claim's contingency fee."""
    claim_id: str
    ip_address: str = ""


class CeleroDisburseRequest(BaseModel):
    """
    Disburse a net recovery amount to the artist via ACH.

    ``amount`` is the net amount in USD after XR7's fee has been deducted.
    ``claim_id`` is optional — omit for manual / ad-hoc disbursements.
    """
    amount: float
    currency: str = "USD"
    claim_id: str | None = None
    description: str = ""


class CeleroRefundRequest(BaseModel):
    """Refund a previous charge, optionally for a partial amount."""
    amount: float | None = None   # None = full refund


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _require_vault_id(artist: Artist) -> str:
    if not artist.celero_customer_vault_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Artist {artist.id} is not registered with Celero Commerce.  "
                f"Call POST /artists/{artist.id}/celero/register first."
            ),
        )
    return artist.celero_customer_vault_id


# ---------------------------------------------------------------------------
# Artist Celero registration
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/celero/register",
    response_model=ArtistSchema,
)
def register_artist_with_celero(
    artist_id: str,
    body: CeleroRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register an artist in the Celero Commerce Customer Vault.

    Creates a new vault record with the artist's contact details.  The
    returned ``celero_customer_vault_id`` is stored on the Artist and used
    for all subsequent charges and disbursements.

    The artist's actual payment credentials (card number / bank account)
    are added separately using Celero's **Collect.js** or **Collect Checkout**
    hosted form — XR7 never handles raw payment data.

    Requires ``CELERO_SECURITY_KEY`` to be configured.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    if artist.celero_customer_vault_id:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Artist already registered with Celero "
                f"(vault_id={artist.celero_customer_vault_id}).  "
                "To update contact details call PUT /artists/{id}/celero/customer."
            ),
        )

    client = CeleroClient()
    try:
        response = client.add_customer(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            company=body.company,
            address1=body.address1,
            city=body.city,
            state=body.state,
            zip_code=body.zip_code,
            country=body.country,
            phone=body.phone,
            XR7_artist_id=artist_id,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    if not response.approved:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Celero rejected the customer registration.",
                "response_code": response.response_code,
                "response_text": response.response_text,
            },
        )

    artist.celero_customer_vault_id = response.customer_vault_id
    db.commit()
    db.refresh(artist)
    return artist


@router.get(
    "/artists/{artist_id}/celero/status",
)
def get_celero_status(artist_id: str, db: Session = Depends(get_db)):
    """
    Return the Celero Commerce integration status for an artist.

    Shows whether the artist has been registered in the Celero vault and
    a summary of their transaction history.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    client = CeleroClient()
    txn_count = (
        db.query(CeleroTransaction)
        .filter(CeleroTransaction.artist_id == artist_id)
        .count()
    )
    total_charged = (
        db.query(CeleroTransaction)
        .filter(
            CeleroTransaction.artist_id == artist_id,
            CeleroTransaction.type == CeleroTxnType.CHARGE,
            CeleroTransaction.status == CeleroTxnStatus.APPROVED,
        )
        .all()
    )
    total_disbursed = (
        db.query(CeleroTransaction)
        .filter(
            CeleroTransaction.artist_id == artist_id,
            CeleroTransaction.type == CeleroTxnType.DISBURSEMENT,
            CeleroTransaction.status.in_([CeleroTxnStatus.APPROVED, CeleroTxnStatus.SETTLED]),
        )
        .all()
    )
    return {
        "artist_id": artist_id,
        "celero_registered": bool(artist.celero_customer_vault_id),
        "celero_customer_vault_id": artist.celero_customer_vault_id,
        "celero_connector_configured": client.configured,
        "transaction_count": txn_count,
        "total_fees_charged": round(sum(t.amount for t in total_charged), 2),
        "total_disbursed": round(sum(t.amount for t in total_disbursed), 2),
    }


@router.put(
    "/artists/{artist_id}/celero/customer",
    response_model=ArtistSchema,
)
def update_celero_customer(
    artist_id: str,
    body: CeleroRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Update an artist's contact details in the Celero Customer Vault.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    vault_id = _require_vault_id(artist)
    client = CeleroClient()
    try:
        response = client.update_customer(
            vault_id,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            company=body.company,
            address1=body.address1,
            city=body.city,
            state=body.state,
            zip=body.zip_code,
            country=body.country,
            phone=body.phone,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    if not response.approved:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Celero rejected the customer update.",
                "response_code": response.response_code,
                "response_text": response.response_text,
            },
        )
    db.refresh(artist)
    return artist


# ---------------------------------------------------------------------------
# Charging contingency fees
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/celero/charge",
    response_model=CeleroTransactionSchema,
    status_code=201,
)
def charge_contingency_fee(
    artist_id: str,
    body: CeleroChargeRequest,
    db: Session = Depends(get_db),
):
    """
    Charge the artist's Celero-vaulted payment method for XR7's
    10% contingency fee on a reconciled claim.

    The claim must be in ``PAID`` status with a ``recovered_amount`` set.
    The charge amount is calculated as ``recovered_amount × 10%``.

    Requires:
    - The artist to be registered with Celero (``celero_customer_vault_id`` set).
    - ``CELERO_SECURITY_KEY`` to be configured.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    vault_id = _require_vault_id(artist)

    claim = db.query(Claim).filter(
        Claim.id == body.claim_id, Claim.artist_id == artist_id
    ).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if ClaimStatus(claim.status) != ClaimStatus.PAID:
        raise HTTPException(
            status_code=400,
            detail=f"Claim must be in PAID status to charge the fee (current: {claim.status}).",
        )
    if not claim.recovered_amount:
        raise HTTPException(
            status_code=400,
            detail="Claim has no recovered_amount set.  Call POST /claims/{id}/reconcile first.",
        )

    engine = BillingEngine(db)
    try:
        txn = engine.charge_via_celero(
            claim_id=body.claim_id,
            customer_vault_id=vault_id,
            ip_address=body.ip_address,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return txn


# ---------------------------------------------------------------------------
# Disbursing net recovery to artist
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/celero/disburse",
    response_model=CeleroTransactionSchema,
    status_code=201,
)
def disburse_to_artist(
    artist_id: str,
    body: CeleroDisburseRequest,
    db: Session = Depends(get_db),
):
    """
    Disburse the artist's net recovery amount via ACH credit through Celero.

    The ``amount`` should be the gross recovery minus XR7's contingency
    fee.  Celero will credit the artist's bank account stored in their vault.

    Requires:
    - The artist to have a bank account on file in their Celero vault.
    - Celero ACH payout capability to be enabled on the XR7 merchant account.
    - ``CELERO_SECURITY_KEY`` to be configured.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    vault_id = _require_vault_id(artist)

    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Disbursement amount must be greater than 0.")

    engine = BillingEngine(db)
    try:
        txn = engine.disburse_via_celero(
            artist_id=artist_id,
            claim_id=body.claim_id,
            amount=body.amount,
            currency=body.currency,
            customer_vault_id=vault_id,
            description=body.description,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return txn


# ---------------------------------------------------------------------------
# Refund and void
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/celero/transactions/{transaction_id}/refund",
    response_model=CeleroTransactionSchema,
    status_code=201,
)
def refund_transaction(
    artist_id: str,
    transaction_id: str,
    body: CeleroRefundRequest,
    db: Session = Depends(get_db),
):
    """
    Issue a partial or full refund for a previous CHARGE transaction.

    If ``amount`` is omitted, the full transaction amount is refunded.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    original = db.query(CeleroTransaction).filter(
        CeleroTransaction.id == transaction_id,
        CeleroTransaction.artist_id == artist_id,
    ).first()
    if not original:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not original.celero_transaction_id:
        raise HTTPException(
            status_code=400,
            detail="Transaction has no Celero transaction ID — cannot refund.",
        )

    refund_amount = body.amount or original.amount
    client = CeleroClient()
    try:
        response = client.refund(
            transaction_id=original.celero_transaction_id,
            amount=refund_amount if body.amount else None,
        )
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    # Create a new REFUND transaction record
    refund_txn = CeleroTransaction(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        claim_id=original.claim_id,
        type=CeleroTxnType.REFUND,
        amount=refund_amount,
        currency=original.currency,
        status=CeleroTxnStatus.APPROVED if response.approved else CeleroTxnStatus.DECLINED,
        celero_transaction_id=response.transaction_id or None,
        celero_customer_vault_id=original.celero_customer_vault_id,
        celero_auth_code=response.auth_code or None,
        celero_response_code=response.response_code or None,
        celero_response_text=response.response_text or None,
        order_id=original.order_id,
        description=f"Refund of transaction {transaction_id}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(refund_txn)

    if response.approved:
        original.status = CeleroTxnStatus.REFUNDED
    db.commit()
    db.refresh(refund_txn)
    return refund_txn


@router.post(
    "/artists/{artist_id}/celero/transactions/{transaction_id}/void",
    response_model=CeleroTransactionSchema,
    status_code=201,
)
def void_transaction(
    artist_id: str,
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """
    Void an unsettled CHARGE transaction (typically same-day).

    Use ``refund`` for transactions that have already settled.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    original = db.query(CeleroTransaction).filter(
        CeleroTransaction.id == transaction_id,
        CeleroTransaction.artist_id == artist_id,
    ).first()
    if not original:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not original.celero_transaction_id:
        raise HTTPException(
            status_code=400,
            detail="Transaction has no Celero transaction ID — cannot void.",
        )

    client = CeleroClient()
    try:
        response = client.void(transaction_id=original.celero_transaction_id)
    except NotImplementedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    void_txn = CeleroTransaction(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        claim_id=original.claim_id,
        type=CeleroTxnType.VOID,
        amount=original.amount,
        currency=original.currency,
        status=CeleroTxnStatus.VOIDED if response.approved else CeleroTxnStatus.ERROR,
        celero_transaction_id=response.transaction_id or None,
        celero_customer_vault_id=original.celero_customer_vault_id,
        celero_auth_code=response.auth_code or None,
        celero_response_code=response.response_code or None,
        celero_response_text=response.response_text or None,
        order_id=original.order_id,
        description=f"Void of transaction {transaction_id}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(void_txn)

    if response.approved:
        original.status = CeleroTxnStatus.VOIDED
    db.commit()
    db.refresh(void_txn)
    return void_txn


# ---------------------------------------------------------------------------
# Transaction history
# ---------------------------------------------------------------------------

@router.get(
    "/artists/{artist_id}/celero/transactions",
    response_model=List[CeleroTransactionSchema],
)
def list_celero_transactions(artist_id: str, db: Session = Depends(get_db)):
    """
    Return all Celero transactions for an artist, newest first.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    return (
        db.query(CeleroTransaction)
        .filter(CeleroTransaction.artist_id == artist_id)
        .order_by(CeleroTransaction.created_at.desc())
        .all()
    )


@router.get(
    "/artists/{artist_id}/celero/transactions/{transaction_id}",
    response_model=CeleroTransactionSchema,
)
def get_celero_transaction(
    artist_id: str,
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """
    Return a single Celero transaction record.
    """
    txn = db.query(CeleroTransaction).filter(
        CeleroTransaction.id == transaction_id,
        CeleroTransaction.artist_id == artist_id,
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


# ---------------------------------------------------------------------------
# Webhook receiver
# ---------------------------------------------------------------------------

@router.post("/celero/webhook", status_code=200)
async def celero_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_celero_signature: str = Header(default="", alias="X-Celero-Signature"),
):
    """
    Receive and process real-time event notifications from Celero Commerce.

    Configure this URL in the Celero merchant dashboard:
      Settings → Webhooks → Add Endpoint → ``https://your-domain/celero/webhook``

    Supported events: ``transaction.approved``, ``transaction.declined``,
    ``transaction.void``, ``transaction.refund``, ``disbursement.settled``,
    ``disbursement.failed``.

    Every request is validated against the HMAC-SHA256 signature in the
    ``X-Celero-Signature`` header using ``CELERO_WEBHOOK_SECRET``.
    """
    raw_body = await request.body()

    try:
        valid = validate_signature(raw_body, x_celero_signature)
    except ValueError as exc:
        # Production: missing CELERO_WEBHOOK_SECRET
        raise HTTPException(status_code=500, detail=str(exc))

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature.  Check CELERO_WEBHOOK_SECRET.",
        )

    try:
        event = parse_event(raw_body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    handler = CeleroWebhookHandler(db)
    result = handler.handle(event)

    return {"received": True, **result}
