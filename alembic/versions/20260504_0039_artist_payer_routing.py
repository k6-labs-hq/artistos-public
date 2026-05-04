"""Add pro_affiliations + bmi_office_name to artists.

Drives dispute filing routing. `pro_affiliations` is a JSON list of
canonical payer ids the artist receives statements from
(e.g. ["BMI", "MLC"]). `bmi_office_name` matches `payer_offices.name`
when "BMI" is in the affiliations list. Both nullable — null means
"artist hasn't completed payer selection at onboarding yet" and
filing falls back to the default BMI office (Nashville).

Revision ID: 20260504_0039
Revises: 20260504_0038
Create Date: 2026-05-04
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260504_0039"
down_revision = "20260504_0038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("artists", sa.Column("pro_affiliations", sa.JSON(), nullable=True))
    op.add_column("artists", sa.Column("bmi_office_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("artists", "bmi_office_name")
    op.drop_column("artists", "pro_affiliations")
