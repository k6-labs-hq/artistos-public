"""Add payer-provided identifier columns to payments.

Captures the per-row payer identifiers (BMI PARTICIPANT #, IP #, TITLE #,
and the same concepts on ASCAP/MLC statements) so dispute packets can
reference the payer's own internal IDs rather than asking the artist to
look them up at filing time.

All three columns are nullable — historical rows ingested before this
migration won't have them, and not every parser populates all three.

Revision ID: 20260504_0037
Revises: 20260426_0036
Create Date: 2026-05-04
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260504_0037"
down_revision = "20260426_0036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("payer_account_id", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("payer_ip_number", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("payer_work_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("payments", "payer_work_id")
    op.drop_column("payments", "payer_ip_number")
    op.drop_column("payments", "payer_account_id")
