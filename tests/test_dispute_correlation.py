"""Tests for outbound filing → inbound reply correlation.

Pinned behavior:
- record_outbound_filing appends to Claim.communications and advances status
  on real (non-stub) success
- record_outbound_filing is a no-op on failed sends (no false advancement)
- record_outbound_filing on stub success records but doesn't advance status
- find_claim_by_outbound_message_id returns the right Claim for a given MessageID
- record_inbound_reply appends inbound entry and advances FILED → IN_REVIEW
- Inbound reply doesn't downgrade an already-advanced status (e.g. ACCEPTED)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from tests.conftest import TestSession as _TestSession
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.recovery.dispute_correlation import (
    find_claim_by_outbound_message_id,
    record_inbound_reply,
    record_outbound_filing,
)


def _seed_claim(status=ClaimStatus.PREPARED) -> tuple[str, str]:
    db = _TestSession()
    artist = Artist(id=str(uuid.uuid4()), name="Corr Test", created_at=datetime.now(timezone.utc))
    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="HIGH_RETROACTIVE_PAYMENT_RATIO",
        severity=AnomalySeverity.HIGH,
        status=AnomalyStatus.OPEN,
        confidence_score=0.84,
    )
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY_AUDIT",
        status=status,
        created_at=datetime.now(timezone.utc),
    )
    db.add_all([artist, anomaly, claim])
    db.commit()
    aid, cid = artist.id, claim.id
    db.close()
    return aid, cid


class TestRecordOutboundFiling:
    def test_real_success_advances_to_filed_and_records_message_id(self):
        aid, cid = _seed_claim(status=ClaimStatus.PREPARED)
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            send_result = {
                "success": True,
                "channel": "email",
                "payer_id": "BMI",
                "submission_address": "member-disputes@bmi.com",
                "message_id": "msg-real-123",
                "stubbed": False,
            }
            record_outbound_filing(claim, send_result=send_result, artist_id=aid)
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            assert claim.status == ClaimStatus.FILED
            assert claim.proof_submitted_at is not None
            assert len(claim.communications) == 1
            assert claim.communications[0]["direction"] == "outbound"
            assert claim.communications[0]["message_id"] == "msg-real-123"
        finally:
            db.close()

    def test_stub_success_records_but_does_not_advance_status(self):
        """Stub mode is for testing wiring — don't lie about real claim lifecycle."""
        aid, cid = _seed_claim(status=ClaimStatus.PREPARED)
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            record_outbound_filing(
                claim,
                send_result={
                    "success": True,
                    "channel": "email",
                    "payer_id": "BMI",
                    "submission_address": "member-disputes@bmi.com",
                    "message_id": None,
                    "stubbed": True,
                },
                artist_id=aid,
            )
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            assert claim.status == ClaimStatus.PREPARED  # unchanged
            assert claim.proof_submitted_at is None
            assert len(claim.communications) == 1
            assert claim.communications[0]["stubbed"] is True
        finally:
            db.close()

    def test_failed_send_does_nothing(self):
        """Don't lie about filing something we didn't actually file."""
        aid, cid = _seed_claim(status=ClaimStatus.PREPARED)
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            record_outbound_filing(
                claim,
                send_result={"success": False, "error_message": "rate limited"},
                artist_id=aid,
            )
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            assert claim.status == ClaimStatus.PREPARED
            assert claim.communications is None or claim.communications == []
        finally:
            db.close()


class TestInboundCorrelation:
    def test_find_returns_correct_claim_for_known_message_id(self):
        aid, cid = _seed_claim()
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            record_outbound_filing(
                claim,
                send_result={
                    "success": True,
                    "message_id": "msg-find-me",
                    "stubbed": False,
                    "channel": "email",
                    "payer_id": "BMI",
                },
                artist_id=aid,
            )
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            found = find_claim_by_outbound_message_id(db, "msg-find-me")
            assert found is not None
            assert found.id == cid
        finally:
            db.close()

    def test_find_returns_none_for_unknown_message_id(self):
        db = _TestSession()
        try:
            assert find_claim_by_outbound_message_id(db, "msg-nonexistent") is None
            assert find_claim_by_outbound_message_id(db, None) is None
            assert find_claim_by_outbound_message_id(db, "") is None
        finally:
            db.close()

    def test_record_inbound_advances_filed_to_in_review(self):
        aid, cid = _seed_claim()
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            record_outbound_filing(
                claim,
                send_result={
                    "success": True,
                    "message_id": "msg-roundtrip",
                    "stubbed": False,
                    "channel": "email",
                    "payer_id": "BMI",
                },
                artist_id=aid,
            )
            db.commit()
            assert claim.status == ClaimStatus.FILED
        finally:
            db.close()

        # Simulated Postmark inbound payload (BMI replying)
        payload = {
            "From": "BMI <support@bmi.com>",
            "Subject": "Re: Royalty audit finding",
            "MessageID": "inbound-bmi-1",
            "InReplyTo": "msg-roundtrip",
            "TextBody": "We received your filing. Case reference: BMI-DR-99999.",
        }

        db = _TestSession()
        try:
            claim = find_claim_by_outbound_message_id(db, "msg-roundtrip")
            assert claim is not None
            record_inbound_reply(claim, postmark_payload=payload)
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            assert claim.status == ClaimStatus.IN_REVIEW
            assert len(claim.communications) == 2
            assert claim.communications[1]["direction"] == "inbound"
            assert claim.communications[1]["in_reply_to"] == "msg-roundtrip"
            assert "BMI-DR-99999" in claim.communications[1]["body_excerpt"]
        finally:
            db.close()

    def test_inbound_does_not_downgrade_advanced_status(self):
        """A reply to a claim already at ACCEPTED shouldn't drop it back to IN_REVIEW."""
        aid, cid = _seed_claim(status=ClaimStatus.ACCEPTED)
        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            record_inbound_reply(
                claim,
                postmark_payload={
                    "From": "BMI",
                    "Subject": "Re: Royalty audit",
                    "MessageID": "in-x",
                    "InReplyTo": "out-x",
                    "TextBody": "follow-up",
                },
            )
            db.commit()
        finally:
            db.close()

        db = _TestSession()
        try:
            claim = db.query(Claim).filter(Claim.id == cid).one()
            assert claim.status == ClaimStatus.ACCEPTED  # unchanged
            assert len(claim.communications) == 1
        finally:
            db.close()
