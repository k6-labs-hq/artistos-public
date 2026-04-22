"""Add deleted_at column for soft-delete across 5 tables.

Models reference Artist.deleted_at / Work.deleted_at / TermsAcceptance.deleted_at /
Claim.deleted_at / Anomaly.deleted_at but no migration ever created the columns.
This caused every query that filters on deleted_at to fail with:
    column ..._at does not exist

Adding nullable DateTime columns + indexes for each. No data backfill needed —
existing rows have deleted_at = NULL (i.e., not deleted).

Revision ID: 20260422_0034
Revises: 20260421_0033
Create Date: 2026-04-22
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260422_0034"
down_revision = "20260421_0033"
branch_labels = None
depends_on = None


SOFT_DELETE_TABLES = [
    "artists",
    "works",
    "terms_acceptances",
    "claims",
    "anomalies",
]


def _has_table(table: str) -> bool:
    try:
        return inspect(op.get_bind()).has_table(table)
    except Exception:
        return False


def _has_column(table: str, column: str) -> bool:
    if not _has_table(table):
        return False
    try:
        cols = [c["name"] for c in inspect(op.get_bind()).get_columns(table)]
        return column in cols
    except Exception:
        return False


def upgrade() -> None:
    # Skip tables that don't exist yet — several are created at app-startup
    # via Base.metadata.create_all, and the model already declares deleted_at
    # so a fresh create_all handles those. This migration only adds the column
    # to tables that already exist in an older deployed schema.
    for table in SOFT_DELETE_TABLES:
        if not _has_table(table):
            continue
        if not _has_column(table, "deleted_at"):
            op.add_column(table, sa.Column("deleted_at", sa.DateTime(), nullable=True))
            op.create_index(
                f"ix_{table}_deleted_at",
                table,
                ["deleted_at"],
            )


def downgrade() -> None:
    for table in SOFT_DELETE_TABLES:
        if _has_column(table, "deleted_at"):
            op.drop_index(f"ix_{table}_deleted_at", table_name=table)
            op.drop_column(table, "deleted_at")
