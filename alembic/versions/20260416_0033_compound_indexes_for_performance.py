"""compound indexes for performance

Revision ID: 20260416_0033
Revises: 20260416_0032
Create Date: 2026-04-16

Add compound indexes on claims, anomalies, and statements tables to optimize
heavy filtering and sorting queries in the API. These tables are frequently
filtered by (artist_id, status) and ordered by timestamps, causing full table
scans on larger datasets.

Without these indexes, queries like:
  - GET /artists/{id}/claims?status=OPEN
  - GET /artists/{id}/anomalies?status=INVESTIGATING
  - GET /artists/{id}/statements?status=PROCESSED
require sequential scans. With compound indexes, these become index-only scans.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260416_0033"
down_revision = "20260416_0032"
branch_labels = None
depends_on = None


def _index_exists(index_name: str) -> bool:
    """Check if an index already exists to avoid migration errors on re-runs."""
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
    # Claims: artist_id + status + updated_at (sorted by updated_at in API)
    if not _index_exists("ix_claims_artist_status_updated"):
        op.create_index(
            "ix_claims_artist_status_updated",
            "claims",
            ["artist_id", "status", "updated_at"],
        )

    # Anomalies: artist_id + status + created_at (sorted by created_at in API)
    if not _index_exists("ix_anomalies_artist_status_created"):
        op.create_index(
            "ix_anomalies_artist_status_created",
            "anomalies",
            ["artist_id", "status", "created_at"],
        )

    # Statements: artist_id + status + uploaded_at (filtered by status, sorted by uploaded_at)
    if not _index_exists("ix_statements_artist_status_uploaded"):
        op.create_index(
            "ix_statements_artist_status_uploaded",
            "statements",
            ["artist_id", "status", "uploaded_at"],
        )


def downgrade() -> None:
    # Drop indexes in reverse order
    if _index_exists("ix_statements_artist_status_uploaded"):
        op.drop_index("ix_statements_artist_status_uploaded", table_name="statements")

    if _index_exists("ix_anomalies_artist_status_created"):
        op.drop_index("ix_anomalies_artist_status_created", table_name="anomalies")

    if _index_exists("ix_claims_artist_status_updated"):
        op.drop_index("ix_claims_artist_status_updated", table_name="claims")
