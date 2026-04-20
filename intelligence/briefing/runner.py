"""Weekly briefing runner."""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from intelligence.briefing.generators.billing_report import BillingReportGenerator
from intelligence.briefing.generators.compliance_report import ComplianceReportGenerator
from intelligence.briefing.generators.executive_summary import ExecutiveSummaryGenerator
from intelligence.briefing.generators.ingestion_report import IngestionReportGenerator
from intelligence.briefing.types import BriefingData

logger = logging.getLogger(__name__)


class BriefingRunner:
    """Orchestrates weekly intelligence briefing generation."""

    def __init__(self):
        """Initialize briefing runner with all generators."""
        self.generators = [
            ExecutiveSummaryGenerator(),
            IngestionReportGenerator(),
            BillingReportGenerator(),
            ComplianceReportGenerator(),
        ]

    def generate(
        self,
        db_session: Session,
        week_start: datetime | None = None,
        week_end: datetime | None = None,
    ) -> BriefingData:
        """
        Generate weekly briefing.

        Args:
            db_session: Database session
            week_start: Start of week (defaults to last Monday)
            week_end: End of week (defaults to last Sunday)

        Returns:
            BriefingData with all sections
        """
        # Default to last complete week
        if week_start is None or week_end is None:
            today = datetime.now(timezone.utc)
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday + 7)
            week_start = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)

        logger.info(f"Generating weekly briefing for {week_start} to {week_end}")

        sections = []
        for generator in self.generators:
            try:
                logger.info(f"Generating section: {generator.title}")
                section = generator.generate(db_session, week_start, week_end)
                sections.append(section)
            except Exception as e:
                logger.error(f"Generator {generator.title} failed: {e}", exc_info=True)
                sections.append(generator._handle_error(e))

        return BriefingData(week_start=week_start, week_end=week_end, sections=sections)

    def save_briefing(self, briefing: BriefingData, output_dir: Path | str = "docs/briefings"):
        """
        Save briefing to markdown file.

        Args:
            briefing: BriefingData to save
            output_dir: Directory to save briefing (default: docs/briefings/)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{briefing.week_start.strftime('%Y-%m-%d')}.md"
        filepath = output_path / filename

        logger.info(f"Saving briefing to {filepath}")
        with open(filepath, "w") as f:
            f.write(briefing.to_markdown())

        logger.info(f"Briefing saved successfully")
        return filepath
