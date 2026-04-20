"""Dependency vulnerability and deprecation detector."""

from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, PlatformState


class DependencyDetector(Detector):
    """Monitors dependency health: CVEs, deprecations, and API version warnings."""

    @property
    def name(self) -> str:
        return "dependency-health-detector"

    @property
    def domain(self) -> str:
        return "security"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        # In production, integrate with:
        # - pip-audit for Python CVEs
        # - npm audit for frontend dependencies
        # - Dependabot alerts
        # - External API version deprecation notices (Stripe, Trolley, Anthropic)

        # Example detections:
        # - CVE with severity HIGH or CRITICAL in production dependencies
        # - Deprecated API version in use with sunset date within 90 days
        # - Security patch available for critical dependency

        return findings
