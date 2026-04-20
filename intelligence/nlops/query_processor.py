"""Natural language query processor."""

import logging
from sqlalchemy.orm import Session

from intelligence.nlops.handlers.billing_queries import BillingQueryHandler
from intelligence.nlops.handlers.recovery_queries import RecoveryQueryHandler
from intelligence.nlops.types import ConfidenceLevel, QueryResponse

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Processes natural language queries and routes to appropriate handlers."""

    def __init__(self):
        """Initialize query processor with all handlers."""
        self.handlers = [
            RecoveryQueryHandler(),
            BillingQueryHandler(),
        ]

    def process(self, query: str, db_session: Session) -> QueryResponse:
        """
        Process natural language query.

        Args:
            query: Natural language question
            db_session: Database session

        Returns:
            QueryResponse with answer and metadata
        """
        query_lower = query.lower()

        # Simple keyword-based routing (in production, use LLM for intent classification)
        for handler in self.handlers:
            if handler.can_handle(query_lower):
                try:
                    logger.info(f"Routing query to {handler.__class__.__name__}")
                    return handler.handle(query, db_session)
                except Exception as e:
                    logger.error(
                        f"Handler {handler.__class__.__name__} failed: {e}",
                        exc_info=True,
                    )
                    return QueryResponse(
                        query=query,
                        answer=f"Unable to process query: {str(e)}",
                        data_sources=[],
                        confidence=ConfidenceLevel.LOW,
                        related_queries=[],
                    )

        # No handler found
        return QueryResponse(
            query=query,
            answer="I don't understand that query. Try asking about recovery exposure, billing status, or platform health.",
            data_sources=[],
            confidence=ConfidenceLevel.LOW,
            related_queries=[
                "What is our black box exposure?",
                "Show me claims resolved this week",
                "How many artists are enrolled?",
            ],
        )
