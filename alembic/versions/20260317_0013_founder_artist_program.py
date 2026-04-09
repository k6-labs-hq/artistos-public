"""founder artist cohort fields and platform config

Revision ID: 20260317_0013
Revises: 20260317_0012
Create Date: 2026-03-17
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260317_0013"
down_revision = "20260317_0012"
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


def _add_col_if_missing(table_name: str, column: sa.Column) -> None:
    if not _table_exists(table_name):
        return
    if _column_exists(table_name, str(column.name)):
        return
    op.add_column(table_name, column)


def _constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        checks = insp.get_check_constraints(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any((c.get("name") or "") == constraint_name for c in checks)


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        idx = insp.get_indexes(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any((i.get("name") or "") == index_name for i in idx)


def upgrade() -> None:
    _add_col_if_missing("artists", sa.Column("is_founder", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add_col_if_missing("artists", sa.Column("founder_slot_number", sa.Integer(), nullable=True))
    _add_col_if_missing("artists", sa.Column("founder_locked_at", sa.DateTime(), nullable=True))
    _add_col_if_missing("artists", sa.Column("contingency_fee_percent", sa.Float(), nullable=True))
    if _table_exists("artists") and not _index_exists("artists", "ix_artists_founder_slot_number"):
        op.create_index("ix_artists_founder_slot_number", "artists", ["founder_slot_number"])

    if _table_exists("artists") and not _constraint_exists("artists", "ck_artists_founder_fee_max"):
        op.create_check_constraint(
            "ck_artists_founder_fee_max",
            "artists",
            "(NOT is_founder) OR contingency_fee_percent <= 10",
        )

    if not _table_exists("platform_config"):
        op.create_table(
            "platform_config",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("founder_cohort_limit", sa.Integer(), nullable=False, server_default="2500"),
            sa.Column("founder_fee_percent", sa.Float(), nullable=False, server_default="10"),
            sa.Column("founder_slots_filled", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("standard_contingency_fee_percent", sa.Float(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    op.execute(
        """
        INSERT INTO platform_config (id, founder_cohort_limit, founder_fee_percent, founder_slots_filled, updated_at)
        SELECT 1, 2500, 10, 0, CURRENT_TIMESTAMP
        WHERE NOT EXISTS (SELECT 1 FROM platform_config WHERE id = 1)
        """
    )


def downgrade() -> None:
    if _table_exists("platform_config"):
        op.drop_table("platform_config")

    if _table_exists("artists"):
        if _constraint_exists("artists", "ck_artists_founder_fee_max"):
            op.drop_constraint("ck_artists_founder_fee_max", "artists", type_="check")
        if _index_exists("artists", "ix_artists_founder_slot_number"):
            op.drop_index("ix_artists_founder_slot_number", table_name="artists")
        if _column_exists("artists", "contingency_fee_percent"):
            op.drop_column("artists", "contingency_fee_percent")
        if _column_exists("artists", "founder_locked_at"):
            op.drop_column("artists", "founder_locked_at")
        if _column_exists("artists", "founder_slot_number"):
            op.drop_column("artists", "founder_slot_number")
        if _column_exists("artists", "is_founder"):
            op.drop_column("artists", "is_founder")
