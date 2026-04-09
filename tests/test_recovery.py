import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import ClaimStatus
from XR7.models.recovery_intelligence import LedgerRecordType, RoyaltyLedgerEntry
from XR7.recovery.orchestrator import ClaimsOrchestrator


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def artist_and_anomaly(db_session):
    artist = Artist(id="artist-recovery", name="Recovery Artist")
    db_session.add(artist)
    db_session.commit()
    anomaly = Anomaly(
        id="anomaly-1",
        artist_id="artist-recovery",
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db_session.add(anomaly)
    db_session.commit()
    return artist, anomaly


def test_create_claim_identified_status(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE", {"note": "missing payment"})
    assert claim.status == ClaimStatus.IDENTIFIED
    assert claim.anomaly_id == "anomaly-1"
    assert claim.artist_id == "artist-recovery"


def test_advance_claim_transitions(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    assert claim.status == ClaimStatus.IDENTIFIED
    claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.PREPARED
    claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.SUBMITTED


def test_advance_claim_raises_at_terminal_state(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    # Advance all the way to CLOSED without hard-coding the number of
    # intermediate states in the workflow.
    for _ in range(10):
        if claim.status == ClaimStatus.CLOSED:
            break
        claim = orchestrator.advance_claim(claim.id)
    assert claim.status == ClaimStatus.CLOSED
    with pytest.raises(ValueError):
        orchestrator.advance_claim(claim.id)


def test_reconcile_recovered_amount(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    updated = orchestrator.reconcile_recovered_amount(claim.id, 1000.0, "USD")
    assert updated.recovered_amount == 1000.0
    assert updated.contingency_fee == pytest.approx(120.0)
    assert updated.currency == "USD"


def test_generate_evidence_packet_has_row_level_proof_and_reconciliation(
    db_session, artist_and_anomaly
):
    orchestrator = ClaimsOrchestrator(db_session)

    anomaly = db_session.query(Anomaly).filter(Anomaly.id == "anomaly-1").first()
    anomaly.expected_amount = 300.0
    anomaly.actual_amount = 100.0
    anomaly.estimated_recoverable = 250.0
    db_session.commit()

    db_session.add_all(
        [
            RoyaltyLedgerEntry(
                artist_id="artist-recovery",
                source="Spotify",
                record_type=LedgerRecordType.EVENT,
                source_file="spotify_q1.csv",
                source_row=10,
                expected_amount=100.0,
                received_amount=20.0,
                currency="USD",
                territory="US",
            ),
            RoyaltyLedgerEntry(
                artist_id="artist-recovery",
                source="Apple Music",
                record_type=LedgerRecordType.EVENT,
                source_file="apple_q1.csv",
                source_row=44,
                expected_amount=90.0,
                received_amount=40.0,
                currency="USD",
                territory="US",
            ),
        ]
    )
    db_session.commit()

    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    packet = orchestrator.generate_evidence_packet(claim.id)

    assert packet["proof"]["totals"]["ledger_row_count"] == 2
    assert packet["proof"]["totals"]["ledger_shortfall_amount"] == pytest.approx(130.0)
    assert packet["proof"]["missing_money_amount"] == pytest.approx(130.0)
    assert len(packet["proof"]["ledger_evidence"]) == 2
    assert packet["proof"]["ledger_evidence"][0]["source_file"] in {
        "spotify_q1.csv",
        "apple_q1.csv",
    }
    assert packet["reconciliation"]["model_shortfall_amount"] == pytest.approx(200.0)
    assert packet["reconciliation"]["proof_shortfall_amount"] == pytest.approx(130.0)
    assert packet["reconciliation"]["discrepancy_flag"] is True

    updated_claim = db_session.query(type(claim)).filter(type(claim).id == claim.id).first()
    assert updated_claim is not None
    assert updated_claim.evidence is not None
    assert updated_claim.evidence["claim_id"] == claim.id


def test_generate_evidence_packet_without_ledger_uses_model_shortfall(
    db_session, artist_and_anomaly
):
    orchestrator = ClaimsOrchestrator(db_session)

    anomaly = db_session.query(Anomaly).filter(Anomaly.id == "anomaly-1").first()
    anomaly.expected_amount = 500.0
    anomaly.actual_amount = 100.0
    anomaly.estimated_recoverable = 400.0
    db_session.commit()

    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")
    packet = orchestrator.generate_evidence_packet(claim.id)

    assert packet["proof"]["totals"]["ledger_row_count"] == 0
    assert packet["proof"]["missing_money_amount"] == pytest.approx(400.0)
    assert packet["reconciliation"]["discrepancy_amount"] == pytest.approx(0.0)
    assert packet["reconciliation"]["discrepancy_flag"] is False


def test_generate_evidence_packet_integrity_chain_advances(db_session, artist_and_anomaly):
    orchestrator = ClaimsOrchestrator(db_session)
    claim = orchestrator.create_claim("anomaly-1", "ROYALTY_DISPUTE")

    first_packet = orchestrator.generate_evidence_packet(claim.id)
    second_packet = orchestrator.generate_evidence_packet(claim.id)

    assert first_packet["integrity"]["packet_hash"]
    assert first_packet["integrity"]["chain_hash"]
    assert first_packet["integrity"]["signature"]
    assert first_packet["metadata"]["packet_version"] == "1.1"
    assert first_packet["metadata"]["revision"] == 1
    assert (
        second_packet["integrity"]["prior_packet_hash"] == first_packet["integrity"]["packet_hash"]
    )
    assert second_packet["integrity"]["chain_hash"] != first_packet["integrity"]["chain_hash"]
    assert second_packet["metadata"]["revision"] == 2


def test_claim_evidence_export_zip_and_pdf():
    client = TestClient(app)
    db = _TestSession()

    artist = Artist(id="artist-export", name="Export Artist")
    db.add(artist)
    db.commit()

    anomaly = Anomaly(
        id="anomaly-export-1",
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.95,
        expected_amount=120.0,
        actual_amount=20.0,
        estimated_recoverable=100.0,
        status=AnomalyStatus.OPEN,
    )
    db.add(anomaly)
    db.commit()

    db.add(
        RoyaltyLedgerEntry(
            artist_id=artist.id,
            source="Spotify",
            record_type=LedgerRecordType.EVENT,
            source_file="missing_statement.csv",
            source_row=5,
            expected_amount=120.0,
            received_amount=20.0,
            currency="USD",
        )
    )
    db.commit()
    artist_id = artist.id
    db.close()

    claim_resp = client.get(f"/artists/{artist_id}/claims")
    assert claim_resp.status_code == 200
    assert claim_resp.json() == []

    # Create claim through orchestrator so export endpoint can find a claim record.
    db = _TestSession()
    claim = ClaimsOrchestrator(db).create_claim("anomaly-export-1", "ROYALTY_DISPUTE")
    db.close()

    zip_resp = client.get(f"/claims/{claim.id}/evidence/export?format=zip&refresh=true")
    assert zip_resp.status_code == 200
    assert zip_resp.headers["content-type"].startswith("application/zip")

    zf = zipfile.ZipFile(io.BytesIO(zip_resp.content))
    names = set(zf.namelist())
    assert "evidence_packet.json" in names
    assert "evidence_summary.txt" in names
    assert "proof_rows.csv" in names
    assert "source_citations.csv" in names
    assert "evidence_packet.pdf" in names
    assert "integrity_manifest.json" in names

    packet = json.loads(zf.read("evidence_packet.json").decode("utf-8"))
    assert packet["integrity"]["packet_hash"]
    assert packet["proof"]["missing_money_amount"] == pytest.approx(100.0)
    assert "legal_authority_sections" in packet
    assert "legal_methodology_summary" in packet
    assert "legal_compliance_statements" in packet
    assert "legal_risk_score" in packet
    assert "settlement_probability" in packet
    assert "escalation_readiness_score" in packet
    assert "legal_structured_packet" in packet
    assert "attorney_briefing_packet" in packet
    assert "predicted_expected_value" in packet
    assert "predicted_recovery_low" in packet
    assert "predicted_recovery_high" in packet
    assert "attorney_export_package" in packet
    assert "narrative_summary" in packet

    pdf_resp = client.get(f"/claims/{claim.id}/evidence/export?format=pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"].startswith("application/pdf")
    assert pdf_resp.content.startswith(b"%PDF-")


def test_claim_evidence_verify_endpoint_and_tamper_detection():
    client = TestClient(app)
    db = _TestSession()

    artist = Artist(id="artist-verify", name="Verify Artist")
    db.add(artist)
    db.commit()

    anomaly = Anomaly(
        id="anomaly-verify-1",
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        expected_amount=80.0,
        actual_amount=10.0,
        estimated_recoverable=70.0,
        status=AnomalyStatus.OPEN,
    )
    db.add(anomaly)
    db.commit()

    claim = ClaimsOrchestrator(db).create_claim(anomaly.id, "ROYALTY_DISPUTE")
    packet = ClaimsOrchestrator(db).generate_evidence_packet(claim.id)
    packet_hash = packet["integrity"]["packet_hash"]
    db.close()

    ok_resp = client.get(f"/claims/{claim.id}/evidence/verify")
    assert ok_resp.status_code == 200
    ok_data = ok_resp.json()
    assert ok_data["valid"] is True
    assert ok_data["checks"]["packet_hash_matches"] is True
    assert ok_data["checks"]["signature_valid"] is True

    db = _TestSession()
    persisted = db.query(type(claim)).filter(type(claim).id == claim.id).first()
    tampered = dict(persisted.evidence)
    tampered_proof = dict(tampered.get("proof", {}))
    tampered_proof["missing_money_amount"] = 999999.0
    tampered["proof"] = tampered_proof
    persisted.evidence = tampered
    db.commit()
    db.close()

    bad_resp = client.get(f"/claims/{claim.id}/evidence/verify")
    assert bad_resp.status_code == 200
    bad_data = bad_resp.json()
    assert bad_data["valid"] is False
    assert bad_data["checks"]["packet_hash_matches"] is False

    prior_resp = client.get(
        f"/claims/{claim.id}/evidence/verify?expected_prior_packet_hash={packet_hash}"
    )
    assert prior_resp.status_code == 200
    prior_data = prior_resp.json()
    assert prior_data["valid"] is False
    assert prior_data["checks"]["prior_link_matches"] is False
