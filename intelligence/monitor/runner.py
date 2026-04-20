"""Monitor runner with timeout handling and graceful degradation."""

import logging
import platform
import signal
from contextlib import contextmanager
from datetime import datetime
from typing import Type

from intelligence.monitor.detector import Detector
from intelligence.monitor.detectors import (
    BillingDetector,
    ComplianceDetector,
    DependencyDetector,
    IngestionDetector,
    LedgerDetector,
    SloDetector,
    TenantIsolationDetector,
)
from intelligence.monitor.types import PlatformState

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Raised when detector exceeds timeout."""

    pass


@contextmanager
def timeout(seconds: int):
    """Context manager for detector execution timeout.

    Note: signal.alarm only works on Unix. On Windows, timeout is not enforced.
    """

    # Skip timeout on Windows (signal.alarm not supported)
    if platform.system() == "Windows":
        yield
        return

    def timeout_handler(signum, frame):
        raise TimeoutException(f"Detector exceeded {seconds}s timeout")

    # Set the signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)  # Disable alarm


class MonitorRunner:
    """Orchestrates detector execution with timeout and error handling."""

    def __init__(self, detectors: list[Type[Detector]] | None = None):
        """Initialize monitor with detectors.

        Args:
            detectors: List of detector classes to run. If None, uses all detectors.
        """
        if detectors is None:
            self.detectors = [
                LedgerDetector,
                BillingDetector,
                IngestionDetector,
                ComplianceDetector,
                SloDetector,
                TenantIsolationDetector,
                DependencyDetector,
            ]
        else:
            self.detectors = detectors

    def run(self, state: PlatformState) -> PlatformState:
        """Run all detectors and collect findings.

        Args:
            state: Platform state snapshot

        Returns:
            Updated state with findings and detector errors
        """
        logger.info(
            f"Monitor run starting with {len(self.detectors)} detectors",
            extra={"collected_at": state.collected_at.isoformat()},
        )

        for detector_class in self.detectors:
            detector = detector_class()
            detector_name = detector.name

            try:
                logger.info(
                    f"Running detector: {detector_name}",
                    extra={"detector": detector_name, "domain": detector.domain},
                )

                # Run detector with timeout
                with timeout(state.timeout_per_detector):
                    findings = detector.detect(state)

                if findings:
                    logger.warning(
                        f"Detector {detector_name} found {len(findings)} issue(s)",
                        extra={
                            "detector": detector_name,
                            "finding_count": len(findings),
                            "severities": [f.severity.value for f in findings],
                        },
                    )
                    state.findings.extend(findings)
                else:
                    logger.info(
                        f"Detector {detector_name} completed: no issues",
                        extra={"detector": detector_name},
                    )

            except TimeoutException:
                error_msg = (
                    f"Detector {detector_name} exceeded {state.timeout_per_detector}s timeout"
                )
                logger.error(error_msg, extra={"detector": detector_name})
                state.detector_errors[detector_name] = error_msg

            except Exception as e:
                error_msg = f"Detector {detector_name} failed: {type(e).__name__}: {str(e)}"
                logger.error(
                    error_msg,
                    extra={"detector": detector_name, "error_type": type(e).__name__},
                    exc_info=True,
                )
                state.detector_errors[detector_name] = error_msg

        logger.info(
            f"Monitor run completed: {len(state.findings)} findings, {len(state.detector_errors)} detector errors",
            extra={
                "total_findings": len(state.findings),
                "detector_errors": len(state.detector_errors),
                "severities": [f.severity.value for f in state.findings],
            },
        )

        return state

    def run_summary(self, state: PlatformState) -> dict:
        """Generate execution summary."""
        findings_by_severity = {}
        for finding in state.findings:
            severity = finding.severity.value
            findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

        findings_by_domain = {}
        for finding in state.findings:
            domain = finding.domain
            findings_by_domain[domain] = findings_by_domain.get(domain, 0) + 1

        return {
            "run_completed_at": datetime.utcnow().isoformat(),
            "platform_state_collected_at": state.collected_at.isoformat(),
            "total_detectors": len(self.detectors),
            "total_findings": len(state.findings),
            "findings_by_severity": findings_by_severity,
            "findings_by_domain": findings_by_domain,
            "detector_errors": state.detector_errors,
            "detectors_run": [d().name for d in self.detectors],
        }
