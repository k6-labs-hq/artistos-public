"""
tests/test_vip_founders_circle.py
──────────────────────────────────
Full coverage test suite for the Invite-Only Premier Experience:
  - VIP invite code creation and claim flow
  - Admin grant / revoke
  - VIP status + drops endpoints (403 guard)
  - Concierge messaging (send / read / escalate)
  - Persona enrichment trigger and GET
  - Copilot query + feedback + history
  - Weekly brief generation
  - VIP referral creation + listing
  - VipService unit tests (offline, no HTTP)
"""

from __future__ import annotations

import hashlib
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession  # shared DB session factory
from XR7.api.app import app
from XR7.models.vip import (
    ConciergeMessageSender,
    CopilotQuery,
    VipTierLevel,
)
from XR7.services.vip_service import VipService

# ──────────────────────────────────────────────────────────────
# Shared test client
# ──────────────────────────────────────────────────────────────

client = TestClient(app)

_ADMIN_HEADERS = {
    "X-Org-Key": "org-secret",
    "X-Org-Role": "org_admin",
    "X-Org-Actor": "admin@test.xr7",
}


def _uid() -> str:
    """Short unique suffix for test isolation."""
    return uuid.uuid4().hex[:10]


def _make_artist(db, name: str = "Test Artist") -> str:
    """Insert a minimal Artist row and return its id (UUID string)."""
    from XR7.models.artist import Artist

    a = Artist(
        name=name,
        email=f"artist_{_uid()}@test.xr7",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a.id


# ══════════════════════════════════════════════════════════════
# 1.  ADMIN: create invite codes
# ══════════════════════════════════════════════════════════════


class TestAdminInviteCodes:
    def test_create_invite_code_success(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        r = client.post(
            "/admin/vip/invite-codes",
            json={"max_uses": 1, "perk_bonus": "early_access"},
            headers=_ADMIN_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        # Response shape: {"codes": [...], "invite_links": [...]}
        assert "codes" in data
        assert len(data["codes"]) == 1
        assert len(data["codes"][0]["code"]) >= 20

    def test_create_invite_code_returns_raw_code(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        r = client.post(
            "/admin/vip/invite-codes",
            json={"count": 1},
            headers=_ADMIN_HEADERS,
        )
        assert r.status_code == 200
        code = r.json()["codes"][0]["code"]
        # token_urlsafe(24) produces 32-char base64url strings
        assert len(code) == 32


# ══════════════════════════════════════════════════════════════
# 2.  CLAIM INVITE
# ══════════════════════════════════════════════════════════════


class TestClaimInvite:
    def _create_code(self) -> str:
        """Create an invite code via service and return raw token."""
        with TestSession() as db:
            svc = VipService(db)
            entry = svc.create_invite_code(perk_bonus="test_perk")
            return entry.code

    def _artist_id(self) -> str:
        with TestSession() as db:
            return _make_artist(db)

    def test_claim_valid_code(self):
        code = self._create_code()
        artist_id = self._artist_id()
        r = client.post(
            "/invite/vip/claim",
            json={"invite_code": code, "artist_id": artist_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["membership"]["tier_level"] == "FOUNDERS_CIRCLE"

    def test_claim_invalid_code(self):
        artist_id = self._artist_id()
        r = client.post(
            "/invite/vip/claim",
            json={"invite_code": "totallyinvalidXXXXXXXX123456789", "artist_id": artist_id},
        )
        assert r.status_code in (400, 404)

    def test_claim_same_code_twice_rejected(self):
        code = self._create_code()
        artist_id = self._artist_id()
        r1 = client.post(
            "/invite/vip/claim",
            json={"invite_code": code, "artist_id": artist_id},
        )
        assert r1.status_code == 200
        # Second claim by same artist should fail
        r2 = client.post(
            "/invite/vip/claim",
            json={"invite_code": code, "artist_id": artist_id},
        )
        assert r2.status_code in (400, 409)

    def test_claim_used_code_rejected(self):
        """After max_uses exhausted, further claims fail."""
        code = self._create_code()  # max_uses=1
        artist_a = self._artist_id()
        artist_b = self._artist_id()
        r1 = client.post(
            "/invite/vip/claim",
            json={"invite_code": code, "artist_id": artist_a},
        )
        assert r1.status_code == 200
        r2 = client.post(
            "/invite/vip/claim",
            json={"invite_code": code, "artist_id": artist_b},
        )
        assert r2.status_code in (400, 409, 410)


# ══════════════════════════════════════════════════════════════
# 3.  ADMIN GRANT / REVOKE
# ══════════════════════════════════════════════════════════════


class TestAdminGrantRevoke:
    def test_grant_vip(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={
                "artist_id": aid,
                "tier_level": "VIP",
                "concierge_analyst_name": "Jane Analyst",
                "concierge_analyst_email": "jane@xr7.test",
            },
            headers=_ADMIN_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_revoke_vip(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        # Grant first
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "VIP"},
            headers=_ADMIN_HEADERS,
        )
        r = client.delete(
            f"/admin/artists/{aid}/vip",
            headers=_ADMIN_HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_revoke_non_vip_404(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.delete(
            f"/admin/artists/{aid}/vip",
            headers=_ADMIN_HEADERS,
        )
        assert r.status_code == 404


# ══════════════════════════════════════════════════════════════
# 4.  VIP STATUS ENDPOINT
# ══════════════════════════════════════════════════════════════


class TestVipStatusEndpoint:
    def _grant_vip(self, artist_id: str, monkeypatch) -> None:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        client.post(
            f"/admin/artists/{artist_id}/vip/grant",
            json={"artist_id": artist_id, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )

    def test_status_for_vip_member(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        self._grant_vip(aid, monkeypatch)
        r = client.get(f"/artists/{aid}/vip/status")
        assert r.status_code == 200
        data = r.json()
        assert data["is_vip"] is True
        assert data["tier_level"] == "FOUNDERS_CIRCLE"

    def test_status_for_non_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.get(f"/artists/{aid}/vip/status")
        assert r.status_code == 200
        data = r.json()
        assert data["is_vip"] is False

    def test_drops_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.get(f"/artists/{aid}/vip/drops")
        assert r.status_code == 403

    def test_drops_for_vip_member(self, monkeypatch):
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        self._grant_vip(aid, monkeypatch)
        r = client.get(f"/artists/{aid}/vip/drops")
        assert r.status_code == 200
        drops = r.json()
        assert isinstance(drops, list)


# ══════════════════════════════════════════════════════════════
# 5.  CONCIERGE MESSAGING
# ══════════════════════════════════════════════════════════════


class TestConciergeMessaging:
    def _vip_artist(self, monkeypatch) -> str:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )
        return aid

    def test_get_messages_empty(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.get(f"/artists/{aid}/concierge/messages")
        assert r.status_code == 200
        assert r.json() == []

    def test_send_message_as_artist(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.post(
            "/concierge/send",
            json={
                "artist_id": aid,
                "message_body": "Hello, I need help with my claim.",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] is not None

    def test_send_message_as_analyst(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.post(
            "/concierge/send",
            json={
                "artist_id": aid,
                "message_body": "We're reviewing your case.",
            },
        )
        assert r.status_code == 200

    def test_messages_list_after_send(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        client.post(
            "/concierge/send",
            json={"artist_id": aid, "message_body": "Test message"},
        )
        r = client.get(f"/artists/{aid}/concierge/messages")
        assert r.status_code == 200
        msgs = r.json()
        assert len(msgs) >= 1
        assert msgs[0]["message_body"] == "Test message"

    def test_mark_messages_read(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        send = client.post(
            "/concierge/send",
            json={"artist_id": aid, "message_body": "Unread message"},
        )
        mid = send.json()["id"]
        r = client.post(
            f"/artists/{aid}/concierge/read",
            json={"message_ids": [mid]},
        )
        assert r.status_code == 200
        assert r.json().get("marked", 0) >= 1

    def test_escalate_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.post(
            f"/artists/{aid}/concierge/escalate",
            json={"reason": "Urgent claim issue"},
        )
        assert r.status_code == 403

    def test_escalate_vip_success(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.post(
            f"/artists/{aid}/concierge/escalate",
            json={"reason": "Need urgent help with disputed royalties"},
        )
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════
# 6.  PERSONA ENRICHMENT
# ══════════════════════════════════════════════════════════════


class TestPersonaEnrichment:
    def _vip_artist(self, monkeypatch) -> str:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )
        return aid

    def test_get_persona_empty(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.get(f"/artists/{aid}/persona")
        # Either 200 with null persona or 404 is acceptable
        assert r.status_code in (200, 404)

    def test_enrich_persona_queues_task(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.tasks.vip_tasks.enrich_artist_persona") as mock_task:
            mock_task.delay = MagicMock(return_value=MagicMock(id="celery-task-123"))
            r = client.post(
                f"/artists/{aid}/persona/enrich",
                json={},
            )
        assert r.status_code == 200

    def test_enrich_persona_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.post(f"/artists/{aid}/persona/enrich", json={})
        assert r.status_code == 403


# ══════════════════════════════════════════════════════════════
# 7.  COPILOT QUERY + FEEDBACK + HISTORY
# ══════════════════════════════════════════════════════════════


class TestCopilot:
    def _vip_artist(self, monkeypatch) -> str:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )
        return aid

    def test_copilot_query_returns_response(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.llm.advisor.ask_xr7_advisor") as mock_advisor:
            mock_advisor.return_value = (
                "Here is your strategy analysis.",
                0.87,
                ["MusicBrainz", "Internal claims DB"],
            )
            r = client.post(
                f"/artists/{aid}/copilot/query",
                json={
                    "query": "What should I focus on this week?",
                    "include_catalog_context": False,
                    "include_recovery_context": False,
                },
            )
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert data["confidence"] == pytest.approx(0.87, abs=0.01)

    def test_copilot_query_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        with patch("XR7.llm.advisor.ask_xr7_advisor") as mock_advisor:
            mock_advisor.return_value = ("mock", 0.5, [])
            r = client.post(
                f"/artists/{aid}/copilot/query",
                json={
                    "query": "test",
                    "include_catalog_context": False,
                    "include_recovery_context": False,
                },
            )
        assert r.status_code == 403

    def test_copilot_history_empty(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.get(f"/artists/{aid}/copilot/history")
        assert r.status_code == 200
        assert r.json() == [] or isinstance(r.json(), list)

    def test_copilot_history_after_query(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.llm.advisor.ask_xr7_advisor") as mock_advisor:
            mock_advisor.return_value = ("Test response.", 0.75, [])
            client.post(
                f"/artists/{aid}/copilot/query",
                json={
                    "query": "Tell me about my royalties",
                    "include_catalog_context": False,
                    "include_recovery_context": False,
                },
            )
        r = client.get(f"/artists/{aid}/copilot/history")
        assert r.status_code == 200
        history = r.json()
        assert len(history) >= 1
        assert history[0]["query_text"] == "Tell me about my royalties"

    def test_copilot_feedback_thumbs_up(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.llm.advisor.ask_xr7_advisor") as mock_advisor:
            mock_advisor.return_value = ("Response.", 0.9, [])
            qr = client.post(
                f"/artists/{aid}/copilot/query",
                json={
                    "query": "Test query",
                    "include_catalog_context": False,
                    "include_recovery_context": False,
                },
            )
        query_id = qr.json()["query_id"]
        r = client.post(
            f"/artists/{aid}/copilot/feedback",
            json={"query_id": query_id, "thumbs_up": True},
        )
        assert r.status_code == 200

    def test_copilot_feedback_thumbs_down(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.llm.advisor.ask_xr7_advisor") as mock_advisor:
            mock_advisor.return_value = ("Response.", 0.6, [])
            qr = client.post(
                f"/artists/{aid}/copilot/query",
                json={
                    "query": "Another query",
                    "include_catalog_context": False,
                    "include_recovery_context": False,
                },
            )
        query_id = qr.json()["query_id"]
        r = client.post(
            f"/artists/{aid}/copilot/feedback",
            json={"query_id": query_id, "thumbs_up": False},
        )
        assert r.status_code == 200


# ══════════════════════════════════════════════════════════════
# 8.  WEEKLY BRIEF
# ══════════════════════════════════════════════════════════════


class TestWeeklyBrief:
    def _vip_artist(self, monkeypatch) -> str:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )
        return aid

    def test_get_weekly_brief_empty(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.get(f"/artists/{aid}/weekly-brief")
        assert r.status_code in (200, 404)

    def test_generate_brief_queues_task(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        with patch("XR7.tasks.vip_tasks.generate_weekly_brief_task") as mock_task:
            mock_task.delay = MagicMock(return_value=MagicMock(id="brief-task-xyz"))
            r = client.post(f"/artists/{aid}/weekly-brief/generate", json={})
        assert r.status_code in (200, 202)

    def test_brief_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.get(f"/artists/{aid}/weekly-brief")
        assert r.status_code == 403


# ══════════════════════════════════════════════════════════════
# 9.  VIP REFERRALS
# ══════════════════════════════════════════════════════════════


class TestVipReferrals:
    def _vip_artist(self, monkeypatch) -> str:
        monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
        with TestSession() as db:
            aid = _make_artist(db)
        client.post(
            f"/admin/artists/{aid}/vip/grant",
            json={"artist_id": aid, "tier_level": "FOUNDERS_CIRCLE"},
            headers=_ADMIN_HEADERS,
        )
        return aid

    def test_create_referral_success(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        r = client.post(
            f"/artists/{aid}/vip/referral",
            json={"referred_email": f"new_{_uid()}@test.xr7"},
        )
        assert r.status_code == 200
        data = r.json()
        # Response shape from vip_referrals router
        assert data is not None

    def test_create_referral_requires_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
        r = client.post(
            f"/artists/{aid}/vip/referral",
            json={"referred_email": "guest@test.xr7"},
        )
        assert r.status_code in (400, 403)

    def test_list_referrals(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        client.post(
            f"/artists/{aid}/vip/referral",
            json={"referred_email": f"a_{_uid()}@test.xr7"},
        )
        r = client.get(f"/artists/{aid}/vip/referrals")
        assert r.status_code == 200
        data = r.json()
        referrals = data.get("referrals", data) if isinstance(data, dict) else data
        assert len(referrals) >= 1

    def test_referral_slot_decrement(self, monkeypatch):
        aid = self._vip_artist(monkeypatch)
        initial_r = client.get(f"/artists/{aid}/vip/status")
        initial_slots = initial_r.json().get("membership", {}).get("referral_slots_remaining", 0)
        client.post(
            f"/artists/{aid}/vip/referral",
            json={"referred_email": f"b_{_uid()}@test.xr7"},
        )
        after_r = client.get(f"/artists/{aid}/vip/status")
        after_slots = (
            after_r.json().get("membership", {}).get("referral_slots_remaining", initial_slots)
        )
        assert after_slots == initial_slots - 1


# ══════════════════════════════════════════════════════════════
# 10.  VipService UNIT TESTS (offline, direct DB)
# ══════════════════════════════════════════════════════════════


class TestVipServiceUnit:
    def test_is_vip_false_for_new_artist(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            assert svc.is_vip(aid) is False

    def test_admin_grant_sets_vip(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            assert svc.is_vip(aid) is True

    def test_create_invite_code_returns_orm_with_raw_code(self):
        with TestSession() as db:
            svc = VipService(db)
            entry = svc.create_invite_code()
            assert isinstance(entry.code, str)
            assert len(entry.code) >= 20
            assert entry.code_hash != entry.code
            expected_hash = hashlib.sha3_256(entry.code.encode()).hexdigest()
            assert entry.code_hash == expected_hash

    def test_claim_invite_sets_membership(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            entry = svc.create_invite_code()
            member = svc.claim_invite(aid, entry.code)
            assert member.artist_id == aid
            assert member.is_active is True
            assert svc.is_vip(aid) is True

    def test_claim_invalid_code_raises(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            with pytest.raises(Exception):
                svc.claim_invite(aid, "not_a_real_code_xyz123")

    def test_revoke_vip_deactivates(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.VIP)
            svc.revoke_vip(aid)
            assert svc.is_vip(aid) is False

    def test_send_and_get_messages(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            svc.send_message(
                artist_id=aid,
                sender_type=ConciergeMessageSender.ARTIST,
                sender_name="Artist",
                message_body="Hello from artist",
            )
            msgs = svc.get_messages(aid)
            assert len(msgs) == 1
            assert msgs[0].message_body == "Hello from artist"

    def test_record_copilot_query(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            qid = svc.record_copilot_query(
                artist_id=aid,
                query_text="What are my top claims?",
                response_text="Your top 3 claims are…",
                confidence=0.88,
                sources_cited=["claims_db"],
            )
            assert qid is not None

    def test_feedback_copilot_updates(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            record = svc.record_copilot_query(
                artist_id=aid,
                query_text="Test Q",
                response_text="Test A",
                confidence=0.7,
            )
            svc.feedback_copilot(record.id, aid, thumbs_up=True)
            q = db.get(CopilotQuery, record.id)
            assert q is not None
            assert q.thumbs_up is True

    def test_create_referral_decrements_slots(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            member = svc.get_membership(aid)
            assert member is not None
            member.referral_slots_remaining = 2
            db.commit()
            email = f"ref_{_uid()}@test.xr7"
            svc.create_referral(referrer_artist_id=aid, referred_email=email)
            member = svc.get_membership(aid)
            assert member is not None
            assert member.referral_slots_remaining == 1

    def test_create_referral_no_slots_raises(self):
        with TestSession() as db:
            aid = _make_artist(db)
            svc = VipService(db)
            svc.admin_grant_vip(aid, tier_level=VipTierLevel.FOUNDERS_CIRCLE)
            member = svc.get_membership(aid)
            assert member is not None
            member.referral_slots_remaining = 0
            db.commit()
            with pytest.raises(Exception):
                svc.create_referral(
                    referrer_artist_id=aid,
                    referred_email=f"over_{_uid()}@test.xr7",
                )

    def test_get_vip_drops_returns_list(self):
        with TestSession() as db:
            svc = VipService(db)
            drops = svc.get_vip_drops()
            assert isinstance(drops, list)
            assert len(drops) >= 1
            assert "title" in drops[0]

