"""Tests for XR7 platform self-monitor system."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from intelligence.monitor.detectors.billing import BillingDetector
from intelligence.monitor.detectors.compliance import ComplianceDetector
from intelligence.monitor.detectors.ledger import LedgerDetector
from intelligence.monitor.runner import MonitorRunner
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState
from XR7.models.artist import Artist
from XR7.models.base import Base
from XR7.models.claim import Claim, ClaimStatus


@pytest.fixture
def db_session():
    """Create isolated test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mock_platform_state(db_session):
    """Create mock platform state for testing."""
    return PlatformState(
        db_session=db_session,
        collected_at=datetime.utcnow(),
        timeout_per_detector=30,
    )


class TestLedgerDetector:
    """Tests for ledger integrity detector."""

    def test_detects_missing_scheduled_verification(self, mock_platform_state):
        """Detector should flag if scheduled chain verification is not configured."""
        # Setup: Artist with evidence but no scheduled verification
        artist = Artist(
            id="test-artist",
            email="test@example.com",
            name="Test Artist",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        claim = Claim(
            id="test-claim",
            artist_id=artist.id,
            anomaly_id="anomaly-1",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            evidence={"integrity": {"packet_hash": "abc123"}},
        )
        mock_platform_state.db_session.add(claim)
        mock_platform_state.db_session.commit()

        # Mock Celery configuration without chain verification
        with patch("intelligence.monitor.detectors.ledger.celery_app") as mock_celery:
            mock_celery.conf.beat_schedule = {}  # No scheduled verification

            detector = LedgerDetector()
            findings = detector.detect(mock_platform_state)

        # Assert: Should find missing scheduled task
        assert len(findings) >= 1
        finding = next((f for f in findings if "scheduled chain verification" in f.title), None)
        assert finding is not None
        assert finding.severity == FindingSeverity.P0
        assert finding.domain == "audit"

    def test_detects_chain_integrity_failure(self, mock_platform_state):
        """Detector should flag evidence packets with integrity failures."""
        artist = Artist(
            id="test-artist-2",
            email="test2@example.com",
            name="Test Artist 2",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        # Create claim with tampered evidence (mismatched hash)
        tampered_evidence = {
            "integrity": {
                "packet_hash": "TAMPERED_HASH",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "data": {"claim_value": 10000},
        }

        claim = Claim(
            id="test-claim-tampered",
            artist_id=artist.id,
            anomaly_id="anomaly-2",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            evidence=tampered_evidence,
        )
        mock_platform_state.db_session.add(claim)
        mock_platform_state.db_session.commit()

        # Mock verify_packet_integrity to return False for tampered packet
        with patch("intelligence.monitor.detectors.ledger.verify_packet_integrity") as mock_verify:
            mock_verify.return_value = False

            detector = LedgerDetector()
            findings = detector.detect(mock_platform_state)

        # Assert: Should find integrity failure
        failure_finding = next((f for f in findings if "chain integrity failure" in f.title), None)
        assert failure_finding is not None
        assert failure_finding.severity == FindingSeverity.P0


class TestBillingDetector:
    """Tests for billing integrity detector."""

    def test_detects_high_trolley_failure_rate(self, mock_platform_state):
        """Detector should flag elevated Trolley disbursement failure rate."""
        # Create 100 claims with 10% failure rate (above 5% threshold)
        artist = Artist(
            id="test-artist-billing",
            email="billing@example.com",
            name="Billing Test",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        for i in range(100):
            status = "failed" if i < 10 else "completed"
            claim = Claim(
                id=f"claim-trolley-{i}",
                artist_id=artist.id,
                anomaly_id=f"anomaly-{i}",
                claim_type="ROYALTY_DISPUTE",
                status=ClaimStatus.RESOLVED,
                currency="USD",
                trolley_payment_id=f"trolley-{i}",
                trolley_payment_status=status,
                updated_at=datetime.now(timezone.utc),
            )
            mock_platform_state.db_session.add(claim)

        mock_platform_state.db_session.commit()

        detector = BillingDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: Should find elevated failure rate
        trolley_finding = next(
            (f for f in findings if "trolley disbursement failure" in f.title), None
        )
        assert trolley_finding is not None
        assert trolley_finding.severity == FindingSeverity.P1
        assert trolley_finding.metadata["failure_rate"] > 0.05

    def test_detects_fee_calculation_drift(self, mock_platform_state):
        """Detector should flag claims where fee != recovered_amount * rate."""
        artist = Artist(
            id="test-artist-fee",
            email="fee@example.com",
            name="Fee Test",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        # Create claim with incorrect fee calculation
        claim = Claim(
            id="claim-fee-drift",
            artist_id=artist.id,
            anomaly_id="anomaly-fee",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.RESOLVED,
            currency="USD",
            recovered_amount=10000.0,
            contingency_fee=1500.0,  # Should be 1200.0 (12% of 10000)
        )
        mock_platform_state.db_session.add(claim)
        mock_platform_state.db_session.commit()

        detector = BillingDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: Should find fee drift
        drift_finding = next((f for f in findings if "fee calculation drift" in f.title), None)
        assert drift_finding is not None
        assert drift_finding.severity == FindingSeverity.P0
        assert len(drift_finding.metadata["drift_cases"]) >= 1

    def test_detects_founders_circle_approaching_capacity(self, mock_platform_state):
        """Detector should alert when Founders Circle nears 2500 seat cap."""
        # Create 2300 founders (92% capacity, above 90% threshold)
        for i in range(2300):
            artist = Artist(
                id=f"founder-{i}",
                email=f"founder{i}@example.com",
                name=f"Founder {i}",
                contingency_fee_percent=12.0,
                founders_circle_member=True,
            )
            mock_platform_state.db_session.add(artist)

        mock_platform_state.db_session.commit()

        detector = BillingDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: Should find approaching capacity
        capacity_finding = next(
            (f for f in findings if "founders circle approaching capacity" in f.title),
            None,
        )
        assert capacity_finding is not None
        assert capacity_finding.severity in [FindingSeverity.P0, FindingSeverity.P1]
        assert capacity_finding.metadata["enrolled_count"] >= 2300


class TestComplianceDetector:
    """Tests for compliance posture detector."""

    def test_detects_approaching_sol_deadlines(self, mock_platform_state):
        """Detector should flag claims with SOL deadlines within 60 days."""
        artist = Artist(
            id="test-artist-sol",
            email="sol@example.com",
            name="SOL Test",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        # Create claim expiring in 10 days (critical)
        critical_deadline = datetime.now(timezone.utc) + timedelta(days=10)
        claim_critical = Claim(
            id="claim-sol-critical",
            artist_id=artist.id,
            anomaly_id="anomaly-sol-1",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            sol_deadline=critical_deadline,
            governing_law_state="NY",
        )
        mock_platform_state.db_session.add(claim_critical)

        # Create claim expiring in 45 days (warning)
        warning_deadline = datetime.now(timezone.utc) + timedelta(days=45)
        claim_warning = Claim(
            id="claim-sol-warning",
            artist_id=artist.id,
            anomaly_id="anomaly-sol-2",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            sol_deadline=warning_deadline,
            governing_law_state="CA",
        )
        mock_platform_state.db_session.add(claim_warning)

        mock_platform_state.db_session.commit()

        detector = ComplianceDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: Should find SOL deadline warning
        sol_finding = next((f for f in findings if "statute of limitations" in f.title), None)
        assert sol_finding is not None
        assert sol_finding.severity in [FindingSeverity.P0, FindingSeverity.P1]

    def test_detects_gdpr_deletion_backlog(self, mock_platform_state):
        """Detector should flag claims marked deleted but with evidence still present."""
        artist = Artist(
            id="test-artist-gdpr",
            email="gdpr@example.com",
            name="GDPR Test",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)

        # Create claim marked deleted 45 days ago but evidence not erased
        old_deletion = datetime.now(timezone.utc) - timedelta(days=45)
        claim = Claim(
            id="claim-gdpr-overdue",
            artist_id=artist.id,
            anomaly_id="anomaly-gdpr",
            claim_type="ROYALTY_DISPUTE",
            status=ClaimStatus.IDENTIFIED,
            currency="USD",
            deleted_at=old_deletion,
            evidence={"data": "should_be_erased"},  # Still has evidence
        )
        mock_platform_state.db_session.add(claim)
        mock_platform_state.db_session.commit()

        detector = ComplianceDetector()
        findings = detector.detect(mock_platform_state)

        # Assert: Should find GDPR backlog
        gdpr_finding = next((f for f in findings if "GDPR deletion backlog" in f.title), None)
        assert gdpr_finding is not None
        assert gdpr_finding.severity == FindingSeverity.P1


class TestMonitorRunner:
    """Integration tests for monitor runner."""

    def test_runner_executes_all_detectors(self, mock_platform_state):
        """Runner should execute all detectors and collect findings."""
        runner = MonitorRunner()
        state = runner.run(mock_platform_state)

        # Assert: Should have run detectors (findings or no findings)
        assert isinstance(state.findings, list)
        assert isinstance(state.detector_errors, dict)

        summary = runner.run_summary(state)
        assert summary["total_detectors"] == 7  # All 7 detectors

    def test_runner_handles_detector_failure_gracefully(self, mock_platform_state):
        """Runner should continue if one detector fails."""

        # Create a detector that always raises
        class FailingDetector:
            @property
            def name(self):
                return "failing-detector"

            @property
            def domain(self):
                return "test"

            def detect(self, state):
                raise ValueError("Intentional test failure")

        runner = MonitorRunner(detectors=[FailingDetector])
        state = runner.run(mock_platform_state)

        # Assert: Should have recorded the error
        assert "failing-detector" in state.detector_errors
        assert "Intentional test failure" in state.detector_errors["failing-detector"]

    def test_full_monitor_cycle_with_issue_filing(self, mock_platform_state):
        """Integration test: full monitor run with simulated issue filing."""
        # Setup: Create minimal artist for cycle test
        artist = Artist(
            id="integration-test-artist",
            email="integration@example.com",
            name="Integration Test",
            contingency_fee_percent=12.0,
        )
        mock_platform_state.db_session.add(artist)
        mock_platform_state.db_session.commit()

        # Run monitor
        runner = MonitorRunner()
        state = runner.run(mock_platform_state)

        # Collect summary
        summary = runner.run_summary(state)

        # Assert: Monitor completed successfully
        assert summary["total_detectors"] > 0
        assert isinstance(summary["findings_by_severity"], dict)
        assert isinstance(summary["findings_by_domain"], dict)

    def test_finding_generates_valid_github_issue_format(self):
        """Finding should generate correctly formatted GitHub issue."""
        finding = Finding(
            detector="test-detector",
            severity=FindingSeverity.P1,
            domain="test",
            title="test finding",
            description="This is a test finding",
            expected_behavior="System should work correctly",
            investigation_path=["Check logs", "Review code", "Escalate if needed"],
            runbook_link="docs/runbooks/test.md",
            metadata={"key": "value"},
        )

        title = finding.to_github_issue_title()
        assert title == "[P1] test: test finding"

        body = finding.to_github_issue_body()
        assert "test-detector" in body
        assert "P1" in body
        assert "This is a test finding" in body
        assert "System should work correctly" in body
        assert "Check logs" in body
        assert "XR7 Self-Monitor" in body

        labels = finding.to_github_labels()
        assert "auto-filed" in labels
        assert "monitor" in labels
        assert "test" in labels
        assert "p1" in labels
