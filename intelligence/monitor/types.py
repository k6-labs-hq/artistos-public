"""Type definitions for the self-monitoring system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FindingSeverity(str, Enum):
    """Severity levels for monitor findings."""

    P0 = "P0"  # Critical - platform non-functional or data integrity at risk
    P1 = "P1"  # High - enterprise readiness or compliance gap
    P2 = "P2"  # Medium - scale bottleneck or degraded performance
    P3 = "P3"  # Low - toil or suboptimal patterns


@dataclass
class Finding:
    """A monitor finding that may result in a GitHub issue."""

    detector: str
    severity: FindingSeverity
    domain: str
    title: str
    description: str
    expected_behavior: str
    investigation_path: list[str]
    runbook_link: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_github_issue_body(self) -> str:
        """Format finding as GitHub issue body."""
        lines = [
            f"**Detected by:** {self.detector}",
            f"**Severity:** {self.severity.value}",
            f"**Domain:** {self.domain}",
            f"**Detected at:** {self.detected_at.isoformat()}Z",
            "",
            "## Problem",
            self.description,
            "",
            "## Expected behavior",
            self.expected_behavior,
            "",
            "## Suggested investigation path",
        ]

        for i, step in enumerate(self.investigation_path, 1):
            lines.append(f"{i}. {step}")

        if self.runbook_link:
            lines.extend(["", "## Runbook", self.runbook_link])

        if self.metadata:
            lines.extend(["", "## Additional context", "```json"])
            import json

            lines.append(json.dumps(self.metadata, indent=2))
            lines.append("```")

        lines.extend(
            [
                "",
                "## Auto-filed by",
                "XR7 Self-Monitor v1.0 — this issue was created automatically.",
                "Do not close without resolving the underlying condition.",
            ]
        )

        return "\n".join(lines)

    def to_github_issue_title(self) -> str:
        """Format finding as GitHub issue title."""
        return f"[{self.severity.value}] {self.domain}: {self.title}"

    def to_github_labels(self) -> list[str]:
        """Get GitHub labels for this finding."""
        return [
            "auto-filed",
            "monitor",
            self.domain.lower(),
            self.severity.value.lower(),
        ]


@dataclass
class PlatformState:
    """Snapshot of platform state for detector analysis."""

    # Database connection for queries
    db_session: Any

    # Monitor execution context
    collected_at: datetime = field(default_factory=lambda: datetime.utcnow())
    timeout_per_detector: int = 30  # seconds

    # Detector results (populated during run)
    findings: list[Finding] = field(default_factory=list)
    detector_errors: dict[str, str] = field(default_factory=dict)
