from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim
from XR7.models.event import Event, EventType
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.payment import Payment, PaymentType
from XR7.models.statement import Statement
from XR7.models.work import Work, WorkType
from tests.conftest import TestSession


client = TestClient(app)


def _seed_artist_with_metadata_drift(db):
    artist = Artist(id=str(uuid.uuid4()), name="   TEST artist  ")
    db.add(artist)
    db.commit()

    work_primary = Work(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        title="my song",
        isrc="US-R1L-24-00001",
        iswc="T-123.456.789-1",
        work_type=WorkType.RECORDING,
    )
    work_duplicate = Work(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        title="My Song",
        isrc="USR1L2400001",
        iswc=None,
        work_type=WorkType.RECORDING,
    )
    db.add(work_primary)
    db.add(work_duplicate)

    ev = Event(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        work_id=work_duplicate.id,
        event_type=EventType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc) - timedelta(days=20),
        quantity=1000,
        unit_value=0.002,
        currency="USD",
    )
    db.add(ev)

    pay = Payment(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        payment_type=PaymentType.ROYALTY,
        amount=500.0,
        currency="USD",
        source="distrokid",
        period_start=datetime.now(timezone.utc) - timedelta(days=30),
        period_end=datetime.now(timezone.utc) - timedelta(days=1),
        received_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db.add(pay)

    st = Statement(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        filename="statement.csv",
        file_hash="abc",
        format_detected="Distro Kid",
        row_count=1,
        events_created=1,
        payments_created=1,
        skipped_rows=0,
        status="PROCESSED",
        ingestion_metadata_json=json.dumps({"upc": "12-34-56-78"}),
    )
    db.add(st)

    anom = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        estimated_recoverable=300.0,
        status=AnomalyStatus.OPEN,
        description="Payment shortfall",
    )
    db.add(anom)

    db.commit()
    return artist, anom, work_primary, work_duplicate


def test_earnings_reconstruct_runs_metadata_audit_and_repairs():
    db = TestSession()
    try:
        artist, _, primary, duplicate = _seed_artist_with_metadata_drift(db)

        resp = client.post(
            f"/artists/{artist.id}/earnings/reconstruct",
            json={
                "start_date": (datetime.now(timezone.utc) - timedelta(days=365)).isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert resp.status_code == 200
        payload = resp.json()

        audit = payload.get("metadata_audit") or {}
        assert audit.get("issues_found", 0) > 0
        assert "catalog_graph_version" in audit
        assert "metadata_health" in audit

        issues = db.query(MetadataIssue).filter(MetadataIssue.artist_id == artist.id).all()
        assert len(issues) > 0

        db.expire_all()
        updated_duplicate = db.query(Work).filter(Work.id == duplicate.id).first()
        # Duplicate may be merged away by auto-repair.
        assert updated_duplicate is None or updated_duplicate.title == "My Song"

        risk_anomaly = (
            db.query(Anomaly)
            .filter(
                Anomaly.artist_id == artist.id,
                Anomaly.subtype == "METADATA_DRIFT_FUTURE_RISK",
            )
            .first()
        )
        assert risk_anomaly is not None

    finally:
        db.close()


def test_catalog_metadata_health_endpoint_returns_required_fields():
    db = TestSession()
    try:
        artist, _, _, _ = _seed_artist_with_metadata_drift(db)
        # Seed one issue quickly to ensure deterministic response fields.
        db.add(
            MetadataIssue(
                artist_id=artist.id,
                issue_type="MISSING_ISRC",
                severity="HIGH",
                issue_key=f"manual:{uuid.uuid4()}",
                before_value_json="{}",
                after_value_json="{}",
                confidence_score=0.7,
                repair_status="REQUIRES_REVIEW",
            )
        )
        db.commit()

        resp = client.get(f"/artists/{artist.id}/catalog/metadata-health")
        assert resp.status_code == 200
        body = resp.json()
        assert "completeness_score" in body
        assert "consistency_score" in body
        assert "identifier_coverage" in body
        assert "recommended_fixes" in body
    finally:
        db.close()


def test_evidence_packet_includes_metadata_repair_logs():
    db = TestSession()
    try:
        artist, anomaly, _, _ = _seed_artist_with_metadata_drift(db)
        db.add(
            MetadataIssue(
                artist_id=artist.id,
                issue_type="TITLE_VARIANT",
                severity="LOW",
                issue_key=f"log:{uuid.uuid4()}",
                before_value_json=json.dumps({"title": "my song"}),
                after_value_json=json.dumps({"title": "My Song"}),
                confidence_score=0.95,
                repair_status="AUTO_REPAIRED",
                repair_rationale="Normalized title",
                chain_of_custody_hash="abc123",
            )
        )
        db.commit()

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status="IDENTIFIED",
            currency="USD",
        )
        db.add(claim)
        db.commit()

        resp = client.post(f"/claims/{claim.id}/evidence")
        assert resp.status_code == 200
        packet = resp.json()
        logs = ((packet.get("metadata_repairs") or {}).get("logs") or [])
        assert len(logs) >= 1
        assert "before" in logs[0]
        assert "after" in logs[0]
        assert "confidence_score" in logs[0]
        assert "repair_rationale" in logs[0]
        assert "chain_of_custody_hash" in logs[0]
    finally:
        db.close()
