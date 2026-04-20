"""Base query handler."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from intelligence.nlops.types import QueryResponse


class QueryHandler(ABC):
    """Base class for query handlers."""

    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """
        Check if this handler can process the query.

        Args:
            query: Normalized query string (lowercase)

        Returns:
            True if handler can process this query
        """
        pass

    @abstractmethod
    def handle(self, query: str, db_session: Session) -> QueryResponse:
        """
        Handle the query and generate response.

        Args:
            query: Original query string
            db_session: Database session

        Returns:
            QueryResponse with answer and metadata
        """
        pass
