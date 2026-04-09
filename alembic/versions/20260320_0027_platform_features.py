"""Platform features: notification log, case rooms, data residency,
connector reliability, SLO, batch ingestion.

Revision ID: 20260320_0027_platform_features
Revises: 20260319_0026_vip_founders_circle
Create Date: 2026-03-20 10:00:00.000000

New tables:
  notification_delivery_logs  — per-channel delivery audit trail
  case_rooms                  — collaborative workspaces per claim
  case_room_members           — membership + role per room
  case_comments               — threaded comments inside a room
  case_attachments            — file attachments with role-gating
  case_approvals              — approval workflow per room
  data_residency_policies     — per-org data region enforcement
  connector_sync_cursors      — resume-cursor per artist/integration
  webhook_events              — raw inbound webhook inbox + DLQ
  slo_metrics                 — SLO definitions + measurements
  tenant_cost_ledger          — per-period cost telemetry
  batch_ingestion_jobs        — multi-file upload jobs
  batch_ingestion_files       — per-file progress within a job
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260320_0027"
down_revision = "20260319_0026"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _index_exists(table: str, index: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return any(i.get("name") == index for i in insp.get_indexes(table))
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    # ------------------------------------------------------------------
    # notification_delivery_logs
    # ------------------------------------------------------------------
    if not _table_exists("notification_delivery_logs"):
        op.create_table(
            "notification_delivery_logs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("event_key", sa.String(128), nullable=False),
            sa.Column("channel", sa.String(32), nullable=False),
            sa.Column("recipient", sa.String(255), nullable=True),
            sa.Column("sent", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("skip_reason", sa.String(128), nullable=True),
            sa.Column("rendered_title", sa.Text(), nullable=True),
            sa.Column("rendered_body", sa.Text(), nullable=True),
            sa.Column("org_id", sa.String(36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_ndl_artist_id", "notification_delivery_logs", ["artist_id"]
        )
        op.create_index(
            "ix_ndl_event_key", "notification_delivery_logs", ["event_key"]
        )

    # ------------------------------------------------------------------
    # case_rooms
    # ------------------------------------------------------------------
    if not _table_exists("case_rooms"):
        op.create_table(
            "case_rooms",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("claim_id", sa.String(36), nullable=True),
            sa.Column("org_id", sa.String(36), nullable=True),
            sa.Column("title", sa.String(512), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="open"),
            sa.Column("created_by_email", sa.String(255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_case_rooms_artist_id", "case_rooms", ["artist_id"])
        op.create_index("ix_case_rooms_status", "case_rooms", ["status"])

    # ------------------------------------------------------------------
    # case_room_members
    # ------------------------------------------------------------------
    if not _table_exists("case_room_members"):
        op.create_table(
            "case_room_members",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("room_id", sa.String(36), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("role", sa.String(32), nullable=False, server_default="viewer"),
            sa.Column("added_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_crm_room_id", "case_room_members", ["room_id"])

    # ------------------------------------------------------------------
    # case_comments
    # ------------------------------------------------------------------
    if not _table_exists("case_comments"):
        op.create_table(
            "case_comments",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("room_id", sa.String(36), nullable=False),
            sa.Column("author_email", sa.String(255), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("edited", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_cc_room_id", "case_comments", ["room_id"])

    # ------------------------------------------------------------------
    # case_attachments
    # ------------------------------------------------------------------
    if not _table_exists("case_attachments"):
        op.create_table(
            "case_attachments",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("room_id", sa.String(36), nullable=False),
            sa.Column("uploaded_by_email", sa.String(255), nullable=False),
            sa.Column("filename", sa.String(512), nullable=False),
            sa.Column("storage_uri", sa.Text(), nullable=False),
            sa.Column("content_type", sa.String(128), nullable=True),
            sa.Column("size_bytes", sa.Integer(), nullable=True),
            # Minimum role required to access this attachment
            sa.Column("min_role_required", sa.String(32), nullable=False, server_default="viewer"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_ca_room_id", "case_attachments", ["room_id"])

    # ------------------------------------------------------------------
    # case_approvals
    # ------------------------------------------------------------------
    if not _table_exists("case_approvals"):
        op.create_table(
            "case_approvals",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("room_id", sa.String(36), nullable=False),
            sa.Column("requested_by_email", sa.String(255), nullable=False),
            sa.Column("approver_email", sa.String(255), nullable=True),
            sa.Column("decision", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("due_at", sa.DateTime(), nullable=True),
            sa.Column("decided_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_cappr_room_id", "case_approvals", ["room_id"])

    # ------------------------------------------------------------------
    # data_residency_policies
    # ------------------------------------------------------------------
    if not _table_exists("data_residency_policies"):
        op.create_table(
            "data_residency_policies",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("org_id", sa.String(36), nullable=False),
            sa.Column("primary_region", sa.String(64), nullable=False),
            sa.Column("permitted_regions", sa.Text(), nullable=True),
            sa.Column("allow_cross_region_ai", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("audit_log_region_locked", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_drp_org_id", "data_residency_policies", ["org_id"], unique=True
        )

    # ------------------------------------------------------------------
    # connector_sync_cursors
    # ------------------------------------------------------------------
    if not _table_exists("connector_sync_cursors"):
        op.create_table(
            "connector_sync_cursors",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("integration", sa.String(128), nullable=False),
            sa.Column("cursor_value", sa.Text(), nullable=False),
            sa.Column("last_successful_fetch_at", sa.DateTime(), nullable=True),
            sa.Column("fetch_count", sa.String(32), nullable=True, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_csc_artist_integration",
            "connector_sync_cursors",
            ["artist_id", "integration"],
            unique=True,
        )

    # ------------------------------------------------------------------
    # webhook_events
    # ------------------------------------------------------------------
    if not _table_exists("webhook_events"):
        op.create_table(
            "webhook_events",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("source", sa.String(128), nullable=False),
            sa.Column("event_type", sa.String(128), nullable=False),
            sa.Column("raw_payload", sa.Text(), nullable=False),
            sa.Column("signature", sa.String(256), nullable=True),
            sa.Column("signature_verified", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
            sa.Column("processing_error", sa.Text(), nullable=True),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("processed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_we_source", "webhook_events", ["source"])
        op.create_index("ix_we_status", "webhook_events", ["status"])

    # ------------------------------------------------------------------
    # slo_metrics
    # ------------------------------------------------------------------
    if not _table_exists("slo_metrics"):
        op.create_table(
            "slo_metrics",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("org_id", sa.String(36), nullable=False),
            sa.Column("metric_name", sa.String(256), nullable=False),
            sa.Column("window_seconds", sa.Integer(), nullable=False, server_default="3600"),
            sa.Column("threshold_ms", sa.Float(), nullable=False, server_default="2000"),
            sa.Column("current_p95_ms", sa.Float(), nullable=True),
            sa.Column("error_budget_pct", sa.Float(), nullable=True),
            sa.Column("burn_rate", sa.Float(), nullable=True),
            sa.Column("breached", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("measured_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_slo_org_id", "slo_metrics", ["org_id"])

    # ------------------------------------------------------------------
    # tenant_cost_ledger
    # ------------------------------------------------------------------
    if not _table_exists("tenant_cost_ledger"):
        op.create_table(
            "tenant_cost_ledger",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("org_id", sa.String(36), nullable=False),
            sa.Column("period_start", sa.DateTime(), nullable=False),
            sa.Column("period_end", sa.DateTime(), nullable=False),
            sa.Column("pipeline_cost_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("compute_cost_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("storage_cost_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("llm_tokens_used", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("llm_cost_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_cost_usd", sa.Float(), nullable=False, server_default="0"),
            sa.Column("budget_limit_usd", sa.Float(), nullable=True),
            sa.Column("budget_alert_pct", sa.Float(), nullable=False, server_default="80"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_tcl_org_id", "tenant_cost_ledger", ["org_id"])

    # ------------------------------------------------------------------
    # batch_ingestion_jobs
    # ------------------------------------------------------------------
    if not _table_exists("batch_ingestion_jobs"):
        op.create_table(
            "batch_ingestion_jobs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("org_id", sa.String(36), nullable=True),
            sa.Column("idempotency_key", sa.String(256), nullable=True, unique=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("total_files", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("processed_files", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("failed_files", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error_summary", sa.Text(), nullable=True),
            sa.Column("submitted_at", sa.DateTime(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_bij_artist_id", "batch_ingestion_jobs", ["artist_id"])

    # ------------------------------------------------------------------
    # batch_ingestion_files
    # ------------------------------------------------------------------
    if not _table_exists("batch_ingestion_files"):
        op.create_table(
            "batch_ingestion_files",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("job_id", sa.String(36), nullable=False),
            sa.Column("filename", sa.String(512), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("parsed_rows", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error_msg", sa.Text(), nullable=True),
            sa.Column("processed_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_bif_job_id", "batch_ingestion_files", ["job_id"])


def downgrade() -> None:
    for table in [
        "batch_ingestion_files",
        "batch_ingestion_jobs",
        "tenant_cost_ledger",
        "slo_metrics",
        "webhook_events",
        "connector_sync_cursors",
        "data_residency_policies",
        "case_approvals",
        "case_attachments",
        "case_comments",
        "case_room_members",
        "case_rooms",
        "notification_delivery_logs",
    ]:
        if _table_exists(table):
            op.drop_table(table)
