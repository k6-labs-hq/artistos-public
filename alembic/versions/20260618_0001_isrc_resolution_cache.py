"""Add isrc_resolution_cache for ISRC -> work metadata lookups.

Sibling of work_identity_cache (artist+title keyed). Stores the resolved work
(title, ISWCs, writer credits, evidence URL) as JSON, including negative
results, so metadata audits are cheap to re-run and citable.

Revision ID: 20260618_0001
Revises: 20260527_0001
Create Date: 2026-11-18
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260618_0001"
down_revision = "20260527_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "isrc_resolution_cache",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("isrc", sa.String(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("looked_up_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("source", "isrc", name="uq_isrc_resolution_cache_key"),
    )
    op.create_index(
        "ix_isrc_resolution_cache_isrc", "isrc_resolution_cache", ["isrc"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_isrc_resolution_cache_isrc", table_name="isrc_resolution_cache")
    op.drop_table("isrc_resolution_cache")
