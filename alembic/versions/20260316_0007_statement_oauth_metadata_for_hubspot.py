"""statement and oauth metadata for HubSpot sync

Revision ID: 20260316_0007
Revises: 20260316_0006
Create Date: 2026-03-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260316_0007"
down_revision = "20260316_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "statements",
        sa.Column("ingestion_metadata_json", sa.Text(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "connector_account_links",
        sa.Column("profile_metadata_json", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("connector_account_links", "profile_metadata_json")
    op.drop_column("statements", "ingestion_metadata_json")
