"""Add soft-delete column to terms_acceptances.

Revision ID: 20260416_2228
Revises: 20260416_2207
Create Date: 2026-04-16 22:28:00
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260416_2228"
down_revision = "20260416_2207"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("terms_acceptances", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index(
        "ix_terms_acceptances_deleted_at",
        "terms_acceptances",
        ["deleted_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_terms_acceptances_deleted_at", table_name="terms_acceptances")
    op.drop_column("terms_acceptances", "deleted_at")
