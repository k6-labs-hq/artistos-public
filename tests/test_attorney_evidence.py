from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus

client = TestClient(app)


def _seed_artist_and_anomaly(db):
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Attorney Evidence Artist",
        email="artist@example.com",
        default_attorney_grace_period_days=60,
    )
    db.add(artist)
    db.commit()

    anomaly = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.88,
        estimated_recoverable=4500.0,
        status=AnomalyStatus.OPEN,
        description="Royalty payment gap",
    )
    db.add(anomaly)
    db.commit()
    return artist, anomaly


def test_list_claims_shows_countdown_and_progress_when_grace_not_elapsed():
    db = _TestSession()
    try:
        artist, anomaly = _seed_artist_and_anomaly(db)
        proof_submitted_at = datetime.now(timezone.utc) - timedelta(days=20)
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PROOF_SUBMITTED,
            recovered_amount=2200.0,
            currency="USD",
            proof_submitted_at=proof_submitted_at,
            grace_period_days=60,
            payer_name="Atlas Label",
        )
        db.add(claim)
        db.commit()

        resp = client.get(f"/artists/{artist.id}/claims")
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload) >= 1

        row = next(r for r in payload if r["claim"]["id"] == claim.id)
        escal = row["attorney_escalation"]
        assert escal["eligible_to_prepare"] is False
        assert escal["days_remaining"] == 40
        assert "Payer has 40 days remaining to respond" in escal["countdown_message"]
        assert 0.3 <= float(escal["progress"]) <= 0.34
    finally:
        db.close()


def test_generate_attorney_evidence_pdf_marks_claim_generated():
    db = _TestSession()
    try:
        artist, anomaly = _seed_artist_and_anomaly(db)
        now = datetime.now(timezone.utc)
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PROOF_SUBMITTED,
            recovered_amount=9150.0,
            currency="USD",
            payer_name="North Star Publishing",
            payer_contact="accounts@northstar.example",
            original_due_date=now - timedelta(days=95),
            proof_submitted_at=now - timedelta(days=70),
            grace_period_days=60,
            sol_deadline=now + timedelta(days=180),
            communications=[
                {
                    "date": (now - timedelta(days=68)).date().isoformat(),
                    "type": "email",
                    "summary": "Initial proof sent",
                },
                {
                    "date": (now - timedelta(days=55)).date().isoformat(),
                    "type": "follow_up",
                    "summary": "No response",
                },
            ],
            anomaly_report={
                "detectedAt": (now - timedelta(days=72)).isoformat(),
                "type": "underpayment",
                "description": "Reported royalties materially below expected range",
                "estimatedLeakage": 9150.0,
            },
            supporting_documents=[
                {
                    "name": "proof_of_non_payment.pdf",
                    "uploadedAt": (now - timedelta(days=70)).isoformat(),
                    "fileRef": "s3://bucket/proof.pdf",
                }
            ],
        )
        db.add(claim)
        db.commit()

        resp = client.post(
            f"/api/claims/{claim.id}/attorney-evidence",
            json={
                "additional_notes": "Escalate with breach timeline",
                "attorney_engagement_deadline": (now + timedelta(days=30)).isoformat(),
            },
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("application/pdf")
        assert "XR7_Evidence_" in resp.headers.get("content-disposition", "")
        assert (
            resp.headers.get("x-evidence-file-ready")
            == "Evidence file ready. Share with your attorney."
        )
        assert resp.content.startswith(b"%PDF-")

        db.refresh(claim)
        assert claim.attorney_file_generated is True
        assert claim.attorney_file_generated_at is not None

        second = client.post(f"/claims/{claim.id}/attorney-evidence", json={})
        assert second.status_code == 409
    finally:
        db.close()


def test_artist_preferences_updates_default_grace_period():
    db = _TestSession()
    try:
        artist, _ = _seed_artist_and_anomaly(db)

        get_resp = client.get(f"/artists/{artist.id}/preferences")
        assert get_resp.status_code == 200
        assert get_resp.json()["default_attorney_grace_period_days"] == 60

        put_resp = client.put(
            f"/artists/{artist.id}/preferences",
            json={"default_attorney_grace_period_days": 75},
        )
        assert put_resp.status_code == 200
        assert put_resp.json()["default_attorney_grace_period_days"] == 75
    finally:
        db.close()
