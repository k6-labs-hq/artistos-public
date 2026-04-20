"""Natural language operations interface."""

__version__ = "1.0.0"

from intelligence.nlops.query_processor import QueryProcessor
from intelligence.nlops.types import QueryResponse

__all__ = ["QueryProcessor", "QueryResponse"]
