"""statement and oauth metadata for HubSpot sync

Revision ID: 20260316_0007
Revises: 20260316_0006
Create Date: 2026-03-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260316_0007"
down_revision = "20260316_0006"
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


def upgrade() -> None:
    if _table_exists("statements") and not _column_exists("statements", "ingestion_metadata_json"):
        op.add_column(
            "statements",
            sa.Column("ingestion_metadata_json", sa.Text(), nullable=False, server_default="{}"),
        )
    if _table_exists("connector_account_links") and not _column_exists("connector_account_links", "profile_metadata_json"):
        op.add_column(
            "connector_account_links",
            sa.Column("profile_metadata_json", sa.Text(), nullable=False, server_default="{}"),
        )


def downgrade() -> None:
    if _table_exists("connector_account_links") and _column_exists("connector_account_links", "profile_metadata_json"):
        op.drop_column("connector_account_links", "profile_metadata_json")
    if _table_exists("statements") and _column_exists("statements", "ingestion_metadata_json"):
        op.drop_column("statements", "ingestion_metadata_json")
