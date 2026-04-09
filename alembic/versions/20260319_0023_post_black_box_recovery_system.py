"""Post black-box recovery system schema extensions.

Revision ID: 20260319_0023
Revises: 20260319_0022
Create Date: 2026-03-19
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260319_0023"
down_revision = "20260319_0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "anomalies" in table_names:
        cols = {c["name"] for c in inspector.get_columns("anomalies")}
        if "recoverability_class" not in cols:
            op.add_column("anomalies", sa.Column("recoverability_class", sa.String(), nullable=True))
        if "legal_basis" not in cols:
            op.add_column("anomalies", sa.Column("legal_basis", sa.String(), nullable=True))
        if "redistribution_risk_score" not in cols:
            op.add_column("anomalies", sa.Column("redistribution_risk_score", sa.Integer(), nullable=True))
        if "trust_score" not in cols:
            op.add_column("anomalies", sa.Column("trust_score", sa.Float(), nullable=True))
        if "urgent_flag" not in cols:
            op.add_column("anomalies", sa.Column("urgent_flag", sa.Boolean(), nullable=False, server_default=sa.false()))

    if "claims" in table_names:
        cols = {c["name"] for c in inspector.get_columns("claims")}
        if "trust_score" not in cols:
            op.add_column("claims", sa.Column("trust_score", sa.Float(), nullable=True))
        if "attorney_review_required" not in cols:
            op.add_column("claims", sa.Column("attorney_review_required", sa.Boolean(), nullable=False, server_default=sa.false()))
        if "legal_defensibility_report" not in cols:
            op.add_column("claims", sa.Column("legal_defensibility_report", sa.JSON(), nullable=True))
        if "claim_strength_rating" not in cols:
            op.add_column("claims", sa.Column("claim_strength_rating", sa.String(), nullable=True))

    if "legal_defensibility_events" not in table_names:
        op.create_table(
            "legal_defensibility_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("anomaly_id", sa.String(), nullable=True),
            sa.Column("claim_id", sa.String(), nullable=True),
            sa.Column("model_version", sa.String(), nullable=True),
            sa.Column("rule_version", sa.String(), nullable=True),
            sa.Column("agent_id", sa.String(), nullable=True),
            sa.Column("confidence_score", sa.Float(), nullable=True),
            sa.Column("human_review_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("input_hash", sa.String(), nullable=True),
            sa.Column("payload_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_legal_defensibility_events_artist_id", "legal_defensibility_events", ["artist_id"], unique=False)

    if "society_signal_logs" not in table_names:
        op.create_table(
            "society_signal_logs",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("source", sa.String(), nullable=False),
            sa.Column("signal_type", sa.String(), nullable=False),
            sa.Column("payer_or_society", sa.String(), nullable=False),
            sa.Column("affected_anomaly_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("classification_impact_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_society_signal_logs_payer_or_society", "society_signal_logs", ["payer_or_society"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "society_signal_logs" in table_names:
        idx = {i["name"] for i in inspector.get_indexes("society_signal_logs")}
        if "ix_society_signal_logs_payer_or_society" in idx:
            op.drop_index("ix_society_signal_logs_payer_or_society", table_name="society_signal_logs")
        op.drop_table("society_signal_logs")

    if "legal_defensibility_events" in table_names:
        idx = {i["name"] for i in inspector.get_indexes("legal_defensibility_events")}
        if "ix_legal_defensibility_events_artist_id" in idx:
            op.drop_index("ix_legal_defensibility_events_artist_id", table_name="legal_defensibility_events")
        op.drop_table("legal_defensibility_events")

    if "claims" in table_names:
        cols = {c["name"] for c in inspector.get_columns("claims")}
        if "claim_strength_rating" in cols:
            op.drop_column("claims", "claim_strength_rating")
        if "legal_defensibility_report" in cols:
            op.drop_column("claims", "legal_defensibility_report")
        if "attorney_review_required" in cols:
            op.drop_column("claims", "attorney_review_required")
        if "trust_score" in cols:
            op.drop_column("claims", "trust_score")

    if "anomalies" in table_names:
        cols = {c["name"] for c in inspector.get_columns("anomalies")}
        if "urgent_flag" in cols:
            op.drop_column("anomalies", "urgent_flag")
        if "trust_score" in cols:
            op.drop_column("anomalies", "trust_score")
        if "redistribution_risk_score" in cols:
            op.drop_column("anomalies", "redistribution_risk_score")
        if "legal_basis" in cols:
            op.drop_column("anomalies", "legal_basis")
        if "recoverability_class" in cols:
            op.drop_column("anomalies", "recoverability_class")
