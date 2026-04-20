"""Type definitions for NL operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConfidenceLevel(Enum):
    """Query response confidence."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class QueryResponse:
    """Response to natural language query."""

    query: str
    answer: str
    data_sources: list[str]
    confidence: ConfidenceLevel
    as_of: datetime = field(default_factory=datetime.now)
    related_queries: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "answer": self.answer,
            "data_sources": self.data_sources,
            "confidence": self.confidence.value,
            "as_of": self.as_of.isoformat(),
            "related_queries": self.related_queries,
            "metadata": self.metadata,
        }

    def format_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            f"QUERY: {self.query}",
            f"DATA SOURCES: {', '.join(self.data_sources)}",
            f"AS OF: {self.as_of.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "ANSWER:",
            self.answer,
            "",
            f"CONFIDENCE: {self.confidence.value}",
        ]

        if self.related_queries:
            lines.append("")
            lines.append("RELATED QUERIES:")
            for related in self.related_queries:
                lines.append(f"  · {related}")

        return "\n".join(lines)
