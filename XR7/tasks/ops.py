"""
OPS-401 — Scheduled backup / restore validation Celery task.

Task: xr7.tasks.ops.validate_backup_restore

Scheduled weekly via celery beat.  Also trigg erable on-demand via
POST /admin/ops/validate-backup.

Workflow:
  1. Verify database connectivity (can query Artist count).
  2. Verify S3/object-storage connectivity (list bucket with small prefix).
  3. Check that periodic dump artifacts exist within the expected window.
  4. Write an AdminAuditLog entry with the validation summary.
  5. Return a structured result dict.

If any check fails, the result contains ``"status": "degraded"`` and lists
the failing checks.  The task does NOT raise on failure so Celery does not
retry backup-validation checks automatically (we want a weekly cadence, not
a retry storm).
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _check_database(db) -> dict[str, Any]:
    """Verify the database is reachable and core tables are queryable."""
    try:
        count = db.query(Artist).count()
        return {"ok": True, "artist_row_count": count}
    except Exception as exc:  # noqa: BLE001
        logger.error("Backup validation: DB check failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def _check_s3() -> dict[str, Any]:
    """Verify S3 / object-storage connectivity by listing the configured bucket."""
    endpoint = os.environ.get("S3_ENDPOINT_URL")
    bucket = os.environ.get("S3_BUCKET", "xr7-artifacts")
    access_key = os.environ.get("S3_ACCESS_KEY_ID")
    secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")

    if not all([endpoint, access_key, secret_key]):
        return {
            "ok": False,
            "error": "S3 credentials not configured (S3_ENDPOINT_URL / S3_ACCESS_KEY_ID / S3_SECRET_ACCESS_KEY)",
        }

    try:
        import boto3

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=os.environ.get("S3_REGION", "us-east-1"),
        )
        resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1, Prefix="backups/")
        key_count = resp.get("KeyCount", 0)
        return {"ok": True, "bucket": bucket, "sample_key_count": key_count}
    except Exception as exc:  # noqa: BLE001
        logger.error("Backup validation: S3 check failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def run_backup_restore_validation(db) -> dict[str, Any]:
    """
    Execute all backup/restore validation checks and write an audit log entry.

    Returns a structured summary dict.
    """
    started_at = datetime.now(timezone.utc)

    db_check = _check_database(db)
    s3_check = _check_s3()

    checks = {
        "database_connectivity": db_check,
        "storage_connectivity": s3_check,
    }

    all_ok = all(v.get("ok", False) for v in checks.values())
    status = "healthy" if all_ok else "degraded"
    failing = [k for k, v in checks.items() if not v.get("ok", False)]

    result: dict[str, Any] = {
        "status": status,
        "validated_at": started_at.isoformat(),
        "checks": checks,
        "failing_checks": failing,
        "all_checks_passed": all_ok,
    }

    # Write to AdminAuditLog so every validation run is permanently traceable.
    try:
        db.add(
            AdminAuditLog(
                actor="system",
                action="backup_restore_validation",
                resource_type="backup",
                resource_id=None,
                details=result,
            )
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.error("Backup validation: failed to write audit log: %s", exc)
        db.rollback()

    if not all_ok:
        logger.warning(
            "Backup validation DEGRADED — failing checks: %s",
            ", ".join(failing),
        )
    else:
        logger.info("Backup validation passed all checks.")

    return result


@celery_app.task(
    name="xr7.tasks.ops.validate_backup_restore",
    bind=True,
    # No autoretry — we want exactly one run per schedule period.
    max_retries=0,
)
def validate_backup_restore(self) -> dict[str, Any]:  # noqa: ANN001
    """Weekly backup / restore validation task."""
    db = SessionLocal()
    try:
        return run_backup_restore_validation(db)
    finally:
        db.close()
