"""core domain baseline: artists, anomalies, claims

Revision ID: 20260314_0000
Revises:
Create Date: 2026-03-14 00:00:00

These three tables are the foundational domain entities referenced by every
subsequent migration.  They must exist before any alembic upgrade can
alter their schema.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260314_0000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── artists ───────────────────────────────────────────────────────────────
    op.create_table(
        "artists",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("ipi_number", sa.String(), nullable=True),
        sa.Column("stage_names", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="NEW"),
        sa.Column("onboarded_at", sa.DateTime(), nullable=True),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=False, server_default="US"),
        sa.Column("trolley_recipient_id", sa.String(), nullable=True),
        sa.Column("payout_account_status", sa.String(), nullable=False, server_default="not_started"),
        sa.Column("payout_method_type", sa.String(), nullable=True),
        sa.Column("payout_last4", sa.String(), nullable=True),
        sa.Column("tax_form_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("default_attorney_grace_period_days", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("primary_jurisdiction", sa.String(), nullable=False, server_default="USA"),
        sa.Column("preferred_contract_type", sa.String(), nullable=False, server_default="recording"),
        sa.Column("xr7_future_leakage_prevented", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_founder", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("founder_slot_number", sa.Integer(), nullable=True),
        sa.Column("founder_locked_at", sa.DateTime(), nullable=True),
        sa.Column("contingency_fee_percent", sa.Float(), nullable=True),
        sa.Column("primary_vertical", sa.String(), nullable=True),
        sa.Column("tvfilm_role", sa.String(), nullable=True),
        sa.Column("organization_type", sa.String(), nullable=True),
        sa.Column("enterprise_mode_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint(
            "(NOT is_founder) OR contingency_fee_percent <= 12",
            name="ck_artists_founder_fee_max",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artists_email", "artists", ["email"])
    op.create_index("ix_artists_status", "artists", ["status"])
    op.create_index("ix_artists_trolley_recipient_id", "artists", ["trolley_recipient_id"])
    op.create_index("ix_artists_founder_slot_number", "artists", ["founder_slot_number"])
    op.create_index("ix_artists_primary_vertical", "artists", ["primary_vertical"])
    op.create_index("ix_artists_tvfilm_role", "artists", ["tvfilm_role"])
    op.create_index("ix_artists_organization_type", "artists", ["organization_type"])

    # ── works ─────────────────────────────────────────────────────────────────
    op.create_table(
        "works",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("iswc", sa.String(), nullable=True),
        sa.Column("work_type", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── events ────────────────────────────────────────────────────────────────
    op.create_table(
        "events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("work_id", sa.String(), nullable=True),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("territory", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── anomalies ─────────────────────────────────────────────────────────────
    op.create_table(
        "anomalies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("subtype", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("expected_amount", sa.Float(), nullable=True),
        sa.Column("actual_amount", sa.Float(), nullable=True),
        sa.Column("estimated_recoverable", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("time_window_start", sa.DateTime(), nullable=True),
        sa.Column("time_window_end", sa.DateTime(), nullable=True),
        sa.Column("territory", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="OPEN"),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("anomaly_score", sa.Float(), nullable=True),
        sa.Column("model_version", sa.String(), nullable=True),
        sa.Column("feature_snapshot", sa.String(), nullable=True),
        sa.Column("recoverability_class", sa.String(), nullable=True),
        sa.Column("legal_basis", sa.String(), nullable=True),
        sa.Column("redistribution_risk_score", sa.Integer(), nullable=True),
        sa.Column("trust_score", sa.Float(), nullable=True),
        sa.Column("urgent_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── claims ────────────────────────────────────────────────────────────────
    # The claimstatus PostgreSQL enum is created here so that migration 0008
    # can safely ALTER TYPE claimstatus ADD VALUE IF NOT EXISTS …
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("""
            DO $$ BEGIN
                CREATE TYPE claimstatus AS ENUM (
                    'IDENTIFIED','PREPARED','FILED','SUBMITTED','PROOF_SUBMITTED',
                    'IN_REVIEW','ACCEPTED','FUNDS_RECEIVED','DISBURSEMENT_FAILED',
                    'PAID','CLOSED'
                );
            EXCEPTION WHEN duplicate_object THEN NULL;
            END $$;
        """)

    op.create_table(
        "claims",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("anomaly_id", sa.String(), nullable=False),
        sa.Column("claim_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="IDENTIFIED"),
        sa.Column("recovered_amount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
        sa.Column("contingency_fee", sa.Float(), nullable=True),
        sa.Column("platform_fee_percent", sa.Float(), nullable=False, server_default="12"),
        sa.Column("platform_fee_amount", sa.Float(), nullable=True),
        sa.Column("artist_net_amount", sa.Float(), nullable=True),
        sa.Column("remittance_method", sa.String(), nullable=True),
        sa.Column("remittance_reference_number", sa.String(), nullable=True),
        sa.Column("remittance_received_at", sa.DateTime(), nullable=True),
        sa.Column("trolley_payment_id", sa.String(), nullable=True),
        sa.Column("trolley_payment_status", sa.String(), nullable=True),
        sa.Column("trolley_fx_rate", sa.Float(), nullable=True),
        sa.Column("trolley_local_amount", sa.Float(), nullable=True),
        sa.Column("trolley_local_currency", sa.String(), nullable=True),
        sa.Column("payout_retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payout_failure_reason", sa.String(), nullable=True),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("payer_name", sa.String(), nullable=True),
        sa.Column("payer_contact", sa.String(), nullable=True),
        sa.Column("original_due_date", sa.DateTime(), nullable=True),
        sa.Column("proof_submitted_at", sa.DateTime(), nullable=True),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("sol_deadline", sa.DateTime(), nullable=True),
        sa.Column("governing_law_state", sa.String(), nullable=False, server_default="USA"),
        sa.Column("contract_type", sa.String(), nullable=False, server_default="recording"),
        sa.Column("infringement_date", sa.DateTime(), nullable=True),
        sa.Column("discovery_date", sa.DateTime(), nullable=True),
        sa.Column("sol_window_years", sa.Integer(), nullable=True),
        sa.Column("sol_citation_source", sa.String(), nullable=True),
        sa.Column("communications", sa.JSON(), nullable=True),
        sa.Column("anomaly_report", sa.JSON(), nullable=True),
        sa.Column("supporting_documents", sa.JSON(), nullable=True),
        sa.Column("attorney_file_generated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("attorney_file_generated_at", sa.DateTime(), nullable=True),
        sa.Column("trust_score", sa.Float(), nullable=True),
        sa.Column("attorney_review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("legal_defensibility_report", sa.JSON(), nullable=True),
        sa.Column("claim_strength_rating", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
        sa.ForeignKeyConstraint(["anomaly_id"], ["anomalies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_claims_trolley_payment_id", "claims", ["trolley_payment_id"])


def downgrade() -> None:
    op.drop_index("ix_claims_trolley_payment_id", table_name="claims")
    op.drop_table("claims")
    op.drop_table("anomalies")
    op.drop_table("events")
    op.drop_table("works")
    op.drop_index("ix_artists_organization_type", table_name="artists")
    op.drop_index("ix_artists_tvfilm_role", table_name="artists")
    op.drop_index("ix_artists_primary_vertical", table_name="artists")
    op.drop_index("ix_artists_founder_slot_number", table_name="artists")
    op.drop_index("ix_artists_trolley_recipient_id", table_name="artists")
    op.drop_index("ix_artists_status", table_name="artists")
    op.drop_index("ix_artists_email", table_name="artists")
    op.drop_table("artists")
