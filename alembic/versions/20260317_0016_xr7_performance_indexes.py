"""xr7 performance indexes

Revision ID: 20260317_0016
Revises: 20260317_0015
Create Date: 2026-03-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260317_0016"
down_revision = "20260317_0015"
branch_labels = None
depends_on = None


def _index_exists(index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        indexes = []
        for table in insp.get_table_names():
            indexes.extend(insp.get_indexes(table))
        return any(ix.get("name") == index_name for ix in indexes)
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if not _index_exists("ix_xr7_usage_events_tenant_artist_event_ts"):
        op.create_index(
            "ix_xr7_usage_events_tenant_artist_event_ts",
            "xr7_usage_events",
            ["tenant_id", "artist_id", "event_timestamp"],
        )
    if not _index_exists("ix_xr7_usage_events_tenant_platform_territory_event_ts"):
        op.create_index(
            "ix_xr7_usage_events_tenant_platform_territory_event_ts",
            "xr7_usage_events",
            ["tenant_id", "platform", "territory", "event_timestamp"],
        )
    if not _index_exists("ix_xr7_royalty_statement_lines_statement_row"):
        op.create_index(
            "ix_xr7_royalty_statement_lines_statement_row",
            "xr7_royalty_statement_lines",
            ["statement_id", "row_index"],
        )
    if not _index_exists("ix_xr7_unmatched_works_tenant_artist_status_updated"):
        op.create_index(
            "ix_xr7_unmatched_works_tenant_artist_status_updated",
            "xr7_unmatched_works",
            ["tenant_id", "artist_id", "status", "updated_at"],
        )
    if not _index_exists("ix_xr7_catalog_valuation_tenant_artist_as_of"):
        op.create_index(
            "ix_xr7_catalog_valuation_tenant_artist_as_of",
            "xr7_catalog_valuation_snapshots",
            ["tenant_id", "artist_id", "as_of_date"],
        )


def downgrade() -> None:
    for index_name, table_name in [
        ("ix_xr7_catalog_valuation_tenant_artist_as_of", "xr7_catalog_valuation_snapshots"),
        ("ix_xr7_unmatched_works_tenant_artist_status_updated", "xr7_unmatched_works"),
        ("ix_xr7_royalty_statement_lines_statement_row", "xr7_royalty_statement_lines"),
        ("ix_xr7_usage_events_tenant_platform_territory_event_ts", "xr7_usage_events"),
        ("ix_xr7_usage_events_tenant_artist_event_ts", "xr7_usage_events"),
    ]:
        if _index_exists(index_name):
            op.drop_index(index_name, table_name=table_name)
