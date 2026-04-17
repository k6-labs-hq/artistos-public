"""add iso 4217 currency validation

Revision ID: 20260416_2133
Revises: 20260416_2123
Create Date: 2026-04-16

CRITICAL DATA INTEGRITY FIX: Add ISO 4217 currency code validation to prevent
invalid currency codes from breaking Trolley payouts.

Without this validation, the system could accept invalid currency codes like:
  - Typos: "USd", "eur", "DOLLARS"
  - Non-existent codes: "XXX", "ZZZ"
  - Cryptocurrencies: "BTC", "ETH" (not supported by Trolley)

This would cause:
  - Trolley API errors when attempting payouts
  - Failed disbursements requiring manual intervention
  - Artists not receiving payments on time
  - Support overhead dealing with failed transactions

The migration adds database check constraints that enforce only valid ISO 4217
currency codes recognized by Trolley's international payout system.

Validates both:
  - claim.currency (primary claim currency, default USD)
  - claim.trolley_local_currency (FX-converted local currency for payout)

Supported currencies include: USD, EUR, GBP, CAD, AUD, JPY, CNY, INR, BRL, MXN
and 40+ other major international currencies.
"""

from __future__ import annotations

from alembic import op

revision = "20260416_2133"
down_revision = "20260416_2123"
branch_labels = None
depends_on = None

# ISO 4217 currency codes supported by Trolley
VALID_CURRENCY_CODES = sorted(
    [
        "AED",
        "ARS",
        "AUD",
        "BRL",
        "CAD",
        "CHF",
        "CLP",
        "CNY",
        "COP",
        "CZK",
        "DKK",
        "EGP",
        "EUR",
        "GBP",
        "HKD",
        "HUF",
        "IDR",
        "ILS",
        "INR",
        "JPY",
        "KES",
        "KRW",
        "MXN",
        "MYR",
        "NGN",
        "NOK",
        "NZD",
        "PEN",
        "PHP",
        "PLN",
        "RON",
        "RUB",
        "SAR",
        "SEK",
        "SGD",
        "THB",
        "TRY",
        "USD",
        "VND",
        "ZAR",
    ]
)


def upgrade() -> None:
    # Add check constraint for currency field
    op.create_check_constraint(
        "valid_currency_code",
        "claims",
        f"currency IN ({','.join(repr(c) for c in VALID_CURRENCY_CODES)})",
    )

    # Add check constraint for trolley_local_currency field
    op.create_check_constraint(
        "valid_trolley_currency_code",
        "claims",
        f"trolley_local_currency IS NULL OR trolley_local_currency IN ({','.join(repr(c) for c in VALID_CURRENCY_CODES)})",
    )


def downgrade() -> None:
    # Drop check constraints
    op.drop_constraint("valid_trolley_currency_code", "claims", type_="check")
    op.drop_constraint("valid_currency_code", "claims", type_="check")
