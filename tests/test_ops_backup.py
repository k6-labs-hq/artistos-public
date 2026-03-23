"""
OPS-401 — Tests for the backup/restore validation task and its admin endpoints.
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.tasks.ops import run_backup_restore_validation
from tests.conftest import TestSession

client = TestClient(app)


# ---------------------------------------------------------------------------
# Unit tests — task logic
# ---------------------------------------------------------------------------

def test_run_backup_restore_validation_returns_expected_shape():
    db = TestSession()
    try:
        result = run_backup_restore_validation(db)
    finally:
        db.close()

    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] in ("healthy", "degraded")
    assert "checks" in result
    assert isinstance(result["checks"], dict)


def test_run_backup_restore_validation_includes_database_check():
    db = TestSession()
    try:
        result = run_backup_restore_validation(db)
    finally:
        db.close()

    assert "database_connectivity" in result["checks"]
    db_check = result["checks"]["database_connectivity"]
    assert "ok" in db_check
    # The in-memory test DB should always respond successfully.
    assert db_check["ok"] is True


def test_run_backup_restore_validation_writes_audit_log():
    db = TestSession()
    try:
        run_backup_restore_validation(db)
        entry = (
            db.query(AdminAuditLog)
            .filter(AdminAuditLog.action == "backup_restore_validation")
            .first()
        )
    finally:
        db.close()

    assert entry is not None
    assert entry.actor == "system"
    assert entry.resource_type == "backup"


def test_run_backup_restore_validation_multiple_runs_each_log_entry():
    """Each invocation must append a new audit log row."""
    db = TestSession()
    try:
        run_backup_restore_validation(db)
        run_backup_restore_validation(db)
        count = (
            db.query(AdminAuditLog)
            .filter(AdminAuditLog.action == "backup_restore_validation")
            .count()
        )
    finally:
        db.close()

    assert count >= 2


# ---------------------------------------------------------------------------
# HTTP endpoint tests — admin console
# ---------------------------------------------------------------------------

def test_backup_report_blocks_missing_key():
    resp = client.get("/admin/ops/backup-report")
    assert resp.status_code in (401, 403, 503)


def test_backup_report_blocks_wrong_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "correct-key")
    resp = client.get("/admin/ops/backup-report", headers={"X-Admin-Key": "wrong-key"})
    assert resp.status_code in (401, 403, 503)


def test_backup_report_returns_structure(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key")
    resp = client.get("/admin/ops/backup-report", headers={"X-Admin-Key": "test-admin-key"})
    assert resp.status_code == 200
    data = resp.json()
    assert "history" in data
    assert "schedule" in data
    assert isinstance(data["history"], list)


def test_validate_backup_endpoint_runs_on_demand(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key")
    resp = client.post("/admin/ops/validate-backup", headers={"X-Admin-Key": "test-admin-key"})
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "checks" in data
    assert data["checks"]["database_connectivity"]["ok"] is True


def test_validate_backup_endpoint_blocks_wrong_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "test-admin-key")
    resp = client.post("/admin/ops/validate-backup", headers={"X-Admin-Key": "bad"})
    assert resp.status_code in (401, 403, 503)
