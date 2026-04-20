"""GitHub issue filing service with deduplication."""

import logging
import subprocess
from typing import Optional

from intelligence.monitor.types import Finding

logger = logging.getLogger(__name__)


class GitHubIssueService:
    """Service for filing GitHub issues from monitor findings."""

    def __init__(self, repo: str = "k6-labs-hq/ArtistOS", dry_run: bool = False):
        """Initialize GitHub issue service.

        Args:
            repo: GitHub repository in format 'owner/repo'
            dry_run: If True, log issues without filing them
        """
        self.repo = repo
        self.dry_run = dry_run

    def file_finding(self, finding: Finding) -> Optional[str]:
        """File a GitHub issue for a finding.

        Args:
            finding: Monitor finding to file

        Returns:
            Issue URL if filed, None if skipped or failed
        """
        # Check if issue already exists
        if self._issue_exists(finding):
            logger.info(
                "Skipping finding: similar issue already open",
                extra={"detector": finding.detector, "title": finding.title},
            )
            return None

        title = finding.to_github_issue_title()
        body = finding.to_github_issue_body()
        labels = finding.to_github_labels()

        if self.dry_run:
            logger.info(
                "DRY RUN: Would file issue",
                extra={
                    "title": title,
                    "labels": labels,
                    "detector": finding.detector,
                },
            )
            return f"https://github.com/{self.repo}/issues/DRY-RUN"

        try:
            # Use GitHub CLI to create issue
            label_args = []
            for label in labels:
                label_args.extend(["--label", label])

            cmd = [
                "gh",
                "issue",
                "create",
                "--repo",
                self.repo,
                "--title",
                title,
                "--body",
                body,
            ] + label_args

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            issue_url = result.stdout.strip()
            logger.info(
                "Filed GitHub issue",
                extra={
                    "issue_url": issue_url,
                    "detector": finding.detector,
                    "severity": finding.severity.value,
                },
            )
            return issue_url

        except subprocess.CalledProcessError as e:
            logger.error(
                f"Failed to file GitHub issue: {e.stderr}",
                extra={"detector": finding.detector, "error": e.stderr},
            )
            return None
        except FileNotFoundError:
            logger.error(
                "GitHub CLI (gh) not installed or not in PATH. Install from https://cli.github.com/"
            )
            return None

    def _issue_exists(self, finding: Finding) -> bool:
        """Check if similar issue already exists (deduplication).

        Args:
            finding: Finding to check

        Returns:
            True if similar open issue exists
        """
        if self.dry_run:
            return False

        try:
            # Search for open issues with same labels
            search_query = f"is:open is:issue label:auto-filed label:{finding.domain.lower()} in:title {finding.title[:50]}"

            cmd = [
                "gh",
                "issue",
                "list",
                "--repo",
                self.repo,
                "--search",
                search_query,
                "--limit",
                "5",
                "--json",
                "title,url",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip() == "[]":
                return False

            # Parse JSON response
            import json

            issues = json.loads(result.stdout)

            # Check if any issue title is similar
            finding_title_lower = finding.title.lower()
            for issue in issues:
                if finding_title_lower in issue["title"].lower():
                    logger.info(
                        f"Found similar open issue: {issue['url']}",
                        extra={
                            "existing_issue": issue["url"],
                            "finding_title": finding.title,
                        },
                    )
                    return True

            return False

        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            # If we can't check, err on side of caution and don't file
            logger.warning(
                "Could not check for existing issues - assuming one exists to avoid duplicates"
            )
            return True

    def file_findings(self, findings: list[Finding]) -> dict[str, Optional[str]]:
        """File GitHub issues for multiple findings.

        Args:
            findings: List of findings to file

        Returns:
            Dict mapping finding detector+title to issue URL (or None if skipped)
        """
        results = {}
        for finding in findings:
            key = f"{finding.detector}:{finding.title}"
            results[key] = self.file_finding(finding)
        return results
