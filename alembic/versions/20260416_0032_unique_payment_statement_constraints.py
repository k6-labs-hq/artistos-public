"""
Add composite unique constraints to payments and statements tables.

- payments(artist_id, reference_id) — prevents duplicate payment records
  for the same artist + payer reference ID.
- statements(artist_id, file_hash) — prevents re-ingesting the same raw
  file for an artist (the upload handler marks duplicates; this is the
  DB-level safety net for concurrent uploads).

Revision ID: 20260416_0032
Revises: 20260416_0031
Create Date: 2026-04-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260416_0032"
down_revision = "20260416_0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # payments: uq_payments_artist_reference
    existing_payment_constraints = {c["name"] for c in inspector.get_unique_constraints("payments")}
    if "uq_payments_artist_reference" not in existing_payment_constraints:
        # SQLite does not support ADD CONSTRAINT directly; use create_unique_constraint
        # which falls back to an index on SQLite-compatible dialects.
        op.create_unique_constraint(
            "uq_payments_artist_reference",
            "payments",
            ["artist_id", "reference_id"],
        )

    # statements: uq_statements_artist_hash
    existing_stmt_constraints = {c["name"] for c in inspector.get_unique_constraints("statements")}
    if "uq_statements_artist_hash" not in existing_stmt_constraints:
        op.create_unique_constraint(
            "uq_statements_artist_hash",
            "statements",
            ["artist_id", "file_hash"],
        )


def downgrade() -> None:
    op.drop_constraint("uq_payments_artist_reference", "payments", type_="unique")
    op.drop_constraint("uq_statements_artist_hash", "statements", type_="unique")
