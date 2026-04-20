"""Recovery and exposure query handler."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from intelligence.nlops.handler import QueryHandler
from intelligence.nlops.types import ConfidenceLevel, QueryResponse
from XR7.models.claim import Claim


class RecoveryQueryHandler(QueryHandler):
    """Handles queries about recovery exposure and black box amounts."""

    def can_handle(self, query: str) -> bool:
        """Check if query is about recovery/exposure."""
        keywords = [
            "black box",
            "exposure",
            "recovery",
            "recovered",
            "amount",
            "revenue",
        ]
        return any(keyword in query for keyword in keywords)

    def handle(self, query: str, db_session: Session) -> QueryResponse:
        """Handle recovery/exposure query."""
        # Get identified claims (black box exposure)
        identified_result = db_session.execute(
            select(func.count(), func.sum(Claim.recovered_amount))
            .select_from(Claim)
            .where(Claim.status == "IDENTIFIED")
        ).one()

        identified_count, identified_amount = identified_result
        identified_count = identified_count or 0
        identified_amount = identified_amount or 0.0

        # Get resolved claims
        resolved_result = db_session.execute(
            select(func.count(), func.sum(Claim.recovered_amount))
            .select_from(Claim)
            .where(Claim.status == "RESOLVED")
        ).one()

        resolved_count, resolved_amount = resolved_result
        resolved_count = resolved_count or 0
        resolved_amount = resolved_amount or 0.0

        # Build answer
        answer_lines = [
            f"**Black Box Exposure:** ${identified_amount:,.2f} across {identified_count:,} identified claims",
            f"**Resolved Revenue:** ${resolved_amount:,.2f} across {resolved_count:,} resolved claims",
            f"**Total Potential Revenue:** ${identified_amount + resolved_amount:,.2f}",
        ]

        return QueryResponse(
            query=query,
            answer="\n".join(answer_lines),
            data_sources=["claims.recovered_amount", "claims.status"],
            confidence=ConfidenceLevel.HIGH,
            related_queries=[
                "Show top 10 artists by recovery amount",
                "What is the average recovery per claim?",
                "How many claims are pending review?",
            ],
        )
