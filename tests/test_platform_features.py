"""Tests for platform features introduced in migration 0027:
- Notification delivery log endpoint
- Case rooms (CRUD, members, comments, approvals)
- Data residency policy (admin CRUD + check)
- Connector reliability (webhook ingest / DLQ replay / sync cursor)
- SLO dashboards + cost telemetry
- Batch ingestion jobs (create / progress / retry)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import (  # noqa: F401  (side-effect: overrides applied)
    TestSession,
    override_get_db,
)
from XR7.api.app import app

client = TestClient(app)

ADMIN_HEADERS = {"x-admin-key": "admin-secret"}


# ============================================================================
# Helpers
# ============================================================================


def _uid() -> str:
    return uuid.uuid4().hex[:8]


# ============================================================================
# 1. Notification delivery log
# ============================================================================


class TestNotificationDeliveryLog:
    def test_empty_log(self):
        artist_id = f"artist-{_uid()}"
        resp = client.get(f"/artists/{artist_id}/notifications/delivery-log")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_filter_by_event_key(self):
        artist_id = f"artist-{_uid()}"
        resp = client.get(
            f"/artists/{artist_id}/notifications/delivery-log",
            params={"event_key": "payment_received", "limit": 10},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_limit_validation(self):
        artist_id = f"artist-{_uid()}"
        resp = client.get(
            f"/artists/{artist_id}/notifications/delivery-log",
            params={"limit": 500},
        )
        # FastAPI validates Query(le=200) → 422
        assert resp.status_code == 422


# ============================================================================
# 2. Case rooms
# ============================================================================


class TestCaseRooms:
    def _create_room(self, artist_id: str | None = None) -> dict:
        aid = artist_id or f"artist-{_uid()}"
        resp = client.post(
            "/case-rooms",
            json={
                "artist_id": aid,
                "title": f"Room {_uid()}",
                "description": "Test case room",
            },
            headers={"x-actor-email": "analyst@xr7.test", "x-actor-role": "owner"},
        )
        assert resp.status_code == 201, resp.text
        return resp.json()

    def test_create_room(self):
        room = self._create_room()
        assert room["status"] == "open"
        assert "id" in room

    def test_get_room(self):
        room = self._create_room()
        resp = client.get(f"/case-rooms/{room['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == room["id"]

    def test_get_room_not_found(self):
        resp = client.get(f"/case-rooms/{_uid()}")
        assert resp.status_code == 404

    def test_list_artist_rooms(self):
        artist_id = f"artist-{_uid()}"
        self._create_room(artist_id)
        self._create_room(artist_id)
        resp = client.get(f"/artists/{artist_id}/case-rooms")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_patch_room_status(self):
        room = self._create_room()
        resp = client.patch(
            f"/case-rooms/{room['id']}/status",
            json={"status": "closed"},
            headers={"x-actor-email": "owner@xr7.test", "x-actor-role": "owner"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "closed"

    def test_members_add_list_delete(self):
        room = self._create_room()
        rid = room["id"]

        # Add member
        add_resp = client.post(
            f"/case-rooms/{rid}/members",
            json={"email": "member@xr7.test", "role": "commenter"},
            headers={"x-actor-email": "owner@xr7.test", "x-actor-role": "owner"},
        )
        assert add_resp.status_code == 201

        # List
        list_resp = client.get(f"/case-rooms/{rid}/members")
        assert list_resp.status_code == 200
        assert any(m["email"] == "member@xr7.test" for m in list_resp.json())

        # Delete
        del_resp = client.delete(
            f"/case-rooms/{rid}/members/member@xr7.test",
            headers={"x-actor-email": "owner@xr7.test", "x-actor-role": "owner"},
        )
        assert del_resp.status_code == 200

    def test_comments_post_list_edit(self):
        room = self._create_room()
        rid = room["id"]

        post_resp = client.post(
            f"/case-rooms/{rid}/comments",
            json={"body": "Initial comment"},
            headers={"x-actor-email": "analyst@xr7.test", "x-actor-role": "commenter"},
        )
        assert post_resp.status_code == 201
        comment_id = post_resp.json()["id"]

        list_resp = client.get(f"/case-rooms/{rid}/comments")
        assert list_resp.status_code == 200
        assert any(c["id"] == comment_id for c in list_resp.json())

        edit_resp = client.patch(
            f"/case-rooms/{rid}/comments/{comment_id}",
            json={"body": "Edited comment"},
            headers={"x-actor-email": "analyst@xr7.test", "x-actor-role": "commenter"},
        )
        assert edit_resp.status_code == 200
        assert edit_resp.json()["edited"] is True

    def test_attachments_filtered_by_role(self):
        room = self._create_room()
        resp = client.get(
            f"/case-rooms/{room['id']}/attachments",
            headers={"x-actor-email": "viewer@xr7.test", "x-actor-role": "viewer"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_approval_workflow(self):
        room = self._create_room()
        rid = room["id"]

        req_resp = client.post(
            f"/case-rooms/{rid}/approvals",
            json={"approver_email": "approver@xr7.test", "notes": "Please review"},
            headers={"x-actor-email": "analyst@xr7.test", "x-actor-role": "commenter"},
        )
        assert req_resp.status_code == 201
        approval_id = req_resp.json()["id"]

        list_resp = client.get(f"/case-rooms/{rid}/approvals")
        assert list_resp.status_code == 200
        assert any(a["id"] == approval_id for a in list_resp.json())

        decide_resp = client.post(
            f"/case-rooms/{rid}/approvals/{approval_id}/decide",
            json={"decision": "approved", "notes": "LGTM"},
            headers={"x-actor-email": "approver@xr7.test", "x-actor-role": "approver"},
        )
        assert decide_resp.status_code == 200
        assert decide_resp.json()["decision"] == "approved"


# ============================================================================
# 3. Data residency
# ============================================================================


class TestDataResidency:
    def _org_id(self):
        return f"org-{_uid()}"

    def test_set_and_get_policy(self):
        org_id = self._org_id()
        put_resp = client.put(
            f"/admin/orgs/{org_id}/data-residency",
            json={
                "primary_region": "eu-west-1",
                "permitted_regions": "eu-west-1,eu-central-1",
                "allow_cross_region_ai": False,
                "audit_log_region_locked": True,
            },
            headers=ADMIN_HEADERS,
        )
        assert put_resp.status_code in (200, 201), put_resp.text

        get_resp = client.get(
            f"/admin/orgs/{org_id}/data-residency",
            headers=ADMIN_HEADERS,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["primary_region"] == "eu-west-1"

    def test_policy_check_allowed(self):
        org_id = self._org_id()
        client.put(
            f"/admin/orgs/{org_id}/data-residency",
            json={"primary_region": "us-east-1", "permitted_regions": "us-east-1,us-west-2"},
            headers=ADMIN_HEADERS,
        )
        check_resp = client.post(
            f"/admin/orgs/{org_id}/data-residency/check",
            json={"target_region": "us-west-2"},
            headers=ADMIN_HEADERS,
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["allowed"] is True

    def test_policy_check_not_allowed(self):
        org_id = self._org_id()
        client.put(
            f"/admin/orgs/{org_id}/data-residency",
            json={"primary_region": "eu-west-1", "permitted_regions": "eu-west-1"},
            headers=ADMIN_HEADERS,
        )
        check_resp = client.post(
            f"/admin/orgs/{org_id}/data-residency/check",
            json={"target_region": "us-east-1"},
            headers=ADMIN_HEADERS,
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["allowed"] is False

    def test_admin_required(self):
        org_id = self._org_id()
        resp = client.get(f"/admin/orgs/{org_id}/data-residency")
        assert resp.status_code == 422  # missing header → validation error


# ============================================================================
# 4. Connector reliability
# ============================================================================


class TestConnectorReliability:
    def test_webhook_ingest(self):
        resp = client.post(
            "/connectors/webhook/ingest",
            json={
                "source": "soundcloud",
                "event_type": "royalty.updated",
                "raw_payload": '{"track_id": "abc", "amount": 12.50}',
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["source"] == "soundcloud"
        assert body["status"] == "PENDING"
        assert body["signature_verified"] is False  # no secret configured in test

    def test_dlq_view_empty(self):
        resp = client.get("/admin/connectors/webhook/queue", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_dlq_replay_not_found(self):
        resp = client.post(
            f"/admin/connectors/webhook/{_uid()}/replay",
            headers=ADMIN_HEADERS,
        )
        assert resp.status_code == 404

    def test_dlq_replay_pending_event_fails(self):
        """Replaying a PENDING event should fail with 404/error."""
        ingest = client.post(
            "/connectors/webhook/ingest",
            json={
                "source": "test-src",
                "event_type": "test.event",
                "raw_payload": "{}",
            },
        )
        event_id = ingest.json()["id"]
        # PENDING → replay should raise ValueError (400-ish via 404 handler)
        resp = client.post(
            f"/admin/connectors/webhook/{event_id}/replay",
            headers=ADMIN_HEADERS,
        )
        # Service raises ValueError: "Cannot replay event in status PENDING" → 404
        assert resp.status_code == 404

    def test_sync_cursor_create_and_get(self):
        artist_id = f"artist-{_uid()}"
        integration = "soundcloud"

        put_resp = client.put(
            f"/artists/{artist_id}/connectors/{integration}/sync-cursor",
            json={"cursor_value": "2026-03-20T10:00:00Z"},
        )
        assert put_resp.status_code == 200
        assert put_resp.json()["cursor_value"] == "2026-03-20T10:00:00Z"

        get_resp = client.get(f"/artists/{artist_id}/connectors/{integration}/sync-cursor")
        assert get_resp.status_code == 200
        assert get_resp.json()["integration"] == integration

    def test_sync_cursor_advance(self):
        artist_id = f"artist-{_uid()}"
        integration = "spotify"

        client.put(
            f"/artists/{artist_id}/connectors/{integration}/sync-cursor",
            json={"cursor_value": "page_token_001"},
        )
        client.put(
            f"/artists/{artist_id}/connectors/{integration}/sync-cursor",
            json={"cursor_value": "page_token_002"},
        )
        get_resp = client.get(f"/artists/{artist_id}/connectors/{integration}/sync-cursor")
        assert get_resp.json()["cursor_value"] == "page_token_002"

    def test_sync_cursor_not_found(self):
        resp = client.get(f"/artists/ghost-{_uid()}/connectors/spotify/sync-cursor")
        assert resp.status_code == 404

    def test_admin_key_required_for_dlq(self):
        resp = client.get("/admin/connectors/webhook/queue")
        assert resp.status_code == 422  # missing header


# ============================================================================
# 5. SLO dashboards + cost telemetry
# ============================================================================


class TestSlo:
    def _org(self):
        return f"org-{_uid()}"

    def test_define_and_list_slo(self):
        org_id = self._org()
        create_resp = client.post(
            f"/admin/orgs/{org_id}/slo",
            json={
                "metric_name": "claim_processing_p95",
                "window_seconds": 3600,
                "threshold_ms": 5000.0,
                "description": "95th percentile claim round-trip under 5 s",
            },
            headers=ADMIN_HEADERS,
        )
        assert create_resp.status_code == 201, create_resp.text
        slo_id = create_resp.json()["id"]

        list_resp = client.get(f"/admin/orgs/{org_id}/slo", headers=ADMIN_HEADERS)
        assert list_resp.status_code == 200
        assert any(s["id"] == slo_id for s in list_resp.json())

    def test_update_slo_measurement_and_breach(self):
        org_id = self._org()
        create_resp = client.post(
            f"/admin/orgs/{org_id}/slo",
            json={"metric_name": "api_latency_p95", "threshold_ms": 1000.0},
            headers=ADMIN_HEADERS,
        )
        slo_id = create_resp.json()["id"]

        # Exceeds threshold → must set breached=True
        patch_resp = client.patch(
            f"/admin/orgs/{org_id}/slo/{slo_id}",
            json={"current_p95_ms": 3500.0, "error_budget_pct": 12.5, "burn_rate": 4.2},
            headers=ADMIN_HEADERS,
        )
        assert patch_resp.status_code == 200
        body = patch_resp.json()
        assert body["current_p95_ms"] == 3500.0
        assert body["breached"] is True

    def test_record_and_list_costs(self):
        org_id = self._org()
        now = datetime.now(timezone.utc)
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = now.replace(day=28, hour=23, minute=59, second=59, microsecond=0)

        post_resp = client.post(
            f"/admin/orgs/{org_id}/cost-telemetry",
            json={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "pipeline_cost_usd": 120.50,
                "compute_cost_usd": 85.00,
                "storage_cost_usd": 12.00,
                "llm_tokens_used": 250000,
                "llm_cost_usd": 18.75,
                "budget_limit_usd": 500.00,
                "budget_alert_pct": 80.0,
            },
            headers=ADMIN_HEADERS,
        )
        assert post_resp.status_code == 201, post_resp.text
        body = post_resp.json()
        # total = 120.50 + 85.00 + 12.00 + 18.75 = 236.25
        assert abs(body["total_cost_usd"] - 236.25) < 0.01

        list_resp = client.get(f"/admin/orgs/{org_id}/cost-telemetry", headers=ADMIN_HEADERS)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

    def test_cost_alert_check_not_breached(self):
        org_id = self._org()
        now = datetime.now(timezone.utc)
        client.post(
            f"/admin/orgs/{org_id}/cost-telemetry",
            json={
                "period_start": now.isoformat(),
                "period_end": now.isoformat(),
                "pipeline_cost_usd": 50.00,
                "budget_limit_usd": 500.00,
                "budget_alert_pct": 80.0,
            },
            headers=ADMIN_HEADERS,
        )
        alert_resp = client.get(
            f"/admin/orgs/{org_id}/cost-telemetry/alert-check", headers=ADMIN_HEADERS
        )
        assert alert_resp.status_code == 200
        body = alert_resp.json()
        assert body["alert"] is False

    def test_cost_alert_check_breached(self):
        org_id = self._org()
        now = datetime.now(timezone.utc)
        client.post(
            f"/admin/orgs/{org_id}/cost-telemetry",
            json={
                "period_start": now.isoformat(),
                "period_end": now.isoformat(),
                "pipeline_cost_usd": 450.00,
                "budget_limit_usd": 500.00,
                "budget_alert_pct": 80.0,
            },
            headers=ADMIN_HEADERS,
        )
        alert_resp = client.get(
            f"/admin/orgs/{org_id}/cost-telemetry/alert-check", headers=ADMIN_HEADERS
        )
        assert alert_resp.status_code == 200
        assert alert_resp.json()["alert"] is True

    def test_cost_alert_no_data(self):
        org_id = self._org()
        resp = client.get(f"/admin/orgs/{org_id}/cost-telemetry/alert-check", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["alert"] is False


# ============================================================================
# 6. Batch ingestion
# ============================================================================


class TestBatchIngestion:
    def _artist(self):
        return f"artist-{_uid()}"

    def test_create_batch_job(self):
        artist_id = self._artist()
        resp = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["jan.csv", "feb.csv", "mar.csv"]},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["total_files"] == 3
        assert body["status"] == "pending"

    def test_idempotency_key_dedup(self):
        artist_id = self._artist()
        ikey = f"idem-{_uid()}"
        r1 = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["a.csv"], "idempotency_key": ikey},
        )
        r2 = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["b.csv"], "idempotency_key": ikey},
        )
        assert r1.status_code == 201
        assert r2.status_code == 201
        # Same job returned
        assert r1.json()["id"] == r2.json()["id"]

    def test_get_batch_job(self):
        artist_id = self._artist()
        create_resp = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["q1.csv"]},
        )
        job_id = create_resp.json()["id"]
        get_resp = client.get(f"/artists/{artist_id}/statements/batch/{job_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == job_id

    def test_get_batch_job_not_found(self):
        artist_id = self._artist()
        resp = client.get(f"/artists/{artist_id}/statements/batch/{_uid()}")
        assert resp.status_code == 404

    def test_get_batch_job_files(self):
        artist_id = self._artist()
        create_resp = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["f1.csv", "f2.csv"]},
        )
        job_id = create_resp.json()["id"]
        files_resp = client.get(f"/artists/{artist_id}/statements/batch/{job_id}/files")
        assert files_resp.status_code == 200
        assert len(files_resp.json()) == 2

    def test_retry_failed_files(self):
        artist_id = self._artist()
        create_resp = client.post(
            f"/artists/{artist_id}/statements/batch",
            json={"filenames": ["x.csv"]},
        )
        job_id = create_resp.json()["id"]
        retry_resp = client.post(f"/artists/{artist_id}/statements/batch/{job_id}/retry-failed")
        assert retry_resp.status_code == 200
        assert retry_resp.json()["status"] == "pending"

    def test_cross_artist_isolation(self):
        a1 = self._artist()
        a2 = self._artist()
        create_resp = client.post(
            f"/artists/{a1}/statements/batch",
            json={"filenames": ["secret.csv"]},
        )
        job_id = create_resp.json()["id"]
        # a2 should not be able to see a1's job
        resp = client.get(f"/artists/{a2}/statements/batch/{job_id}")
        assert resp.status_code == 404
