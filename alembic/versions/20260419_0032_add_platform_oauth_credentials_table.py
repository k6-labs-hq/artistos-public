"""Add platform_oauth_credentials table for OAuth connector feature.

Feature #7: Semi-automated pull fallbacks

Create table for storing OAuth tokens with encryption:
- Spotify for Artists API
- YouTube Analytics API
- SoundCloud API (where available)

Security features:
- Encrypted access/refresh tokens (at rest)
- Token rotation on refresh
- Artist-scoped credentials

Revision ID: 20260419_0032
Revises: 20260419_0031
Create Date: 2026-04-19
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260419_0032"
down_revision = "20260419_0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create platform_oauth_credentials table."""
    
    op.create_table(
        "platform_oauth_credentials",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("scopes", sa.String(), nullable=False, server_default="[]"),
        sa.Column(
            "status",
            sa.Enum("active", "expired", "revoked", "error", name="platformoauthstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create composite index on artist_id + platform for efficient lookups
    op.create_index(
        "ix_platform_oauth_credentials_artist_platform",
        "platform_oauth_credentials",
        ["artist_id", "platform"],
    )
    
    # Create index on artist_id for filtering by artist
    op.create_index(
        "ix_platform_oauth_credentials_artist_id",
        "platform_oauth_credentials",
        ["artist_id"],
    )
    
    # Create index on platform for admin visibility
    op.create_index(
        "ix_platform_oauth_credentials_platform",
        "platform_oauth_credentials",
        ["platform"],
    )


def downgrade() -> None:
    """Drop platform_oauth_credentials table."""
    
    op.drop_index("ix_platform_oauth_credentials_platform", table_name="platform_oauth_credentials")
    op.drop_index("ix_platform_oauth_credentials_artist_id", table_name="platform_oauth_credentials")
    op.drop_index("ix_platform_oauth_credentials_artist_platform", table_name="platform_oauth_credentials")
    op.drop_table("platform_oauth_credentials")
    
    # Drop enum type (PostgreSQL-specific)
    op.execute("DROP TYPE IF EXISTS platformoauthstatus")
