"""Create payer_offices table and seed BMI's six regional offices.

BMI routes member dispute inquiries through regional Writer/Publisher
Relations offices, each with its own email + mailing address. Per the
BMI writer kit (form 3-2025) and the attorney-review brief at
docs/runbooks/bmi-dispute-attorney-brief.md, the offices are:
Nashville (default for our country/Americana cohort), New York,
Los Angeles, Atlanta, Austin, London.

Other PROs (ASCAP, MLC, SoundExchange) are intentionally NOT seeded
yet — their dispute mechanisms are materially different (portal-only,
non-geographic team routing, Letter of Direction-based authorization)
and the attorney briefs flag them as needing review before we wire
real submission targets. They'll get their own entries once the
attorney response lands.

Revision ID: 20260504_0038
Revises: 20260504_0037
Create Date: 2026-05-04
"""

from __future__ import annotations

import sys
import uuid
from datetime import date
from pathlib import Path

import sqlalchemy as sa

from alembic import op

# Make project root importable so the seed list lives in one place
# (the model module) and isn't duplicated here.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from XR7.models.payer_office import BMI_OFFICES_SEED  # noqa: E402

revision = "20260504_0038"
down_revision = "20260504_0037"
branch_labels = None
depends_on = None


_BMI_VERIFIED = date(2026, 5, 4)


def upgrade() -> None:
    op.create_table(
        "payer_offices",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("payer_id", sa.String(), nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("submission_email", sa.String(), nullable=False),
        sa.Column("mailing_address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_verified", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("payer_id", "name", name="uq_payer_offices_payer_name"),
    )

    bind = op.get_bind()
    payer_offices = sa.table(
        "payer_offices",
        sa.column("id", sa.String),
        sa.column("payer_id", sa.String),
        sa.column("name", sa.String),
        sa.column("submission_email", sa.String),
        sa.column("mailing_address", sa.Text),
        sa.column("phone", sa.String),
        sa.column("is_default", sa.Boolean),
        sa.column("last_verified", sa.Date),
        sa.column("notes", sa.Text),
    )

    rows = [
        {
            "id": str(uuid.uuid4()),
            "payer_id": "BMI",
            "name": office["name"],
            "submission_email": office["submission_email"],
            "mailing_address": office["mailing_address"],
            "phone": office["phone"],
            "is_default": office["is_default"],
            "last_verified": _BMI_VERIFIED,
            "notes": office["notes"],
        }
        for office in BMI_OFFICES_SEED
    ]
    bind.execute(payer_offices.insert(), rows)


def downgrade() -> None:
    op.drop_table("payer_offices")
