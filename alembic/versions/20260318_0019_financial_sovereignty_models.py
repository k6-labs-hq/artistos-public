"""financial sovereignty models

Revision ID: 20260318_0019
Revises: 20260317_0018
Create Date: 2026-03-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260318_0019"
down_revision = "20260317_0018"
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
    if not _table_exists("trust_trace_events"):
        op.create_table(
            "trust_trace_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("run_id", sa.String(), nullable=False),
            sa.Column("stage", sa.String(), nullable=False),
            sa.Column("sub_stage", sa.String(), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.Column("explanation", sa.Text(), nullable=True),
            sa.Column("eta_seconds", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_trust_trace_events_artist_id", "trust_trace_events", ["artist_id"])
        op.create_index("ix_trust_trace_events_run_id", "trust_trace_events", ["run_id"])

    if not _table_exists("artist_referrals"):
        op.create_table(
            "artist_referrals",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("referrer_artist_id", sa.String(), nullable=False),
            sa.Column("referred_artist_id", sa.String(), nullable=False),
            sa.Column("referral_fee_pct", sa.Float(), nullable=False, server_default="5.0"),
            sa.Column("lifetime_earned", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["referrer_artist_id"], ["artists.id"]),
            sa.ForeignKeyConstraint(["referred_artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_artist_referrals_referrer_artist_id", "artist_referrals", ["referrer_artist_id"])
        op.create_index("ix_artist_referrals_referred_artist_id", "artist_referrals", ["referred_artist_id"])

    if not _table_exists("recoverable_liquidity_advances"):
        op.create_table(
            "recoverable_liquidity_advances",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("offered_amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("predicted_low_forecast", sa.Float(), nullable=False),
            sa.Column("advance_fee_pct", sa.Float(), nullable=False, server_default="3.0"),
            sa.Column(
                "status",
                sa.Enum(
                    "OFFERED",
                    "ACCEPTED",
                    "DISBURSED",
                    "REPAID",
                    "DECLINED",
                    "EXPIRED",
                    name="advancestatus",
                ),
                nullable=False,
                server_default="OFFERED",
            ),
            sa.Column("trolley_payment_id", sa.String(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("offered_at", sa.DateTime(), nullable=False),
            sa.Column("accepted_at", sa.DateTime(), nullable=True),
            sa.Column("disbursed_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_recoverable_liquidity_advances_artist_id",
            "recoverable_liquidity_advances",
            ["artist_id"],
        )

    if not _table_exists("rights_scan_results"):
        op.create_table(
            "rights_scan_results",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("work_id", sa.String(), nullable=True),
            sa.Column("gap_type", sa.String(), nullable=False),
            sa.Column("territory", sa.String(), nullable=True),
            sa.Column("registration_packet", sa.JSON(), nullable=True),
            sa.Column("submission_status", sa.String(), nullable=False, server_default="pending"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("scanned_at", sa.DateTime(), nullable=False),
            sa.Column("submitted_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_rights_scan_results_artist_id", "rights_scan_results", ["artist_id"])
        op.create_index("ix_rights_scan_results_work_id", "rights_scan_results", ["work_id"])

    if not _table_exists("artist_messages"):
        op.create_table(
            "artist_messages",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column(
                "category",
                sa.Enum(
                    "onboarding",
                    "comfort",
                    "claim",
                    "sol_alert",
                    "deposit",
                    "recovery",
                    "weekly_story",
                    "system",
                    name="messagecategory",
                ),
                nullable=False,
                server_default="system",
            ),
            sa.Column("subject", sa.String(), nullable=True),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_artist_messages_artist_id", "artist_messages", ["artist_id"])

    if not _table_exists("class_action_signals"):
        op.create_table(
            "class_action_signals",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("payer_name", sa.String(), nullable=False),
            sa.Column("anomaly_type", sa.String(), nullable=False),
            sa.Column("affected_artist_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("total_estimated_loss", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("contributing_artist_ids", sa.JSON(), nullable=True),
            sa.Column("packet_url", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="active"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("first_detected_at", sa.DateTime(), nullable=False),
            sa.Column("last_updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_class_action_signals_payer_name", "class_action_signals", ["payer_name"])


def downgrade() -> None:
    if _table_exists("class_action_signals"):
        op.drop_index("ix_class_action_signals_payer_name", table_name="class_action_signals")
        op.drop_table("class_action_signals")

    if _table_exists("artist_messages"):
        op.drop_index("ix_artist_messages_artist_id", table_name="artist_messages")
        op.drop_table("artist_messages")

    if _table_exists("rights_scan_results"):
        op.drop_index("ix_rights_scan_results_work_id", table_name="rights_scan_results")
        op.drop_index("ix_rights_scan_results_artist_id", table_name="rights_scan_results")
        op.drop_table("rights_scan_results")

    if _table_exists("recoverable_liquidity_advances"):
        op.drop_index(
            "ix_recoverable_liquidity_advances_artist_id",
            table_name="recoverable_liquidity_advances",
        )
        op.drop_table("recoverable_liquidity_advances")

    if _table_exists("artist_referrals"):
        op.drop_index("ix_artist_referrals_referred_artist_id", table_name="artist_referrals")
        op.drop_index("ix_artist_referrals_referrer_artist_id", table_name="artist_referrals")
        op.drop_table("artist_referrals")

    if _table_exists("trust_trace_events"):
        op.drop_index("ix_trust_trace_events_run_id", table_name="trust_trace_events")
        op.drop_index("ix_trust_trace_events_artist_id", table_name="trust_trace_events")
        op.drop_table("trust_trace_events")
