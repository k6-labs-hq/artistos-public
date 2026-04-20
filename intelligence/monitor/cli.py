"""CLI interface for XR7 platform monitor."""

import argparse
import json
import logging
import sys
from datetime import datetime

from sqlalchemy.orm import Session

from intelligence.monitor.github_service import GitHubIssueService
from intelligence.monitor.runner import MonitorRunner
from intelligence.monitor.types import PlatformState
from XR7.models.base import SessionLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run_monitor(
    db_session: Session,
    file_issues: bool = False,
    dry_run: bool = False,
) -> dict:
    """Run platform monitor and optionally file GitHub issues.

    Args:
        db_session: Database session for platform queries
        file_issues: If True, file GitHub issues for findings
        dry_run: If True, simulate issue filing without creating them

    Returns:
        Summary dict with findings and execution metadata
    """
    logger.info("Starting XR7 platform monitor run")

    # Collect platform state
    state = PlatformState(
        db_session=db_session,
        collected_at=datetime.utcnow(),
        timeout_per_detector=30,
    )

    # Run all detectors
    runner = MonitorRunner()
    state = runner.run(state)

    # Generate summary
    summary = runner.run_summary(state)

    # File GitHub issues if requested
    if file_issues:
        github = GitHubIssueService(dry_run=dry_run)
        issue_results = github.file_findings(state.findings)
        summary["issues_filed"] = {
            "total_attempted": len(state.findings),
            "filed": sum(1 for url in issue_results.values() if url),
            "skipped": sum(1 for url in issue_results.values() if not url),
            "results": issue_results,
        }

    return summary


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="XR7 Platform Self-Monitor - Automated health detection and issue filing"
    )
    parser.add_argument(
        "--file-issues",
        action="store_true",
        help="File GitHub issues for findings (requires gh CLI)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate issue filing without creating them",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    try:
        # Create database session
        db = SessionLocal()

        # Run monitor
        summary = run_monitor(
            db_session=db,
            file_issues=args.file_issues,
            dry_run=args.dry_run,
        )

        # Output results
        if args.output == "json":
            print(json.dumps(summary, indent=2))
        else:
            print("\n" + "=" * 80)
            print("XR7 PLATFORM MONITOR - RUN SUMMARY")
            print("=" * 80)
            print(f"Completed at: {summary['run_completed_at']}")
            print(f"Platform state from: {summary['platform_state_collected_at']}")
            print(f"\nDetectors run: {summary['total_detectors']}")
            print(f"Total findings: {summary['total_findings']}")

            if summary["findings_by_severity"]:
                print("\nFindings by severity:")
                for severity, count in sorted(summary["findings_by_severity"].items()):
                    print(f"  {severity}: {count}")

            if summary["findings_by_domain"]:
                print("\nFindings by domain:")
                for domain, count in sorted(summary["findings_by_domain"].items()):
                    print(f"  {domain}: {count}")

            if summary["detector_errors"]:
                print(f"\n⚠️  Detector errors: {len(summary['detector_errors'])}")
                for detector, error in summary["detector_errors"].items():
                    print(f"  {detector}: {error}")

            if "issues_filed" in summary:
                filed = summary["issues_filed"]["filed"]
                skipped = summary["issues_filed"]["skipped"]
                print(f"\nGitHub issues: {filed} filed, {skipped} skipped (duplicates)")

            print("=" * 80 + "\n")

        # Exit with non-zero code if P0 findings detected
        if summary.get("findings_by_severity", {}).get("P0", 0) > 0:
            logger.warning("P0 findings detected - exiting with code 1")
            sys.exit(1)

        db.close()

    except Exception as e:
        logger.error(f"Monitor run failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
