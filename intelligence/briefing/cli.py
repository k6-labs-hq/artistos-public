"""CLI interface for briefing system."""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from intelligence.briefing.runner import BriefingRunner


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Generate weekly intelligence briefing"
    )
    parser.add_argument(
        "--week-start",
        type=parse_date,
        help="Week start date (YYYY-MM-DD). Defaults to last Monday.",
    )
    parser.add_argument(
        "--week-end",
        type=parse_date,
        help="Week end date (YYYY-MM-DD). Defaults to last Sunday.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs/briefings",
        help="Output directory for briefing (default: docs/briefings)",
    )
    parser.add_argument(
        "--db-url",
        help="Database URL (defaults to environment DATABASE_URL)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    # Get database URL
    db_url = args.db_url
    if not db_url:
        import os

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL not set and --db-url not provided")
            sys.exit(1)

    # Create database session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()

    try:
        # Generate briefing
        runner = BriefingRunner()
        logger.info("Generating weekly briefing...")
        briefing = runner.generate(db_session, args.week_start, args.week_end)

        # Save briefing
        output_path = runner.save_briefing(briefing, args.output)
        logger.info(f"✅ Briefing generated successfully")
        logger.info(f"📄 Saved to: {output_path}")

        # Print summary
        print("\n" + "=" * 80)
        print(f"Weekly Briefing: {briefing.week_start.date()} to {briefing.week_end.date()}")
        print("=" * 80)
        for section in briefing.sections:
            print(f"\n{section.title}")
            print("-" * len(section.title))
            print(section.summary)
            if section.recommendations:
                print(f"\nRecommendations: {len(section.recommendations)}")
        print("\n" + "=" * 80)

    except Exception as e:
        logger.error(f"Failed to generate briefing: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
