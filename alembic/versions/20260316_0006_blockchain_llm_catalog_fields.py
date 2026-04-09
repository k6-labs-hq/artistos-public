"""blockchain anchor and catalog contract fields

Revision ID: 20260316_0006
Revises: 20260314_0005
Create Date: 2026-03-16 12:40:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260316_0006"
down_revision = "20260314_0005"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = insp.get_columns(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any(c.get("name") == column_name for c in cols)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if _table_exists("evidence_anchors") and not _column_exists("evidence_anchors", "cid"):
        op.add_column("evidence_anchors", sa.Column("cid", sa.String(), nullable=True))

    if _table_exists("evidence_anchors") and not _column_exists("evidence_anchors", "tx_hash"):
        op.add_column("evidence_anchors", sa.Column("tx_hash", sa.String(), nullable=True))

    if _table_exists("evidence_anchors") and not _column_exists("evidence_anchors", "blockchain_status"):
        op.add_column(
            "evidence_anchors",
            sa.Column("blockchain_status", sa.String(), nullable=False, server_default="PENDING"),
        )
        op.alter_column("evidence_anchors", "blockchain_status", server_default=None)

    if _table_exists("catalog_graph_snapshots") and not _column_exists("catalog_graph_snapshots", "contract_address"):
        op.add_column("catalog_graph_snapshots", sa.Column("contract_address", sa.String(), nullable=True))


def downgrade() -> None:
    if _table_exists("catalog_graph_snapshots") and _column_exists("catalog_graph_snapshots", "contract_address"):
        op.drop_column("catalog_graph_snapshots", "contract_address")

    if _table_exists("evidence_anchors") and _column_exists("evidence_anchors", "blockchain_status"):
        op.drop_column("evidence_anchors", "blockchain_status")

    if _table_exists("evidence_anchors") and _column_exists("evidence_anchors", "tx_hash"):
        op.drop_column("evidence_anchors", "tx_hash")

    if _table_exists("evidence_anchors") and _column_exists("evidence_anchors", "cid"):
        op.drop_column("evidence_anchors", "cid")
