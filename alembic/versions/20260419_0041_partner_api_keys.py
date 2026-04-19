"""Add partner_api_keys table for API ecosystem lifecycle management.

Revision ID: 20260419_0041
Revises: 20260419_0040
Create Date: 2026-04-19 15:00:00.000000

Enables partner integrations with full API key lifecycle: generation, rotation,
scoped permissions, tiered rate limits, usage tracking, and revocation.

Supports sandbox (100 req/hr) and production (10000 req/hr) tiers for partners
integrating with XR7 APIs.

Closes: XR7-404
Domain: api-ecosystem
Scale-target: Partner-facing API ecosystem with full lifecycle governance
Compliance: SOC 2 CC6.1 — Logical access controls
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260419_0041"
down_revision = "20260419_0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create partner_api_keys table."""
    op.create_table(
        "partner_api_keys",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("partner_id", sa.String(), nullable=False),
        sa.Column("key_hash", sa.String(), nullable=False),  # bcrypt hash
        sa.Column("key_prefix", sa.String(), nullable=False),  # xr7_live_abc... for identification
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "tier",
            sa.String(),
            nullable=False,
            server_default="sandbox",
        ),  # sandbox|production
        sa.Column("rate_limit_per_hour", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_reason", sa.String(), nullable=True),
        sa.Column("usage_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id", name="pk_partner_api_keys"),
    )

    # Indexes for performance
    op.create_index("ix_partner_api_keys_partner_id", "partner_api_keys", ["partner_id"])
    op.create_index(
        "ix_partner_api_keys_key_prefix", "partner_api_keys", ["key_prefix"], unique=True
    )
    op.create_index(
        "ix_partner_api_keys_active",
        "partner_api_keys",
        ["partner_id", "revoked_at"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def downgrade() -> None:
    """Drop partner_api_keys table."""
    op.drop_index("ix_partner_api_keys_active", table_name="partner_api_keys")
    op.drop_index("ix_partner_api_keys_key_prefix", table_name="partner_api_keys")
    op.drop_index("ix_partner_api_keys_partner_id", table_name="partner_api_keys")
    op.drop_table("partner_api_keys")
