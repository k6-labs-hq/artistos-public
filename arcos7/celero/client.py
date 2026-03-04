"""
Celero Commerce — Celero Connect® API Client for ARCOS7 Engine 2.

Celero Commerce acts as the **Merchant of Record** for ARCOS7, meaning:

- Celero legally processes every contingency-fee payment on behalf of ARCOS7.
- Celero handles tax compliance (sales tax, VAT) for all transactions.
- Celero issues receipts and manages chargebacks / refunds with the card networks.
- ARCOS7 receives net funds after Celero's processing fees.
- Artists are registered as *customers* in Celero's Customer Vault; their payment
  tokens are stored there so ARCOS7 never holds raw card data (PCI scope eliminated).

Payment flows
-------------
1. **Contingency fee collection** (ARCOS7 charges the artist 10% of recovered amount):

   artist.celero_customer_vault_id → CeleroClient.charge()
   → CeleroTransaction (type=CHARGE, status=PENDING)
   → Celero approves / declines
   → Webhook ``transaction.approved`` / ``transaction.declined``
   → CeleroTransaction.status updated
   → Claim.status → CLOSED

2. **Disbursement to artist** (ARCOS7 pays artist their 90% share):

   CeleroClient.disburse()
   → CeleroTransaction (type=DISBURSEMENT, status=PENDING)
   → Celero ACH payout to artist's bank account
   → Webhook ``disbursement.settled``
   → CeleroTransaction.status → SETTLED

Celero Connect® API format
--------------------------
Celero Connect is built on the NMI (Network Merchants Inc.) gateway platform.
Requests are HTTP POST with ``application/x-www-form-urlencoded`` body.
Responses are ``key=value`` pairs separated by ``&``.

Required environment variables
-------------------------------
``CELERO_SECURITY_KEY``
    Merchant security key issued by Celero during onboarding.
    Request a sandbox key at https://celerocommerce.com/developers/

``CELERO_API_URL``  (optional, defaults to sandbox endpoint)
    Gateway URL.  Celero's live URL is provided during production onboarding.
    Sandbox: ``https://secure.networkmerchants.com/api/transact.php``

``CELERO_WEBHOOK_SECRET``
    HMAC-SHA256 secret used to verify webhook payloads.
    Configured in the Celero merchant dashboard under Webhooks.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SANDBOX_URL = "https://secure.networkmerchants.com/api/transact.php"
_QUERY_URL = "https://secure.networkmerchants.com/api/query.php"

# Permitted gateway domains — only Celero / NMI endpoints are allowed.
# This prevents SSRF if CELERO_API_URL is misconfigured or injected.
_ALLOWED_GATEWAY_HOSTS: frozenset[str] = frozenset({
    "secure.networkmerchants.com",
    "secure.celerocommerce.com",
    "secure.celarocommerce.com",
})

# Celero response codes
RESPONSE_APPROVED = "1"
RESPONSE_DECLINED = "2"
RESPONSE_ERROR = "3"

RESPONSE_CODE_DESCRIPTIONS: dict[str, str] = {
    "100": "Transaction was approved.",
    "200": "Transaction was declined by processor.",
    "201": "Do not honor.",
    "202": "Insufficient funds.",
    "203": "Over limit.",
    "204": "Pick up card.",
    "220": "Incorrect payment information.",
    "221": "No such card issuer.",
    "222": "No card number on file with issuer.",
    "223": "Expired card.",
    "224": "Invalid expiration date.",
    "225": "Invalid card security code.",
    "226": "Invalid PIN.",
    "240": "Call issuer for further information.",
    "250": "Pick up card.",
    "251": "Lost card.",
    "252": "Stolen card.",
    "253": "Fraudulent card.",
    "260": "Declined with further instructions available.",
    "261": "Declined — stop all recurring payments.",
    "262": "Declined — stop this recurring program.",
    "263": "Declined — update cardholder data available.",
    "264": "Declined — retry in a few days.",
    "300": "Transaction was rejected by gateway.",
    "400": "Transaction error returned by processor.",
    "410": "Invalid merchant configuration.",
    "411": "Merchant not activated.",
    "420": "Communication error.",
    "421": "Communication error with issuer.",
    "430": "Duplicate transaction at processor.",
    "440": "Processor format error.",
    "441": "Invalid transaction information.",
    "460": "Processor feature not available.",
    "461": "Unsupported card type.",
}


# ---------------------------------------------------------------------------
# Response dataclass
# ---------------------------------------------------------------------------

@dataclass
class CeleroResponse:
    """Parsed response from the Celero Connect gateway."""

    raw: str
    response: str                    # "1" approved, "2" declined, "3" error
    response_text: str
    auth_code: str = ""
    transaction_id: str = ""
    avs_response: str = ""
    cvv_response: str = ""
    order_id: str = ""
    type: str = ""
    response_code: str = ""
    customer_vault_id: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def approved(self) -> bool:
        return self.response == RESPONSE_APPROVED

    @property
    def declined(self) -> bool:
        return self.response == RESPONSE_DECLINED

    @property
    def response_code_description(self) -> str:
        return RESPONSE_CODE_DESCRIPTIONS.get(self.response_code, self.response_text)

    def to_dict(self) -> dict:
        return {
            "approved": self.approved,
            "transaction_id": self.transaction_id,
            "auth_code": self.auth_code,
            "response": self.response,
            "response_code": self.response_code,
            "response_text": self.response_text,
            "response_code_description": self.response_code_description,
            "customer_vault_id": self.customer_vault_id,
            "order_id": self.order_id,
            "avs_response": self.avs_response,
            "cvv_response": self.cvv_response,
            "type": self.type,
        }


def _parse_response(raw: str) -> CeleroResponse:
    """Parse a ``key=value&key=value`` response string from the gateway."""
    params: dict[str, str] = {}
    for part in raw.split("&"):
        if "=" in part:
            k, _, v = part.partition("=")
            params[k.strip()] = urllib.parse.unquote_plus(v.strip())

    return CeleroResponse(
        raw=raw,
        response=params.get("response", "3"),
        response_text=params.get("responsetext", "Unknown error"),
        auth_code=params.get("authcode", ""),
        transaction_id=params.get("transactionid", ""),
        avs_response=params.get("avsresponse", ""),
        cvv_response=params.get("cvvresponse", ""),
        order_id=params.get("orderid", ""),
        type=params.get("type", ""),
        response_code=params.get("response_code", ""),
        customer_vault_id=params.get("customer_vault_id", ""),
        extra={k: v for k, v in params.items() if k not in {
            "response", "responsetext", "authcode", "transactionid",
            "avsresponse", "cvvresponse", "orderid", "type",
            "response_code", "customer_vault_id",
        }},
    )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class CeleroClient:
    """
    HTTP client for the Celero Connect® payment gateway.

    Instantiate once per request (or share a single instance — all state is
    stateless / env-based).

    Parameters
    ----------
    security_key:
        Overrides ``CELERO_SECURITY_KEY`` env var.  Leave ``None`` to read
        from the environment.
    api_url:
        Overrides ``CELERO_API_URL`` env var.  Defaults to the NMI sandbox.
    """

    def __init__(
        self,
        security_key: str | None = None,
        api_url: str | None = None,
    ) -> None:
        self._security_key = security_key or os.environ.get("CELERO_SECURITY_KEY", "")
        self._api_url = api_url or os.environ.get("CELERO_API_URL", _SANDBOX_URL)
        self._query_url = os.environ.get("CELERO_QUERY_URL", _QUERY_URL)

    # ------------------------------------------------------------------
    # Credential check
    # ------------------------------------------------------------------

    @property
    def configured(self) -> bool:
        """Return ``True`` if the required API credentials are present."""
        return bool(self._security_key)

    def _require_configured(self, operation: str) -> None:
        if not self.configured:
            raise NotImplementedError(
                f"Celero Commerce is not yet configured ({operation}).  "
                "Set the 'CELERO_SECURITY_KEY' environment variable using the key "
                "issued during Celero onboarding.  "
                "Request a sandbox key at https://celerocommerce.com/developers/  "
                "For the full integration guide see the CELERO_SETUP.md in this repo."
            )

    # ------------------------------------------------------------------
    # HTTP transport
    # ------------------------------------------------------------------

    def _post(self, url: str, params: dict[str, str]) -> CeleroResponse:
        """POST key=value pairs to the gateway and return a parsed response."""
        # Validate URL against the allowlist to prevent SSRF attacks.
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_GATEWAY_HOSTS:
            logger.error(
                "Celero gateway URL '%s' is not in the permitted host allowlist %s",
                url,
                _ALLOWED_GATEWAY_HOSTS,
            )
            return CeleroResponse(
                raw="",
                response=RESPONSE_ERROR,
                response_text=(
                    f"Gateway URL '{url}' is not permitted.  "
                    "CELERO_API_URL must point to a Celero / NMI domain."
                ),
                response_code="441",
            )
        params["security_key"] = self._security_key
        body = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
                raw = resp.read().decode("utf-8")
        except Exception as exc:
            logger.error("Celero gateway communication error: %s", exc)
            return CeleroResponse(
                raw="",
                response=RESPONSE_ERROR,
                response_text=f"Gateway communication error: {exc}",
                response_code="420",
            )
        return _parse_response(raw)

    # ------------------------------------------------------------------
    # Customer Vault
    # ------------------------------------------------------------------

    def add_customer(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        company: str = "",
        address1: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        country: str = "US",
        phone: str = "",
        arcos7_artist_id: str = "",
    ) -> CeleroResponse:
        """
        Register a new customer in the Celero Customer Vault.

        The returned ``customer_vault_id`` should be stored on the
        :class:`~arcos7.models.artist.Artist` record as
        ``celero_customer_vault_id``.

        Card / bank details are collected separately via Celero's hosted
        Collect.js form (PCI scope remains entirely with Celero).
        """
        self._require_configured("add_customer")
        return self._post(self._api_url, {
            "customer_vault": "add_customer",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "company": company or "",
            "address1": address1 or "",
            "city": city or "",
            "state": state or "",
            "zip": zip_code or "",
            "country": country or "US",
            "phone": phone or "",
            "order_description": f"ARCOS7 artist: {arcos7_artist_id}",
        })

    def update_customer(
        self,
        customer_vault_id: str,
        **fields: str,
    ) -> CeleroResponse:
        """Update an existing customer vault record."""
        self._require_configured("update_customer")
        return self._post(self._api_url, {
            "customer_vault": "update_customer",
            "customer_vault_id": customer_vault_id,
            **fields,
        })

    def delete_customer(self, customer_vault_id: str) -> CeleroResponse:
        """Remove a customer from the vault."""
        self._require_configured("delete_customer")
        return self._post(self._api_url, {
            "customer_vault": "delete_customer",
            "customer_vault_id": customer_vault_id,
        })

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def charge(
        self,
        *,
        amount: float,
        customer_vault_id: str,
        currency: str = "usd",
        order_id: str = "",
        order_description: str = "",
        ip_address: str = "",
    ) -> CeleroResponse:
        """
        Charge a stored customer vault record.

        Use this to collect ARCOS7's 10% contingency fee after a claim
        is reconciled.  The ``customer_vault_id`` comes from the artist's
        Celero registration (``POST /artists/{id}/celero/register``).

        Parameters
        ----------
        amount:
            Amount in dollars (e.g. ``150.00`` for $150.00).
        customer_vault_id:
            Vault ID returned when the artist was registered.
        currency:
            ISO 4217 currency code, lowercase (default ``"usd"``).
        order_id:
            Your internal order/invoice reference (e.g. ARCOS7 claim ID).
        order_description:
            Human-readable description shown on the artist's statement.
        """
        self._require_configured("charge")
        return self._post(self._api_url, {
            "type": "sale",
            "amount": f"{amount:.2f}",
            "customer_vault_id": customer_vault_id,
            "currency": currency.lower(),
            "orderid": order_id or "",
            "order_description": order_description or "ARCOS7 recovery fee",
            "ipaddress": ip_address or "",
        })

    def refund(
        self,
        *,
        transaction_id: str,
        amount: float | None = None,
    ) -> CeleroResponse:
        """
        Refund a previously captured transaction.

        If ``amount`` is omitted the full transaction amount is refunded.
        """
        self._require_configured("refund")
        params: dict[str, str] = {
            "type": "refund",
            "transactionid": transaction_id,
        }
        if amount is not None:
            params["amount"] = f"{amount:.2f}"
        return self._post(self._api_url, params)

    def void(self, *, transaction_id: str) -> CeleroResponse:
        """
        Void an unsettled transaction.

        Use instead of refund when the transaction has not yet settled
        (typically same-day).
        """
        self._require_configured("void")
        return self._post(self._api_url, {
            "type": "void",
            "transactionid": transaction_id,
        })

    def disburse(
        self,
        *,
        amount: float,
        customer_vault_id: str,
        currency: str = "usd",
        order_id: str = "",
        order_description: str = "",
    ) -> CeleroResponse:
        """
        Disburse (pay out) funds to an artist via ACH credit.

        This is used to send the artist their net recovery amount (recovered
        royalties minus ARCOS7's 10% contingency fee) directly to their
        bank account stored in the Celero vault.

        Requires the Celero account to have ACH payout capability enabled.
        Contact Celero onboarding to activate disbursements.
        """
        self._require_configured("disburse")
        return self._post(self._api_url, {
            "type": "credit",      # ACH credit = outbound payout
            "amount": f"{amount:.2f}",
            "customer_vault_id": customer_vault_id,
            "currency": currency.lower(),
            "orderid": order_id or "",
            "order_description": order_description or "ARCOS7 royalty disbursement",
        })

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query_transaction(self, transaction_id: str) -> dict:
        """
        Fetch current status and details of a transaction from the gateway.

        Useful for reconciliation and when a webhook was not received.
        """
        self._require_configured("query_transaction")
        resp = self._post(self._query_url, {"transaction_id": transaction_id})
        return resp.to_dict()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """
        Return the configuration status of the Celero client.

        Called by ``GET /health/readiness`` to show operators whether the
        integration is ready.
        """
        return {
            "configured": self.configured,
            "status": "ready" if self.configured else "missing_credentials",
            "required_env_vars": [
                "CELERO_SECURITY_KEY",
                "CELERO_WEBHOOK_SECRET",
            ],
            "optional_env_vars": [
                "CELERO_API_URL",
                "CELERO_QUERY_URL",
            ],
            "setup_url": "https://celerocommerce.com/developers/",
            "note": (
                "CELERO_SECURITY_KEY is issued during Celero Commerce merchant onboarding.  "
                "Request a sandbox key at https://celerocommerce.com/developers/  "
                "CELERO_WEBHOOK_SECRET is configured in the Celero merchant dashboard "
                "under Settings → Webhooks."
            ),
        }
