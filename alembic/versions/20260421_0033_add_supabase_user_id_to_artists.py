"""Add supabase_user_id column to artists table for Supabase Auth integration.

Revision ID: 20260421_0033
Revises: e97a0aed10b5
Create Date: 2026-04-21
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260421_0033"
down_revision = "e97a0aed10b5"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    cols = [c["name"] for c in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("artists", "supabase_user_id"):
        op.add_column("artists", sa.Column("supabase_user_id", sa.String(), nullable=True))
        op.create_index(
            "ix_artists_supabase_user_id",
            "artists",
            ["supabase_user_id"],
            unique=True,
        )


def downgrade() -> None:
    if _has_column("artists", "supabase_user_id"):
        op.drop_index("ix_artists_supabase_user_id", table_name="artists")
        op.drop_column("artists", "supabase_user_id")
