"""Add unique constraint on events table for ingestion ON CONFLICT dedup.

XR7/api/routers/ingestion.py calls INSERT ... ON CONFLICT DO NOTHING using
index_elements=[artist_id, event_type, platform, territory, timestamp, quantity,
unit_value] to skip duplicate rows on re-upload. Postgres requires a unique
constraint on those columns for the ON CONFLICT target to be valid.

Revision ID: 20260422_0035
Revises: 20260422_0034
Create Date: 2026-04-22
"""

from sqlalchemy import inspect

from alembic import op

revision = "20260422_0035"
down_revision = "20260422_0034"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "uq_events_dedup"
INDEX_COLUMNS = [
    "artist_id",
    "event_type",
    "platform",
    "territory",
    "timestamp",
    "quantity",
    "unit_value",
]


def _constraint_exists(table: str, name: str) -> bool:
    try:
        uqs = inspect(op.get_bind()).get_unique_constraints(table)
        return any(u.get("name") == name for u in uqs)
    except Exception:
        return False


def upgrade() -> None:
    if not _constraint_exists("events", CONSTRAINT_NAME):
        # Plain unique constraint — matches SQLAlchemy's
        # on_conflict_do_nothing(index_elements=[...]) target.
        # NB: Postgres treats NULLs as distinct by default. Re-upload dedup
        # only works when platform + territory are populated, which they
        # always are for real DSP statements.
        op.create_unique_constraint(
            CONSTRAINT_NAME,
            "events",
            INDEX_COLUMNS,
        )


def downgrade() -> None:
    if _constraint_exists("events", CONSTRAINT_NAME):
        op.drop_constraint(CONSTRAINT_NAME, "events", type_="unique")
