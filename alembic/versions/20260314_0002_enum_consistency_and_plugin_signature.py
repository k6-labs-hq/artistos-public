"""enum consistency and parser plugin signatures

Revision ID: 20260314_0002
Revises: 20260314_0001
Create Date: 2026-03-14 00:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260314_0002"
down_revision = "20260314_0001"
branch_labels = None
depends_on = None


def _dialect_name() -> str:
    bind = op.get_bind()
    return bind.dialect.name if bind is not None else ""


def upgrade() -> None:
    # Existing environments from 0001 need plugin_signature support.
    with op.batch_alter_table("parser_plugins") as batch:
        batch.add_column(sa.Column("plugin_signature", sa.String(), nullable=True))

    # Enforce consistent status/backends even on non-enum-friendly engines.
    with op.batch_alter_table("sync_jobs") as batch:
        batch.create_check_constraint(
            "ck_sync_jobs_status_values",
            "status IN ('PENDING','RUNNING','RETRYING','FAILED','COMPLETED')",
        )
        batch.create_check_constraint(
            "ck_sync_jobs_queue_backend_values",
            "queue_backend IN ('inline','background','celery')",
        )

    with op.batch_alter_table("oauth_connector_sessions") as batch:
        batch.create_check_constraint(
            "ck_oauth_connector_sessions_status_values",
            "status IN ('pending','exchanged','expired','cancelled')",
        )

    with op.batch_alter_table("connector_account_links") as batch:
        batch.create_check_constraint(
            "ck_connector_account_links_status_values",
            "status IN ('active','disconnected')",
        )

    # PostgreSQL enum type alignment.
    if _dialect_name() == "postgresql":
        op.execute("CREATE TYPE IF NOT EXISTS sync_job_status AS ENUM ('PENDING','RUNNING','RETRYING','FAILED','COMPLETED')")
        op.execute("CREATE TYPE IF NOT EXISTS sync_queue_backend AS ENUM ('inline','background','celery')")
        op.execute("ALTER TABLE sync_jobs ALTER COLUMN status TYPE sync_job_status USING status::sync_job_status")
        op.execute("ALTER TABLE sync_jobs ALTER COLUMN queue_backend TYPE sync_queue_backend USING queue_backend::sync_queue_backend")


def downgrade() -> None:
    if _dialect_name() == "postgresql":
        op.execute("ALTER TABLE sync_jobs ALTER COLUMN status TYPE VARCHAR USING status::text")
        op.execute("ALTER TABLE sync_jobs ALTER COLUMN queue_backend TYPE VARCHAR USING queue_backend::text")

    with op.batch_alter_table("connector_account_links") as batch:
        batch.drop_constraint("ck_connector_account_links_status_values", type_="check")

    with op.batch_alter_table("oauth_connector_sessions") as batch:
        batch.drop_constraint("ck_oauth_connector_sessions_status_values", type_="check")

    with op.batch_alter_table("sync_jobs") as batch:
        batch.drop_constraint("ck_sync_jobs_queue_backend_values", type_="check")
        batch.drop_constraint("ck_sync_jobs_status_values", type_="check")

    with op.batch_alter_table("parser_plugins") as batch:
        batch.drop_column("plugin_signature")
