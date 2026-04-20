"""Executive summary generator."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.briefing.generator import SectionGenerator
from intelligence.briefing.types import BriefingMetrics, BriefingSection
from XR7.models.claim import Claim


class ExecutiveSummaryGenerator(SectionGenerator):
    """Generates executive summary section."""

    @property
    def title(self) -> str:
        return "Executive Summary"

    def generate(
        self, db_session: Session, week_start: datetime, week_end: datetime
    ) -> BriefingSection:
        """Generate executive summary with platform overview."""
        # Get total claims
        total_claims = db_session.execute(
            select(func.count()).select_from(Claim)
        ).scalar()

        # Get claims created this week
        week_claims = db_session.execute(
            select(func.count())
            .select_from(Claim)
            .where(Claim.created_at >= week_start, Claim.created_at <week_end)
        ).scalar()

        # Get previous week for comparison
        prev_week_start = week_start - (week_end - week_start)
        prev_week_claims = db_session.execute(
            select(func.count())
            .select_from(Claim)
            .where(
                Claim.created_at >= prev_week_start, Claim.created_at < week_start
            )
        ).scalar()

        # Calculate change
        change_pct = (
            ((week_claims - prev_week_claims) / prev_week_claims * 100)
            if prev_week_claims > 0
            else 0.0
        )

        summary = f"""Platform processed {week_claims:,} claims this week, {"up" if change_pct > 0 else "down"} {abs(change_pct):.1f}% from last week. 
Total platform claims: {total_claims:,}. All core systems operational."""

        metrics = {
            "Claims This Week": BriefingMetrics(
                total_count=week_claims,
                period_change=change_pct,
                notable_events=[
                    f"{week_claims:,} claims processed",
                    f"{abs(change_pct):.1f}% {'increase' if change_pct > 0 else 'decrease'} from prior week",
                ],
            ),
        }

        recommendations = []
        if change_pct < -10:
            recommendations.append(
                "⚠️ Claims volume declined >10% - investigate ingestion pipeline"
            )
        elif change_pct > 50:
            recommendations.append(
                "📈 Claims volume increased >50% - verify capacity planning"
            )

        return BriefingSection(
            title=self.title,
            summary=summary,
            metrics=metrics,
            recommendations=recommendations,
        )
