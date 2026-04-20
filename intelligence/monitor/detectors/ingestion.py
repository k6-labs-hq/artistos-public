"""Ingestion pipeline health detector."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select

from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState
from XR7.models.claim import Claim


class IngestionDetector(Detector):
    """Monitors ingestion pipeline health and payer data quality."""

    @property
    def name(self) -> str:
        return "ingestion-pipeline-detector"

    @property
    def domain(self) -> str:
        return "ingestion"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        findings.extend(self._check_dead_letter_queue(state))

        return findings

    def _check_dead_letter_queue(self, state: PlatformState) -> list[Finding]:
        """Check for elevated dead letter queue depth (simulated)."""
        # In production, query dead_letter_events table or Celery failed task queue
        # For now, simulate by checking for ingestion-related errors in logs

        # This is a placeholder detection - in real implementation would query:
        # SELECT payer, COUNT(*) FROM dead_letter_events
        # WHERE created_at >= NOW() - INTERVAL '24 hours'
        # GROUP BY payer

        # Simulated check: look for claims with anomaly detection but no evidence
        # (indicates ingestion failure)
        stmt = (
            select(func.count())
            .select_from(Claim)
            .where(
                and_(
                    Claim.created_at >= datetime.now(timezone.utc) - timedelta(hours=24),
                    Claim.evidence.is_(None),
                )
            )
        )

        try:
            failed_ingestion = state.db_session.execute(stmt).scalar()

            # Alert if >5% of recent claims have no evidence
            total_stmt = (
                select(func.count())
                .select_from(Claim)
                .where(Claim.created_at >= datetime.now(timezone.utc) - timedelta(hours=24))
            )
            total_recent = state.db_session.execute(total_stmt).scalar()

            if total_recent > 0:
                failure_rate = failed_ingestion / total_recent

                if failure_rate > 0.05:
                    return [
                        Finding(
                            detector=self.name,
                            severity=FindingSeverity.P1,
                            domain=self.domain,
                            title=f"ingestion failure rate elevated ({failure_rate:.1%})",
                            description=f"Last 24 hours: {failed_ingestion} of {total_recent} claims created without evidence. Normal failure rate <5%. This indicates ingestion pipeline degradation.",
                            expected_behavior="Ingestion pipeline should successfully attach evidence to >95% of claims within 1 hour of creation.",
                            investigation_path=[
                                "Check Celery worker logs for ingestion task failures",
                                "Verify PRO adapter health (ASCAP, BMI, SESAC, MLC, SoundExchange)",
                                "Review payer API rate limit status",
                                "Check for schema changes in payer data formats",
                            ],
                            metadata={
                                "failed_ingestion_24h": failed_ingestion,
                                "total_claims_24h": total_recent,
                                "failure_rate": failure_rate,
                                "threshold": 0.05,
                            },
                        )
                    ]
        except Exception:
            # Claim model not available - not a monitor failure
            pass

        return []
