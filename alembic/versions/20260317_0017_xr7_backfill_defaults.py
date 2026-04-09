"""xr7 backfill defaults

Revision ID: 20260317_0017
Revises: 20260317_0016
Create Date: 2026-03-17
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260317_0017"
down_revision = "20260317_0016"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if _table_exists("xr7_tracks"):
        op.execute(
            sa.text(
                """
                UPDATE xr7_tracks
                SET metadata_quality_score = COALESCE(metadata_quality_score, 0.0),
                    ai_repair_status = COALESCE(ai_repair_status, 'not_evaluated')
                """
            )
        )

    if _table_exists("xr7_usage_events"):
        op.execute(
            sa.text(
                """
                UPDATE xr7_usage_events
                SET short_form_signal_strength = COALESCE(short_form_signal_strength, 0.0),
                    black_box_risk_score = COALESCE(black_box_risk_score, 0.0),
                    explainability_json = COALESCE(explainability_json, '{}')
                """
            )
        )

    if _table_exists("xr7_unmatched_works"):
        op.execute(
            sa.text(
                """
                UPDATE xr7_unmatched_works
                SET suggested_matches_json = COALESCE(suggested_matches_json, '[]'),
                    suggested_resolution_actions_json = COALESCE(suggested_resolution_actions_json, '[]'),
                    ai_resolution_confidence = COALESCE(ai_resolution_confidence, 0.0)
                """
            )
        )


def downgrade() -> None:
    return
