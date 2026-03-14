"""ml feedback core, model registry, segmentation, and crm fields

Revision ID: 20260314_0005
Revises: 20260314_0004
Create Date: 2026-03-14 03:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260314_0005"
down_revision = "20260314_0004"
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
    if not _column_exists("artists", "email"):
        op.add_column("artists", sa.Column("email", sa.String(), nullable=True))
        op.create_index("ix_artists_email", "artists", ["email"])
    if not _column_exists("artists", "role"):
        op.add_column("artists", sa.Column("role", sa.String(), nullable=True))

    if not _column_exists("anomalies", "anomaly_score"):
        op.add_column("anomalies", sa.Column("anomaly_score", sa.Float(), nullable=True))
    if not _column_exists("anomalies", "model_version"):
        op.add_column("anomalies", sa.Column("model_version", sa.String(), nullable=True))
    if not _column_exists("anomalies", "feature_snapshot"):
        op.add_column("anomalies", sa.Column("feature_snapshot", sa.String(), nullable=True))

    if not _table_exists("ml_feedback_events"):
        op.create_table(
            "ml_feedback_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("feedback_type", sa.String(), nullable=False),
            sa.Column("source_type", sa.String(), nullable=True),
            sa.Column("source_id", sa.String(), nullable=True),
            sa.Column("anomaly_id", sa.String(), nullable=True),
            sa.Column("claim_id", sa.String(), nullable=True),
            sa.Column("subtype", sa.String(), nullable=True),
            sa.Column("category", sa.String(), nullable=True),
            sa.Column("artist_profile_segment", sa.String(), nullable=True),
            sa.Column("model_version", sa.String(), nullable=True),
            sa.Column("model_prediction", sa.Float(), nullable=True),
            sa.Column("human_decision", sa.String(), nullable=True),
            sa.Column("outcome", sa.String(), nullable=True),
            sa.Column("estimated_amount", sa.Float(), nullable=True),
            sa.Column("actual_amount", sa.Float(), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ml_feedback_events_artist_id", "ml_feedback_events", ["artist_id"])
        op.create_index("ix_ml_feedback_events_feedback_type", "ml_feedback_events", ["feedback_type"])
        op.create_index("ix_ml_feedback_events_source_type", "ml_feedback_events", ["source_type"])
        op.create_index("ix_ml_feedback_events_source_id", "ml_feedback_events", ["source_id"])
        op.create_index("ix_ml_feedback_events_anomaly_id", "ml_feedback_events", ["anomaly_id"])
        op.create_index("ix_ml_feedback_events_claim_id", "ml_feedback_events", ["claim_id"])
        op.create_index("ix_ml_feedback_events_subtype", "ml_feedback_events", ["subtype"])
        op.create_index("ix_ml_feedback_events_category", "ml_feedback_events", ["category"])
        op.create_index("ix_ml_feedback_events_artist_profile_segment", "ml_feedback_events", ["artist_profile_segment"])
        op.create_index("ix_ml_feedback_events_created_at", "ml_feedback_events", ["created_at"])

    if not _table_exists("ml_calibration_snapshots"):
        op.create_table(
            "ml_calibration_snapshots",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("scope_type", sa.String(), nullable=False),
            sa.Column("scope_key", sa.String(), nullable=False),
            sa.Column("alpha", sa.Float(), nullable=False),
            sa.Column("beta", sa.Float(), nullable=False),
            sa.Column("sample_count", sa.Integer(), nullable=False),
            sa.Column("success_count", sa.Integer(), nullable=False),
            sa.Column("failure_count", sa.Integer(), nullable=False),
            sa.Column("posterior_mean", sa.Float(), nullable=False),
            sa.Column("lower_credible", sa.Float(), nullable=False),
            sa.Column("upper_credible", sa.Float(), nullable=False),
            sa.Column("last_updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ml_calibration_snapshots_artist_id", "ml_calibration_snapshots", ["artist_id"])
        op.create_index("ix_ml_calibration_snapshots_scope_type", "ml_calibration_snapshots", ["scope_type"])
        op.create_index("ix_ml_calibration_snapshots_scope_key", "ml_calibration_snapshots", ["scope_key"])
        op.create_index("ix_ml_calibration_snapshots_last_updated_at", "ml_calibration_snapshots", ["last_updated_at"])

    if not _table_exists("ml_model_registry"):
        op.create_table(
            "ml_model_registry",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("model_family", sa.String(), nullable=False),
            sa.Column("model_version", sa.String(), nullable=False),
            sa.Column("training_snapshot_ref", sa.String(), nullable=True),
            sa.Column("metrics", sa.JSON(), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ml_model_registry_model_family", "ml_model_registry", ["model_family"])
        op.create_index("ix_ml_model_registry_model_version", "ml_model_registry", ["model_version"])
        op.create_index("ix_ml_model_registry_created_at", "ml_model_registry", ["created_at"])

    if not _table_exists("catalog_segments"):
        op.create_table(
            "catalog_segments",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("segment_name", sa.String(), nullable=False),
            sa.Column("score", sa.Float(), nullable=False),
            sa.Column("features", sa.JSON(), nullable=True),
            sa.Column("generated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_catalog_segments_artist_id", "catalog_segments", ["artist_id"])
        op.create_index("ix_catalog_segments_segment_name", "catalog_segments", ["segment_name"])
        op.create_index("ix_catalog_segments_generated_at", "catalog_segments", ["generated_at"])


def downgrade() -> None:
    if _table_exists("catalog_segments"):
        op.drop_index("ix_catalog_segments_generated_at", table_name="catalog_segments")
        op.drop_index("ix_catalog_segments_segment_name", table_name="catalog_segments")
        op.drop_index("ix_catalog_segments_artist_id", table_name="catalog_segments")
        op.drop_table("catalog_segments")

    if _table_exists("ml_model_registry"):
        op.drop_index("ix_ml_model_registry_created_at", table_name="ml_model_registry")
        op.drop_index("ix_ml_model_registry_model_version", table_name="ml_model_registry")
        op.drop_index("ix_ml_model_registry_model_family", table_name="ml_model_registry")
        op.drop_table("ml_model_registry")

    if _table_exists("ml_calibration_snapshots"):
        op.drop_index("ix_ml_calibration_snapshots_last_updated_at", table_name="ml_calibration_snapshots")
        op.drop_index("ix_ml_calibration_snapshots_scope_key", table_name="ml_calibration_snapshots")
        op.drop_index("ix_ml_calibration_snapshots_scope_type", table_name="ml_calibration_snapshots")
        op.drop_index("ix_ml_calibration_snapshots_artist_id", table_name="ml_calibration_snapshots")
        op.drop_table("ml_calibration_snapshots")

    if _table_exists("ml_feedback_events"):
        op.drop_index("ix_ml_feedback_events_created_at", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_artist_profile_segment", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_category", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_subtype", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_claim_id", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_anomaly_id", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_source_id", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_source_type", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_feedback_type", table_name="ml_feedback_events")
        op.drop_index("ix_ml_feedback_events_artist_id", table_name="ml_feedback_events")
        op.drop_table("ml_feedback_events")

    if _column_exists("anomalies", "feature_snapshot"):
        op.drop_column("anomalies", "feature_snapshot")
    if _column_exists("anomalies", "model_version"):
        op.drop_column("anomalies", "model_version")
    if _column_exists("anomalies", "anomaly_score"):
        op.drop_column("anomalies", "anomaly_score")

    if _column_exists("artists", "role"):
        op.drop_column("artists", "role")
    if _column_exists("artists", "email"):
        op.drop_index("ix_artists_email", table_name="artists")
        op.drop_column("artists", "email")
