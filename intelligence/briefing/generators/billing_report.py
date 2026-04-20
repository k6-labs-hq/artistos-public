"""Billing report generator."""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.briefing.generator import SectionGenerator
from intelligence.briefing.types import BriefingMetrics, BriefingSection
from XR7.models.claim import Claim


class BillingReportGenerator(SectionGenerator):
    """Generates billing and revenue report."""

    @property
    def title(self) -> str:
        return "Billing & Revenue"

    def generate(
        self, db_session: Session, week_start: datetime, week_end: datetime
    ) -> BriefingSection:
        """Generate billing and revenue report."""
        # Claims resolved this week
        resolved_claims = db_session.execute(
            select(func.count(), func.sum(Claim.recovered_amount))
            .select_from(Claim)
            .where(
                Claim.resolved_at >= week_start,
                Claim.resolved_at < week_end,
                Claim.status == "RESOLVED",
            )
        ).one()

        count, total_recovered = resolved_claims
        count = count or 0
        total_recovered = total_recovered or 0.0

        # Calculate contingency fees (placeholder - would query actual fee records)
        avg_fee_rate = 12.0  # Average contingency fee percentage
        estimated_fees = total_recovered * (avg_fee_rate / 100)

        summary = f"""Platform recovered ${total_recovered:,.2f} across {count:,} resolved claims this week. 
Estimated contingency fee revenue: ${estimated_fees:,.2f} at {avg_fee_rate}% average rate."""

        metrics = {
            "Claims Resolved": BriefingMetrics(
                total_count=count,
                period_change=0.0,
                notable_events=[f"{count:,} claims resolved"],
            ),
            "Revenue Recovered": BriefingMetrics(
                total_count=int(total_recovered),
                period_change=0.0,
                notable_events=[f"${total_recovered:,.2f} total"],
            ),
            "Fee Revenue": BriefingMetrics(
                total_count=int(estimated_fees),
                period_change=0.0,
                notable_events=[f"${estimated_fees:,.2f} estimated"],
            ),
        }

        recommendations = []
        if count < 10:
            recommendations.append(
                "⚠️ Low weekly resolution volume - review recovery workflow efficiency"
            )
        if total_recovered > 100000:
            recommendations.append(
                "🎯 High-value week - ensure Trolley payment processing capacity"
            )

        return BriefingSection(
            title=self.title,
            summary=summary,
            metrics=metrics,
            recommendations=recommendations,
        )
