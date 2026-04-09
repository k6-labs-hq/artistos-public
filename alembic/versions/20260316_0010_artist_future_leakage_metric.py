"""artist future leakage prevented metric

Revision ID: 20260316_0010
Revises: 20260316_0009
Create Date: 2026-03-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260316_0010"
down_revision = "20260316_0009"
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
    if not _table_exists("artists"):
        return
    if _column_exists("artists", "xr7_future_leakage_prevented"):
        return
    op.add_column(
        "artists",
        sa.Column("xr7_future_leakage_prevented", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    if not _table_exists("artists"):
        return
    if not _column_exists("artists", "xr7_future_leakage_prevented"):
        return
    op.drop_column("artists", "xr7_future_leakage_prevented")
