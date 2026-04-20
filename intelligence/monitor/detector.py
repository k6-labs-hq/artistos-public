"""Base detector interface for platform health monitoring."""

from abc import ABC, abstractmethod

from intelligence.monitor.types import Finding, PlatformState


class Detector(ABC):
    """Base class for all platform health detectors.

    Each detector analyzes a specific domain of platform health and returns
    a list of findings. Detectors must be:
    - Isolated: no shared state with other detectors
    - Testable: accept PlatformState, return list of findings
    - Bounded: respect timeout limits
    - Graceful: handle failures without crashing the monitor
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique detector name for logging and issue filing."""
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this detector monitors (e.g., 'billing', 'compliance')."""
        pass

    @abstractmethod
    def detect(self, state: PlatformState) -> list[Finding]:
        """Analyze platform state and return findings.

        Args:
            state: Current platform state snapshot with database access

        Returns:
            List of findings (empty if no issues detected)

        Raises:
            Exception: Detector failures are caught by the monitor runner
        """
        pass
