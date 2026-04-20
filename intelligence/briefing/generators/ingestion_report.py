"""Ingestion report generator."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.briefing.generator import SectionGenerator
from intelligence.briefing.types import BriefingMetrics, BriefingSection
from XR7.models.claim import Claim


class IngestionReportGenerator(SectionGenerator):
    """Generates ingestion pipeline report."""

    @property
    def title(self) -> str:
        return "Ingestion Pipeline Health"

    def generate(
        self, db_session: Session, week_start: datetime, week_end: datetime
    ) -> BriefingSection:
        """Generate ingestion pipeline health report."""
        # Claims with evidence (successful ingestion)
        claims_with_evidence = db_session.execute(
            select(func.count())
            .select_from(Claim)
            .where(
                Claim.created_at >= week_start,
                Claim.created_at < week_end,
                Claim.evidence.isnot(None),
            )
        ).scalar()

        # Total claims this week
        total_claims_week = db_session.execute(
            select(func.count())
            .select_from(Claim)
            .where(Claim.created_at >= week_start, Claim.created_at < week_end)
        ).scalar()

        # Calculate success rate
        success_rate = (
            (claims_with_evidence / total_claims_week * 100)
            if total_claims_week > 0
            else 0.0
        )

        summary = f"""Ingestion pipeline processed {total_claims_week:,} claims with {success_rate:.1f}% evidence attachment rate. 
{total_claims_week - claims_with_evidence:,} claims pending evidence ingestion."""

        metrics = {
            "Total Claims Processed": BriefingMetrics(
                total_count=total_claims_week,
                period_change=0.0,  # Placeholder - would compare to previous week
                notable_events=[f"{total_claims_week:,} claims ingested"],
            ),
            "Claims With Evidence": BriefingMetrics(
                total_count=claims_with_evidence,
                period_change=0.0,
                notable_events=[f"{success_rate:.1f}% success rate"],
            ),
        }

        recommendations = []
        if success_rate < 95:
            recommendations.append(
                f"⚠️ Evidence attachment rate ({success_rate:.1f}%) below 95% SLO - investigate PRO adapter health"
            )
        if total_claims_week - claims_with_evidence > 100:
            recommendations.append(
                "📋 High volume of pending evidence - review dead letter queue"
            )

        return BriefingSection(
            title=self.title,
            summary=summary,
            metrics=metrics,
            recommendations=recommendations,
        )
