"""xr7 cleanup constraints

Revision ID: 20260317_0018
Revises: 20260317_0017
Create Date: 2026-03-17
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260317_0018"
down_revision = "20260317_0017"
branch_labels = None
depends_on = None


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name.startswith("sqlite")


def _constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        checks = insp.get_check_constraints(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any(c.get("name") == constraint_name for c in checks)


def upgrade() -> None:
    if _is_sqlite():
        return

    if not _constraint_exists("xr7_usage_events", "ck_xr7_usage_events_confidence_score_01"):
        op.create_check_constraint(
            "ck_xr7_usage_events_confidence_score_01",
            "xr7_usage_events",
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
        )

    if not _constraint_exists("xr7_usage_events", "ck_xr7_usage_events_black_box_risk_score_01"):
        op.create_check_constraint(
            "ck_xr7_usage_events_black_box_risk_score_01",
            "xr7_usage_events",
            "black_box_risk_score >= 0.0 AND black_box_risk_score <= 1.0",
        )

    if not _constraint_exists("xr7_tracks", "ck_xr7_tracks_metadata_quality_score_01"):
        op.create_check_constraint(
            "ck_xr7_tracks_metadata_quality_score_01",
            "xr7_tracks",
            "metadata_quality_score >= 0.0 AND metadata_quality_score <= 1.0",
        )


def downgrade() -> None:
    if _is_sqlite():
        return

    for table_name, constraint_name in [
        ("xr7_tracks", "ck_xr7_tracks_metadata_quality_score_01"),
        ("xr7_usage_events", "ck_xr7_usage_events_black_box_risk_score_01"),
        ("xr7_usage_events", "ck_xr7_usage_events_confidence_score_01"),
    ]:
        if _constraint_exists(table_name, constraint_name):
            op.drop_constraint(constraint_name, table_name, type_="check")
