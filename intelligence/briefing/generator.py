"""Base generator for briefing sections."""

from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Session

from intelligence.briefing.types import BriefingSection


class SectionGenerator(ABC):
    """Base class for briefing section generators."""

    @property
    @abstractmethod
    def title(self) -> str:
        """Section title."""
        pass

    @abstractmethod
    def generate(
        self, db_session: Session, week_start: datetime, week_end: datetime
    ) -> BriefingSection:
        """
        Generate briefing section for the specified week.

        Args:
            db_session: Database session
            week_start: Start of the week
            week_end: End of the week

        Returns:
            BriefingSection with summary, metrics, and recommendations
        """
        pass

    def _handle_error(self, error: Exception) -> BriefingSection:
        """Create error section when generator fails."""
        return BriefingSection(
            title=self.title,
            summary=f"⚠️ Unable to generate section: {str(error)}",
            recommendations=[
                "Investigate section generator failure",
                "Check database connectivity and data availability",
            ],
        )
