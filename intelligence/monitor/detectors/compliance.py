"""Compliance and regulatory posture detector."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select

from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState
from XR7.models.claim import Claim


class ComplianceDetector(Detector):
    """Monitors GDPR, SOC 2, and statute of limitations compliance."""

    @property
    def name(self) -> str:
        return "compliance-posture-detector"

    @property
    def domain(self) -> str:
        return "compliance"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        findings.extend(self._check_approaching_sol_deadlines(state))
        findings.extend(self._check_gdpr_deletion_queue(state))

        return findings

    def _check_approaching_sol_deadlines(self, state: PlatformState) -> list[Finding]:
        """Alert on statute of limitations deadlines within 60 days."""
        sixty_days = datetime.now(timezone.utc) + timedelta(days=60)

        stmt = (
            select(Claim.id, Claim.sol_deadline, Claim.governing_law_state)
            .where(
                and_(
                    Claim.sol_deadline.isnot(None),
                    Claim.sol_deadline <= sixty_days,
                    Claim.deleted_at.is_(None),
                )
            )
            .order_by(Claim.sol_deadline)
        )

        expiring_claims = state.db_session.execute(stmt).all()

        if expiring_claims:
            # Group by urgency
            critical = [
                c
                for c in expiring_claims
                if c.sol_deadline <= datetime.now(timezone.utc) + timedelta(days=14)
            ]
            warning = [c for c in expiring_claims if c not in critical]

            if critical:
                return [
                    Finding(
                        detector=self.name,
                        severity=FindingSeverity.P0,
                        domain=self.domain,
                        title=f"statute of limitations deadlines expiring ({len(critical)} claims within 14 days)",
                        description=f"Found {len(critical)} claims with SOL deadlines expiring in next 14 days. Claims become unenforceable after SOL expiration. Total at risk in 60 days: {len(expiring_claims)} claims.",
                        expected_behavior="Claims approaching SOL deadline should be prioritized for recovery action. Attorney evidence packages should be generated 90 days before SOL expiration.",
                        investigation_path=[
                            f"Query critical claims: SELECT id, artist_id, sol_deadline, governing_law_state FROM claims WHERE sol_deadline <= '{(datetime.now(timezone.utc) + timedelta(days=14)).isoformat()}' AND deleted_at IS NULL ORDER BY sol_deadline",
                            "Generate attorney evidence packages for claims without attorney_file_generated = true",
                            "Coordinate with legal counsel for filing timeline",
                            "Notify affected artists of urgency",
                        ],
                        metadata={
                            "critical_14_days": len(critical),
                            "warning_60_days": len(warning),
                            "earliest_deadline": min(
                                c.sol_deadline for c in expiring_claims
                            ).isoformat(),
                            "critical_claim_ids": [c.id for c in critical][:20],
                        },
                    )
                ]
            elif warning:
                return [
                    Finding(
                        detector=self.name,
                        severity=FindingSeverity.P1,
                        domain=self.domain,
                        title=f"statute of limitations deadlines approaching ({len(warning)} claims within 60 days)",
                        description=f"Found {len(warning)} claims with SOL deadlines expiring in next 60 days. Attorney evidence packages should be generated now.",
                        expected_behavior="Claims should have attorney evidence packages generated 90 days before SOL expiration.",
                        investigation_path=[
                            "Review claims without attorney_file_generated = true",
                            "Trigger evidence package generation workflow",
                            "Schedule legal review for high-value claims",
                        ],
                        metadata={
                            "warning_60_days": len(warning),
                            "earliest_deadline": min(c.sol_deadline for c in warning).isoformat(),
                        },
                    )
                ]

        return []

    def _check_gdpr_deletion_queue(self, state: PlatformState) -> list[Finding]:
        """Check for overdue GDPR deletion requests."""
        # GDPR Article 17: Right to erasure must be fulfilled "without undue delay"
        # Industry standard: 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        # In production, check deletion_requests table
        # For now, check for soft-deleted artists with deleted_at > 30 days ago
        # where deletion is not yet complete

        stmt = (
            select(func.count())
            .select_from(Claim)
            .where(
                and_(
                    Claim.deleted_at.isnot(None),
                    Claim.deleted_at <= thirty_days_ago,
                    # Evidence still present = deletion incomplete
                    Claim.evidence.isnot(None),
                )
            )
        )

        incomplete_deletions = state.db_session.execute(stmt).scalar()

        if incomplete_deletions and incomplete_deletions > 0:
            return [
                Finding(
                    detector=self.name,
                    severity=FindingSeverity.P1,
                    domain=self.domain,
                    title=f"GDPR deletion backlog detected ({incomplete_deletions} claims)",
                    description=f"Found {incomplete_deletions} claims marked for deletion >30 days ago but still containing evidence. GDPR Article 17 requires erasure 'without undue delay' (industry standard: 30 days).",
                    expected_behavior="Claims marked deleted_at should have evidence field nullified within 30 days. PII should be tombstoned or fully erased per deletion strategy.",
                    investigation_path=[
                        f"Query overdue deletions: SELECT id, artist_id, deleted_at FROM claims WHERE deleted_at IS NOT NULL AND deleted_at <= '{thirty_days_ago.isoformat()}' AND evidence IS NOT NULL",
                        "Check GDPR deletion job logs for failures",
                        "Verify deletion strategy implementation (tombstone vs full erasure)",
                        "Document any legal holds preventing deletion",
                    ],
                    metadata={
                        "incomplete_deletions": incomplete_deletions,
                        "threshold_days": 30,
                        "regulatory_reference": "GDPR Article 17",
                    },
                )
            ]

        return []
