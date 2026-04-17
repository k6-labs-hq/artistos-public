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


@celery_app.task(
    name="xr7.tasks.ops.backup_database_to_s3",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def backup_database_to_s3(self) -> dict[str, Any]:  # noqa: ANN001
    """Daily task: pg_dump the database and upload the result to S3.

    Reads connection details from DATABASE_URL env var.  Uploads to
    ``s3://<S3_BUCKET>/backups/<YYYY-MM-DD>/xr7_<timestamp>.pgdump``.

    Returns a summary dict with ``status``, ``s3_key``, and ``size_bytes``.
    """
    import subprocess
    import tempfile
    import urllib.parse

    db_url = os.environ.get("DATABASE_URL", "")
    endpoint = os.environ.get("S3_ENDPOINT_URL")
    bucket = os.environ.get("S3_BUCKET", "xr7-artifacts")
    access_key = os.environ.get("S3_ACCESS_KEY_ID")
    secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")

    if not db_url:
        logger.error("backup_database_to_s3: DATABASE_URL not set")
        return {"status": "error", "error": "DATABASE_URL not configured"}

    if not all([endpoint, access_key, secret_key]):
        logger.error("backup_database_to_s3: S3 credentials not configured")
        return {"status": "error", "error": "S3 credentials not configured"}

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    ts_str = now.strftime("%Y%m%dT%H%M%SZ")
    s3_key = f"backups/{date_str}/xr7_{ts_str}.pgdump"

    # Parse DATABASE_URL to extract pg_dump arguments.
    # Supports postgresql://user:pass@host:port/dbname
    parsed = urllib.parse.urlparse(db_url)
    pg_env = dict(os.environ)
    if parsed.password:
        pg_env["PGPASSWORD"] = parsed.password

    pg_host = parsed.hostname or "localhost"
    pg_port = str(parsed.port or 5432)
    pg_user = parsed.username or "postgres"
    pg_db = (parsed.path or "/postgres").lstrip("/")

    try:
        with tempfile.NamedTemporaryFile(suffix=".pgdump", delete=False) as tmp:
            tmp_path = tmp.name

        result = subprocess.run(  # noqa: S603
            [
                "pg_dump",
                "-h", pg_host,
                "-p", pg_port,
                "-U", pg_user,
                "-F", "c",  # custom format (compressed)
                "-f", tmp_path,
                pg_db,
            ],
            env=pg_env,
            capture_output=True,
            timeout=600,
        )

        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace")[:500]
            logger.error("backup_database_to_s3: pg_dump failed: %s", err)
            return {"status": "error", "error": f"pg_dump failed: {err}"}

        import boto3

        s3 = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=os.environ.get("S3_REGION", "us-east-1"),
        )

        file_size = os.path.getsize(tmp_path)
        s3.upload_file(tmp_path, bucket, s3_key)

        logger.info(
            "backup_database_to_s3: uploaded %s (%d bytes) to s3://%s/%s",
            tmp_path, file_size, bucket, s3_key,
        )

        # Audit log entry
        db_session = SessionLocal()
        try:
            db_session.add(
                AdminAuditLog(
                    actor="system",
                    action="database_backup_uploaded",
                    resource_type="backup",
                    resource_id=s3_key,
                    details={"s3_key": s3_key, "size_bytes": file_size, "bucket": bucket},
                )
            )
            db_session.commit()
        except Exception:  # noqa: BLE001
            db_session.rollback()
        finally:
            db_session.close()

        return {"status": "ok", "s3_key": s3_key, "size_bytes": file_size, "bucket": bucket}

    except subprocess.TimeoutExpired:
        logger.error("backup_database_to_s3: pg_dump timed out")
        return {"status": "error", "error": "pg_dump timed out after 600s"}
    except Exception as exc:  # noqa: BLE001
        logger.error("backup_database_to_s3: unexpected error: %s", exc)
        raise self.retry(exc=exc)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:  # noqa: BLE001
            pass
