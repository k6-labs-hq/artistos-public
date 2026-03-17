"""replace celero integration with trolley payout schema

Revision ID: 20260317_0012
Revises: 20260316_0011
Create Date: 2026-03-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260317_0012"
down_revision = "20260316_0011"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = insp.get_columns(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any(c.get("name") == column_name for c in cols)


def _add_col_if_missing(table_name: str, column: sa.Column) -> None:
    if not _table_exists(table_name):
        return
    if _column_exists(table_name, str(column.name)):
        return
    op.add_column(table_name, column)


def _drop_col_if_exists(table_name: str, column_name: str) -> None:
    if _table_exists(table_name) and _column_exists(table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    _add_col_if_missing("artists", sa.Column("first_name", sa.String(), nullable=True))
    _add_col_if_missing("artists", sa.Column("last_name", sa.String(), nullable=True))
    _add_col_if_missing("artists", sa.Column("country_code", sa.String(), nullable=False, server_default="US"))
    _add_col_if_missing("artists", sa.Column("trolley_recipient_id", sa.String(), nullable=True))
    _add_col_if_missing("artists", sa.Column("payout_account_status", sa.String(), nullable=False, server_default="not_started"))
    _add_col_if_missing("artists", sa.Column("payout_method_type", sa.String(), nullable=True))
    _add_col_if_missing("artists", sa.Column("payout_last4", sa.String(), nullable=True))
    _add_col_if_missing("artists", sa.Column("tax_form_status", sa.String(), nullable=False, server_default="pending"))

    _add_col_if_missing("claims", sa.Column("platform_fee_percent", sa.Float(), nullable=False, server_default="10"))
    _add_col_if_missing("claims", sa.Column("platform_fee_amount", sa.Float(), nullable=True))
    _add_col_if_missing("claims", sa.Column("artist_net_amount", sa.Float(), nullable=True))
    _add_col_if_missing("claims", sa.Column("remittance_method", sa.String(), nullable=True))
    _add_col_if_missing("claims", sa.Column("remittance_reference_number", sa.String(), nullable=True))
    _add_col_if_missing("claims", sa.Column("remittance_received_at", sa.DateTime(), nullable=True))
    _add_col_if_missing("claims", sa.Column("trolley_payment_id", sa.String(), nullable=True))
    _add_col_if_missing("claims", sa.Column("trolley_payment_status", sa.String(), nullable=True))
    _add_col_if_missing("claims", sa.Column("trolley_fx_rate", sa.Float(), nullable=True))
    _add_col_if_missing("claims", sa.Column("trolley_local_amount", sa.Float(), nullable=True))
    _add_col_if_missing("claims", sa.Column("trolley_local_currency", sa.String(), nullable=True))
    _add_col_if_missing("claims", sa.Column("payout_retry_count", sa.Integer(), nullable=False, server_default="0"))
    _add_col_if_missing("claims", sa.Column("payout_failure_reason", sa.String(), nullable=True))

    if _table_exists("artists") and _column_exists("artists", "celero_customer_vault_id"):
        op.drop_column("artists", "celero_customer_vault_id")

    if not _table_exists("trolley_transactions"):
        op.create_table(
            "trolley_transactions",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("claim_id", sa.String(), nullable=True),
            sa.Column("type", sa.Enum("REMITTANCE", "DISBURSEMENT", name="trolleytxntype"), nullable=False),
            sa.Column("status", sa.Enum("PENDING", "PROCESSING", "PAID", "FAILED", "RETURNED", name="trolleytxnstatus"), nullable=False),
            sa.Column("gross_amount", sa.Float(), nullable=True),
            sa.Column("platform_fee_amount", sa.Float(), nullable=True),
            sa.Column("net_amount", sa.Float(), nullable=True),
            sa.Column("source_currency", sa.String(), nullable=False),
            sa.Column("local_amount", sa.Float(), nullable=True),
            sa.Column("local_currency", sa.String(), nullable=True),
            sa.Column("exchange_rate", sa.Float(), nullable=True),
            sa.Column("trolley_payment_id", sa.String(), nullable=True),
            sa.Column("trolley_batch_id", sa.String(), nullable=True),
            sa.Column("external_id", sa.String(), nullable=True),
            sa.Column("failure_reason", sa.String(), nullable=True),
            sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.ForeignKeyConstraint(["claim_id"], ["claims.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_trolley_transactions_artist_id", "trolley_transactions", ["artist_id"])
        op.create_index("ix_trolley_transactions_claim_id", "trolley_transactions", ["claim_id"])
        op.create_index("ix_trolley_transactions_trolley_payment_id", "trolley_transactions", ["trolley_payment_id"])
        op.create_index("ix_trolley_transactions_external_id", "trolley_transactions", ["external_id"])


def downgrade() -> None:
    if _table_exists("trolley_transactions"):
        op.drop_table("trolley_transactions")

    _drop_col_if_exists("claims", "payout_failure_reason")
    _drop_col_if_exists("claims", "payout_retry_count")
    _drop_col_if_exists("claims", "trolley_local_currency")
    _drop_col_if_exists("claims", "trolley_local_amount")
    _drop_col_if_exists("claims", "trolley_fx_rate")
    _drop_col_if_exists("claims", "trolley_payment_status")
    _drop_col_if_exists("claims", "trolley_payment_id")
    _drop_col_if_exists("claims", "remittance_received_at")
    _drop_col_if_exists("claims", "remittance_reference_number")
    _drop_col_if_exists("claims", "remittance_method")
    _drop_col_if_exists("claims", "artist_net_amount")
    _drop_col_if_exists("claims", "platform_fee_amount")
    _drop_col_if_exists("claims", "platform_fee_percent")

    _drop_col_if_exists("artists", "tax_form_status")
    _drop_col_if_exists("artists", "payout_last4")
    _drop_col_if_exists("artists", "payout_method_type")
    _drop_col_if_exists("artists", "payout_account_status")
    _drop_col_if_exists("artists", "trolley_recipient_id")
    _drop_col_if_exists("artists", "country_code")
    _drop_col_if_exists("artists", "last_name")
    _drop_col_if_exists("artists", "first_name")

    _add_col_if_missing("artists", sa.Column("celero_customer_vault_id", sa.String(), nullable=True))
