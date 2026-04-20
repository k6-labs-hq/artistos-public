"""
Add deleted_at soft-delete column to artists, works, claims, and anomalies.

Preserves referential integrity for historical records. Rows with a non-NULL
deleted_at are considered logically deleted; application queries should filter
on deleted_at IS NULL unless explicitly auditing erasures.

Revision ID: 20260416_0031
Revises: 20260407_0030
Create Date: 2026-04-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260416_0031"
down_revision = "20260407_0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table_name in ("artists", "works", "claims", "anomalies"):
        existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
        if "deleted_at" not in existing_cols:
            op.add_column(
                table_name,
                sa.Column("deleted_at", sa.DateTime(), nullable=True),
            )
            # Index speeds up the common filter: WHERE deleted_at IS NULL
            op.create_index(
                f"ix_{table_name}_deleted_at",
                table_name,
                ["deleted_at"],
            )


def downgrade() -> None:
    for table_name in ("artists", "works", "claims", "anomalies"):
        op.drop_index(f"ix_{table_name}_deleted_at", table_name=table_name)
        op.drop_column(table_name, "deleted_at")
