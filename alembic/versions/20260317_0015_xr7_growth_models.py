"""xr7 growth models

Revision ID: 20260317_0015
Revises: 20260317_0014
Create Date: 2026-03-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260317_0015"
down_revision = "20260317_0014"
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


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if _table_exists(table_name) and not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def upgrade() -> None:
    _add_column_if_missing("xr7_tracks", sa.Column("metadata_quality_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_tracks", sa.Column("metadata_quality_grade", sa.String(), nullable=True))
    _add_column_if_missing("xr7_tracks", sa.Column("ai_repair_status", sa.String(), nullable=False, server_default="not_evaluated"))
    _add_column_if_missing("xr7_tracks", sa.Column("ugc_usage_velocity_7d", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_tracks", sa.Column("ugc_usage_velocity_30d", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_tracks", sa.Column("ugc_platform_coverage_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_tracks", sa.Column("viral_risk_score", sa.Float(), nullable=False, server_default="0.0"))

    _add_column_if_missing("xr7_works", sa.Column("registration_completeness_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_works", sa.Column("split_conflict_flag", sa.Boolean(), nullable=False, server_default=sa.false()))
    _add_column_if_missing("xr7_works", sa.Column("split_conflict_reason", sa.String(), nullable=True))
    _add_column_if_missing("xr7_works", sa.Column("recovery_forecast_90d", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_works", sa.Column("recovery_forecast_365d", sa.Float(), nullable=False, server_default="0.0"))

    _add_column_if_missing("xr7_usage_events", sa.Column("ugc_content_id", sa.String(), nullable=True))
    _add_column_if_missing("xr7_usage_events", sa.Column("ugc_format", sa.String(), nullable=True))
    _add_column_if_missing("xr7_usage_events", sa.Column("ugc_video_duration_sec", sa.Integer(), nullable=True))
    _add_column_if_missing("xr7_usage_events", sa.Column("remix_parent_ref", sa.String(), nullable=True))
    _add_column_if_missing("xr7_usage_events", sa.Column("trend_cluster_id", sa.String(), nullable=True))
    _add_column_if_missing("xr7_usage_events", sa.Column("short_form_signal_strength", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_usage_events", sa.Column("black_box_risk_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_usage_events", sa.Column("explainability_json", sa.Text(), nullable=False, server_default="{}"))

    _add_column_if_missing("xr7_unmatched_works", sa.Column("suggested_matches_json", sa.Text(), nullable=False, server_default="[]"))
    _add_column_if_missing("xr7_unmatched_works", sa.Column("suggested_resolution_actions_json", sa.Text(), nullable=False, server_default="[]"))
    _add_column_if_missing("xr7_unmatched_works", sa.Column("ai_resolution_confidence", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_unmatched_works", sa.Column("recovery_potential_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_unmatched_works", sa.Column("urgency_score", sa.Float(), nullable=False, server_default="0.0"))
    _add_column_if_missing("xr7_unmatched_works", sa.Column("sla_due_at", sa.DateTime(), nullable=True))

    if not _table_exists("xr7_catalog_valuation_snapshots"):
        op.create_table(
            "xr7_catalog_valuation_snapshots",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("as_of_date", sa.Date(), nullable=False),
            sa.Column("baseline_value", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("corrected_value", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("upside_value", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("confidence_interval_low", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("confidence_interval_high", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("assumptions_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_recovery_forecasts"):
        op.create_table(
            "xr7_recovery_forecasts",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("scope_type", sa.String(), nullable=False, server_default="artist"),
            sa.Column("scope_id", sa.String(), nullable=True),
            sa.Column("forecast_horizon_days", sa.Integer(), nullable=False, server_default="90"),
            sa.Column("forecast_amount", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("confidence_interval_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("model_version", sa.String(), nullable=False, server_default="v1"),
            sa.Column("feature_snapshot_ref", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_split_sheet_imports"):
        op.create_table(
            "xr7_split_sheet_imports",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("file_ref", sa.String(), nullable=False),
            sa.Column("import_status", sa.String(), nullable=False, server_default="pending"),
            sa.Column("conflicts_found", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("auto_resolved_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("manual_required_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("imported_by", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_ai_decision_audit_log"):
        op.create_table(
            "xr7_ai_decision_audit_log",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("decision_type", sa.String(), nullable=False),
            sa.Column("model_provider", sa.String(), nullable=False),
            sa.Column("model_version", sa.String(), nullable=False),
            sa.Column("prompt_hash", sa.String(), nullable=False),
            sa.Column("input_ref", sa.String(), nullable=True),
            sa.Column("output_ref", sa.String(), nullable=True),
            sa.Column("reviewer_id", sa.String(), nullable=True),
            sa.Column("override_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    for table in [
        "xr7_ai_decision_audit_log",
        "xr7_split_sheet_imports",
        "xr7_recovery_forecasts",
        "xr7_catalog_valuation_snapshots",
    ]:
        if _table_exists(table):
            op.drop_table(table)
