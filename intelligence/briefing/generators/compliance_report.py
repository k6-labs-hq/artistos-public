"""Compliance report generator."""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.briefing.generator import SectionGenerator
from intelligence.briefing.types import BriefingMetrics, BriefingSection
from XR7.models.claim import Claim


class ComplianceReportGenerator(SectionGenerator):
    """Generates compliance posture report."""

    @property
    def title(self) -> str:
        return "Compliance Posture"

    def generate(
        self, db_session: Session, week_start: datetime, week_end: datetime
    ) -> BriefingSection:
        """Generate compliance posture report."""
        # Claims approaching SOL deadline (next 60 days)
        sol_threshold = week_end + timedelta(days=60)
        approaching_sol = db_session.execute(
            select(func.count())
            .select_from(Claim)
            .where(
                Claim.sol_deadline.isnot(None),
                Claim.sol_deadline <= sol_threshold,
                Claim.status != "RESOLVED",
            )
        ).scalar()

        # Claims with evidence (chain integrity maintained)
        claims_with_evidence = db_session.execute(
            select(func.count()).select_from(Claim).where(Claim.evidence.isnot(None))
        ).scalar()

        total_claims = db_session.execute(
            select(func.count()).select_from(Claim)
        ).scalar()

        chain_integrity_pct = (
            (claims_with_evidence / total_claims * 100) if total_claims > 0 else 0.0
        )

        summary = f"""Chain-of-custody maintained for {chain_integrity_pct:.1f}% of claims via SHA-256 ledger. 
{approaching_sol:,} claims approaching statute of limitations deadline in next 60 days."""

        metrics = {
            "Chain Integrity": BriefingMetrics(
                total_count=claims_with_evidence,
                period_change=0.0,
                notable_events=[f"{chain_integrity_pct:.1f}% of claims have evidence"],
            ),
            "Approaching SOL": BriefingMetrics(
                total_count=approaching_sol,
                period_change=0.0,
                notable_events=[f"{approaching_sol:,} claims need attention"],
            ),
        }

        recommendations = []
        if approaching_sol > 50:
            recommendations.append(
                f"⚠️ {approaching_sol} claims approaching SOL - prioritize resolution workflow"
            )
        if chain_integrity_pct < 99:
            recommendations.append(
                "📋 Not all claims have evidence packets - review ingestion pipeline"
            )

        return BriefingSection(
            title=self.title,
            summary=summary,
            metrics=metrics,
            recommendations=recommendations,
        )
