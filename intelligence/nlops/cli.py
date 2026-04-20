"""CLI interface for NL operations."""

import argparse
import json
import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from intelligence.nlops.query_processor import QueryProcessor


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Query XR7 platform in natural language")
    parser.add_argument("query", nargs="+", help="Your question")
    parser.add_argument(
        "--db-url", help="Database URL (defaults to environment DATABASE_URL)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get database URL
    db_url = args.db_url
    if not db_url:
        import os

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("ERROR: DATABASE_URL not set and --db-url not provided", file=sys.stderr)
            sys.exit(1)

    # Create database session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()

    try:
        # Process query
        query = " ".join(args.query)
        processor = QueryProcessor()
        response = processor.process(query, db_session)

        # Output response
        if args.format == "json":
            print(json.dumps(response.to_dict(), indent=2))
        else:
            print(response.format_text())

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
