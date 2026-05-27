"""Add statement_id to events + payments for per-file attribution.

Closes #333.

Today every event/payment carries only `artist_id`, so we can compute
"this artist has $X recoverable" but never "this PDF surfaced $Y vs this
CSV surfaced $Z." That blocks parser-ROI analysis, file-level debugging,
and operator clarity when reviewing anomalies.

Both columns are nullable so existing rows stay legal. We deliberately
do NOT add a foreign-key constraint:

- The upload write path in `XR7/api/routers/ingestion.py` commits events
  and payments BEFORE creating the Statement row. An FK with default
  (immediate) check semantics would fail every upload until that flow is
  restructured. Restructuring is out of scope for this migration; we'll
  add the FK in a follow-up after the write-path change.
- Attribution doesn't strictly require referential integrity. An orphan
  statement_id (e.g. if a Statement gets deleted) just means a stale
  pointer, which is fine for reporting and harmless for the engine.

Backfill is intentionally NOT done — historical rows stay NULL. We don't
have the data to recover historical attribution and synthesizing it
would introduce wrong numbers in reports.

Revision ID: 20260527_0001
Revises: 20260508_0001
Create Date: 2026-05-27
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260527_0001"
down_revision = "20260508_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("statement_id", sa.String(), nullable=True))
    op.create_index("ix_events_statement_id", "events", ["statement_id"])
    op.add_column("payments", sa.Column("statement_id", sa.String(), nullable=True))
    op.create_index("ix_payments_statement_id", "payments", ["statement_id"])


def downgrade() -> None:
    op.drop_index("ix_payments_statement_id", table_name="payments")
    op.drop_column("payments", "statement_id")
    op.drop_index("ix_events_statement_id", table_name="events")
    op.drop_column("events", "statement_id")
