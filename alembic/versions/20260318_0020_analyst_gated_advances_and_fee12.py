"""analyst gated advances and fee 12 defaults

Revision ID: 20260318_0020
Revises: 20260318_0019
Create Date: 2026-03-18
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260318_0020"
down_revision = "20260318_0019"
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
    return any(str(c.get("name")) == column_name for c in cols)


def upgrade() -> None:
    if _table_exists("platform_config") and _column_exists("platform_config", "founder_fee_percent"):
        op.execute("UPDATE platform_config SET founder_fee_percent = 12.0 WHERE founder_fee_percent = 10.0")

    if _table_exists("claims") and _column_exists("claims", "platform_fee_percent"):
        op.execute("UPDATE claims SET platform_fee_percent = 12.0 WHERE platform_fee_percent = 10.0")

    if _table_exists("artists") and _column_exists("artists", "contingency_fee_percent"):
        op.execute(
            "UPDATE artists SET contingency_fee_percent = 12.0 "
            "WHERE is_founder IS TRUE AND contingency_fee_percent IS NOT NULL AND contingency_fee_percent > 12.0"
        )

    if not _table_exists("advance_opportunities"):
        op.create_table(
            "advance_opportunities",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("anomaly_id", sa.String(), nullable=True),
            sa.Column("claim_id", sa.String(), nullable=True),
            sa.Column(
                "status",
                sa.Enum(
                    "QUEUED_ANALYST",
                    "ANALYST_APPROVED",
                    "ANALYST_REJECTED",
                    "QUEUED_EXEC",
                    "EXEC_APPROVED",
                    "EXEC_REJECTED",
                    "OFFER_GENERATED",
                    "EXPIRED",
                    name="advanceopportunitystatus",
                ),
                nullable=False,
                server_default="QUEUED_ANALYST",
            ),
            sa.Column("model_score", sa.Float(), nullable=False),
            sa.Column("ensemble_scores", sa.JSON(), nullable=False),
            sa.Column("predicted_recovery_amount", sa.Float(), nullable=False),
            sa.Column("max_advance_amount", sa.Float(), nullable=False),
            sa.Column("proposed_advance_fee_percent", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("analyst_notes", sa.Text(), nullable=True),
            sa.Column("executive_notes", sa.Text(), nullable=True),
            sa.Column("source_snapshot", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.ForeignKeyConstraint(["anomaly_id"], ["anomalies.id"]),
            sa.ForeignKeyConstraint(["claim_id"], ["claims.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_advance_opportunities_artist_id", "advance_opportunities", ["artist_id"])
        op.create_index("ix_advance_opportunities_anomaly_id", "advance_opportunities", ["anomaly_id"])
        op.create_index("ix_advance_opportunities_claim_id", "advance_opportunities", ["claim_id"])
        op.create_index("ix_advance_opportunities_status", "advance_opportunities", ["status"])

    if not _table_exists("advance_approvals"):
        op.create_table(
            "advance_approvals",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("opportunity_id", sa.String(), nullable=False),
            sa.Column("stage", sa.Enum("ANALYST", "EXECUTIVE", name="approvalstage"), nullable=False),
            sa.Column("decision", sa.Enum("APPROVED", "REJECTED", name="approvaldecision"), nullable=False),
            sa.Column("actor_subject", sa.String(), nullable=False),
            sa.Column("actor_role", sa.String(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["opportunity_id"], ["advance_opportunities.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_advance_approvals_opportunity_id", "advance_approvals", ["opportunity_id"])

    if not _table_exists("advance_offers"):
        op.create_table(
            "advance_offers",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("opportunity_id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("liquidity_advance_id", sa.String(), nullable=True),
            sa.Column("offered_amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("advance_fee_percent", sa.Float(), nullable=False),
            sa.Column("effective_total_fee_cap_percent", sa.Float(), nullable=False),
            sa.Column("visible_to_artist", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column(
                "status",
                sa.Enum(
                    "PENDING_ARTIST",
                    "ACCEPTED",
                    "DECLINED",
                    "EXPIRED",
                    "FAILED",
                    name="advanceofferstatus",
                ),
                nullable=False,
                server_default="PENDING_ARTIST",
            ),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["opportunity_id"], ["advance_opportunities.id"]),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.ForeignKeyConstraint(["liquidity_advance_id"], ["recoverable_liquidity_advances.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_advance_offers_opportunity_id", "advance_offers", ["opportunity_id"])
        op.create_index("ix_advance_offers_artist_id", "advance_offers", ["artist_id"])
        op.create_index("ix_advance_offers_liquidity_advance_id", "advance_offers", ["liquidity_advance_id"])
        op.create_index("ix_advance_offers_status", "advance_offers", ["status"])

    if not _table_exists("advance_recovery_packets"):
        op.create_table(
            "advance_recovery_packets",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("offer_id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("chain_of_custody", sa.JSON(), nullable=False),
            sa.Column("required_signers", sa.JSON(), nullable=False),
            sa.Column("collected_signatures", sa.JSON(), nullable=False),
            sa.Column("legal_basis", sa.JSON(), nullable=False),
            sa.Column("failure_reason", sa.Text(), nullable=False),
            sa.Column("immutable_ledger_hash", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="READY"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["offer_id"], ["advance_offers.id"]),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_advance_recovery_packets_offer_id", "advance_recovery_packets", ["offer_id"])
        op.create_index("ix_advance_recovery_packets_artist_id", "advance_recovery_packets", ["artist_id"])


def downgrade() -> None:
    if _table_exists("advance_recovery_packets"):
        op.drop_index("ix_advance_recovery_packets_artist_id", table_name="advance_recovery_packets")
        op.drop_index("ix_advance_recovery_packets_offer_id", table_name="advance_recovery_packets")
        op.drop_table("advance_recovery_packets")

    if _table_exists("advance_offers"):
        op.drop_index("ix_advance_offers_status", table_name="advance_offers")
        op.drop_index("ix_advance_offers_liquidity_advance_id", table_name="advance_offers")
        op.drop_index("ix_advance_offers_artist_id", table_name="advance_offers")
        op.drop_index("ix_advance_offers_opportunity_id", table_name="advance_offers")
        op.drop_table("advance_offers")

    if _table_exists("advance_approvals"):
        op.drop_index("ix_advance_approvals_opportunity_id", table_name="advance_approvals")
        op.drop_table("advance_approvals")

    if _table_exists("advance_opportunities"):
        op.drop_index("ix_advance_opportunities_status", table_name="advance_opportunities")
        op.drop_index("ix_advance_opportunities_claim_id", table_name="advance_opportunities")
        op.drop_index("ix_advance_opportunities_anomaly_id", table_name="advance_opportunities")
        op.drop_index("ix_advance_opportunities_artist_id", table_name="advance_opportunities")
        op.drop_table("advance_opportunities")
