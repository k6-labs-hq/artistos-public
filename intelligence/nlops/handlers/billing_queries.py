"""Billing status query handler."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.nlops.handler import QueryHandler
from intelligence.nlops.types import ConfidenceLevel, QueryResponse
from XR7.models.claim import Claim


class BillingQueryHandler(QueryHandler):
    """Handles queries about billing and fees."""

    def can_handle(self, query: str) -> bool:
        """Check if query is about billing."""
        keywords = ["billing", "fee", "fees", "trolley", "payment", "invoice"]
        return any(keyword in query for keyword in keywords)

    def handle(self, query: str, db_session: Session) -> QueryResponse:
        """Handle billing query."""
        # Get claims resolved this week
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        weekly_result = db_session.execute(
            select(func.count(), func.sum(Claim.recovered_amount))
            .select_from(Claim)
            .where(Claim.resolved_at >= week_ago, Claim.status == "RESOLVED")
        ).one()

        count, amount = weekly_result
        count = count or 0
        amount = amount or 0.0

        # Calculate estimated fees (placeholder - would query actual fee records)
        avg_fee_rate = 12.0
        estimated_fees = amount * (avg_fee_rate / 100)

        answer_lines = [
            f"**Claims Resolved (Last 7 Days):** {count:,} claims",
            f"**Revenue Recovered:** ${amount:,.2f}",
            f"**Estimated Fee Revenue:** ${estimated_fees:,.2f} (at {avg_fee_rate}% avg rate)",
        ]

        return QueryResponse(
            query=query,
            answer="\n".join(answer_lines),
            data_sources=["claims.resolved_at", "claims.recovered_amount"],
            confidence=ConfidenceLevel.HIGH,
            related_queries=[
                "What is Trolley payment success rate?",
                "Show fee breakdown by artist tier",
                "How many artists are in Founders Circle?",
            ],
        )
