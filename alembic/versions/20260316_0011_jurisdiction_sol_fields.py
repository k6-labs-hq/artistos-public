"""jurisdiction aware sol fields for artists and claims

Revision ID: 20260316_0011
Revises: 20260316_0010
Create Date: 2026-03-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260316_0011"
down_revision = "20260316_0010"
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


def upgrade() -> None:
    _add_col_if_missing(
        "artists",
        sa.Column("primary_jurisdiction", sa.String(), nullable=False, server_default="USA"),
    )
    _add_col_if_missing(
        "artists",
        sa.Column("preferred_contract_type", sa.String(), nullable=False, server_default="recording"),
    )

    _add_col_if_missing(
        "claims",
        sa.Column("governing_law_state", sa.String(), nullable=False, server_default="USA"),
    )
    _add_col_if_missing(
        "claims",
        sa.Column("contract_type", sa.String(), nullable=False, server_default="recording"),
    )
    _add_col_if_missing("claims", sa.Column("infringement_date", sa.DateTime(), nullable=True))
    _add_col_if_missing("claims", sa.Column("discovery_date", sa.DateTime(), nullable=True))
    _add_col_if_missing("claims", sa.Column("sol_window_years", sa.Integer(), nullable=True))
    _add_col_if_missing("claims", sa.Column("sol_citation_source", sa.String(), nullable=True))


def downgrade() -> None:
    if _table_exists("claims"):
        if _column_exists("claims", "sol_citation_source"):
            op.drop_column("claims", "sol_citation_source")
        if _column_exists("claims", "sol_window_years"):
            op.drop_column("claims", "sol_window_years")
        if _column_exists("claims", "discovery_date"):
            op.drop_column("claims", "discovery_date")
        if _column_exists("claims", "infringement_date"):
            op.drop_column("claims", "infringement_date")
        if _column_exists("claims", "contract_type"):
            op.drop_column("claims", "contract_type")
        if _column_exists("claims", "governing_law_state"):
            op.drop_column("claims", "governing_law_state")

    if _table_exists("artists"):
        if _column_exists("artists", "preferred_contract_type"):
            op.drop_column("artists", "preferred_contract_type")
        if _column_exists("artists", "primary_jurisdiction"):
            op.drop_column("artists", "primary_jurisdiction")
