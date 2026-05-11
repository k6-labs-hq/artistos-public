"""Add work_identity_cache table + payments.iswc column.

Backs issue #278 — the ISWC bridge between BMI/ASCAP work_no and MLC's
ISWC-indexed database. The cache table memoizes external lookups
(MusicBrainz primarily, Discogs later) so re-running ingestion doesn't
re-query and we stay inside MusicBrainz's 1 req/sec budget. The
payments.iswc column holds the resolved ISWC per Payment row so dispute
packets can cite both the payer's internal work id and the cross-PRO
identifier in the same line item.

Revision ID: 20260508_0001
Revises: 20260505_0041
Create Date: 2026-05-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260508_0001"
down_revision = "20260505_0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_identity_cache",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("artist_normalized", sa.String(), nullable=False),
        sa.Column("title_normalized", sa.String(), nullable=False),
        sa.Column("artist_raw", sa.String(), nullable=False),
        sa.Column("title_raw", sa.String(), nullable=False),
        sa.Column("iswc", sa.String(), nullable=True),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("looked_up_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "source",
            "artist_normalized",
            "title_normalized",
            name="uq_work_identity_cache_key",
        ),
    )
    op.create_index(
        "ix_work_identity_cache_iswc", "work_identity_cache", ["iswc"], unique=False
    )

    op.add_column("payments", sa.Column("iswc", sa.String(), nullable=True))
    op.create_index("ix_payments_iswc", "payments", ["iswc"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payments_iswc", table_name="payments")
    op.drop_column("payments", "iswc")
    op.drop_index("ix_work_identity_cache_iswc", table_name="work_identity_cache")
    op.drop_table("work_identity_cache")
