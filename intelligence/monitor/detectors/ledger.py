"""Ledger integrity detector for SHA-256 chain monitoring."""

from sqlalchemy import func, select

from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState
from XR7.models.artist import Artist
from XR7.models.claim import Claim
from XR7.tasks.chain_verification import verify_packet_integrity


class LedgerDetector(Detector):
    """Monitors SHA-256 chain integrity and scheduled verification health."""

    @property
    def name(self) -> str:
        return "ledger-integrity-detector"

    @property
    def domain(self) -> str:
        return "audit"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        # Check 1: Find artists with evidence but no recent chain verification
        findings.extend(self._check_stale_verifications(state))

        # Check 2: Detect actual chain integrity failures
        findings.extend(self._check_chain_integrity(state))

        return findings

    def _check_stale_verifications(self, state: PlatformState) -> list[Finding]:
        """Check for tenants without recent chain verification."""
        # Query artists with evidence packets
        stmt = (
            select(Artist.id)
            .join(Claim, Claim.artist_id == Artist.id)
            .where(Claim.evidence.isnot(None))
            .group_by(Artist.id)
        )

        artist_ids_with_evidence = [row[0] for row in state.db_session.execute(stmt)]

        if not artist_ids_with_evidence:
            return []  # No evidence to verify - not a finding

        # In production, we'd check a chain_verification_log table
        # For now, we flag if scheduled job isn't configured
        # This is a bootstrapping check - once job runs, we'd check last_run timestamp

        # Check if verification task is in Celery beat schedule
        try:
            from XR7.celery_app import app as celery_app

            if "xr7-chain-verification-daily" not in celery_app.conf.beat_schedule:
                return [
                    Finding(
                        detector=self.name,
                        severity=FindingSeverity.P0,
                        domain=self.domain,
                        title="scheduled chain verification not configured",
                        description=f"Found {len(artist_ids_with_evidence)} artists with evidence packets, but no scheduled chain verification job is configured in Celery beat. Chain integrity violations may go undetected.",
                        expected_behavior="Celery beat schedule should include 'xr7-chain-verification-daily' task running every 86400 seconds (daily) to verify chain integrity across all tenants.",
                        investigation_path=[
                            "Check XR7/celery_app.py beat_schedule configuration",
                            "Verify Celery beat process is running in production",
                            "Check Celery beat logs for task execution history",
                        ],
                        runbook_link="docs/operations/runbooks/chain-integrity-failure.md",
                        metadata={
                            "artists_with_evidence": len(artist_ids_with_evidence),
                            "expected_schedule": "daily (86400s)",
                        },
                    )
                ]
        except Exception:
            pass  # Celery not configured - not a monitor failure

        return []

    def _check_chain_integrity(self, state: PlatformState) -> list[Finding]:
        """Sample chain integrity across random tenants."""
        # Sample up to 10 random artists with evidence for spot check
        stmt = (
            select(Artist.id, Claim.id, Claim.evidence)
            .join(Claim, Claim.artist_id == Artist.id)
            .where(Claim.evidence.isnot(None))
            .order_by(func.random())
            .limit(10)
        )

        claims_to_check = state.db_session.execute(stmt).all()

        failures = []
        for artist_id, claim_id, evidence in claims_to_check:
            try:
                if evidence and "integrity" in evidence:
                    is_valid = verify_packet_integrity(evidence)
                    if not is_valid:
                        failures.append(
                            {
                                "artist_id": artist_id,
                                "claim_id": claim_id,
                                "packet_hash": evidence["integrity"].get("packet_hash"),
                            }
                        )
            except Exception:
                # Verification errors are potential integrity issues
                failures.append(
                    {
                        "artist_id": artist_id,
                        "claim_id": claim_id,
                        "error": "verification_failed",
                    }
                )

        if failures:
            return [
                Finding(
                    detector=self.name,
                    severity=FindingSeverity.P0,
                    domain=self.domain,
                    title=f"chain integrity failure detected ({len(failures)} packet(s))",
                    description=f"Spot check of {len(claims_to_check)} evidence packets found {len(failures)} with integrity failures. This indicates potential evidence tampering or corruption.",
                    expected_behavior="All evidence packets should pass SHA-256 chain verification. packet_hash should match recomputed hash of packet contents.",
                    investigation_path=[
                        "Immediately verify affected packets using full chain verification task",
                        "Check database audit logs for unauthorized modifications to claims.evidence",
                        "Review application logs for evidence manipulation events",
                        "Escalate to Security if confirmed tampering",
                    ],
                    runbook_link="docs/operations/runbooks/chain-integrity-failure.md",
                    metadata={
                        "failed_packets": failures,
                        "sample_size": len(claims_to_check),
                        "failure_rate": len(failures) / len(claims_to_check),
                    },
                )
            ]

        return []
