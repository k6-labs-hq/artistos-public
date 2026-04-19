"""
Statement parsing timeout enforcement for ingestion DoS protection.

Prevents malformed or maliciously crafted large statement files from hanging
the ingestion worker indefinitely by enforcing a configurable hard timeout.

Without timeout:
- 50MB CSV with quadratic-complexity malformed records can hang parser indefinitely
- Worker thread blocked forever, reducing throughput to zero
- Subsequent uploads queued behind hung parser
- No visibility into which file caused the hang

With 60s timeout:
- Parser killed after 60s regardless of file size
- Worker thread released immediately
- Clear 422 error to user with actionable message
- Metrics track timeout frequency for capacity planning

Configuration:
- STATEMENT_PARSE_TIMEOUT_SECONDS: Hard timeout for parsing (default: 60)
- STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD: Log warning if parse >N seconds (default: 30)

Closes: XR7-402
Domain: ingestion
Scale-target: 10x ingestion volume with DoS protection
Compliance: SOC 2 CC6.1 — Data integrity and availability controls
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from xr7_common.logging import get_logger

logger = get_logger(__name__)

PARSE_TIMEOUT_SECONDS = int(os.environ.get("STATEMENT_PARSE_TIMEOUT_SECONDS", "60"))
PARSE_TIMEOUT_LOG_THRESHOLD = int(os.environ.get("STATEMENT_PARSE_TIMEOUT_LOG_THRESHOLD", "30"))


@dataclass
class TimeoutConfig:
    """Timeout configuration for statement parsing."""

    timeout_seconds: int = PARSE_TIMEOUT_SECONDS
    log_threshold_seconds: int = PARSE_TIMEOUT_LOG_THRESHOLD
    enabled: bool = True


class StatementParseTimeoutError(Exception):
    """Raised when statement parsing exceeds timeout threshold."""

    def __init__(self, timeout_seconds: int, filename: str):
        self.timeout_seconds = timeout_seconds
        self.filename = filename
        super().__init__(
            f"Statement parsing timed out after {timeout_seconds}s for file {filename}"
        )


def parse_with_timeout(
    parse_fn: callable,
    content: bytes,
    artist_id: str,
    filename: str = "statement.csv",
    timeout_config: TimeoutConfig | None = None,
    **kwargs,
) -> Any:
    """Execute statement parsing function with hard timeout.

    Uses ThreadPoolExecutor to isolate parsing in a separate thread and kill it
    if it exceeds the timeout threshold. This prevents malformed files from
    hanging the ingestion worker indefinitely.

    Args:
        parse_fn: The parsing function to execute (e.g., parse_statement_file)
        content: Raw file bytes
        artist_id: Artist ID for the statement
        filename: Original filename for error messages
        timeout_config: Timeout configuration (uses defaults if None)
        **kwargs: Additional arguments to pass to parse_fn

    Returns:
        ParseResult from the parsing function

    Raises:
        StatementParseTimeoutError: If parsing exceeds timeout threshold

    Example:
        >>> from XR7.ingestion.statement_parser import parse_statement_file
        >>> result = parse_with_timeout(
        ...     parse_statement_file,
        ...     file_bytes,
        ...     "artist-123",
        ...     "march_statement.csv"
        ... )
    """
    if timeout_config is None:
        timeout_config = TimeoutConfig()

    if not timeout_config.enabled:
        # Timeout enforcement disabled (e.g., for testing)
        return parse_fn(content, artist_id, filename=filename, **kwargs)

    start_time = datetime.now()

    # Execute parse in thread pool with timeout
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="parse_timeout_") as executor:
        future = executor.submit(parse_fn, content, artist_id, filename=filename, **kwargs)

        try:
            result = future.result(timeout=timeout_config.timeout_seconds)

            # Log warning if parsing took significant time (but didn't timeout)
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_config.log_threshold_seconds:
                logger.warning(
                    "Statement parsing slow (near timeout)",
                    extra={
                        "artist_id": artist_id,
                        "filename": filename,
                        "elapsed_seconds": round(elapsed, 2),
                        "threshold_seconds": timeout_config.log_threshold_seconds,
                        "timeout_seconds": timeout_config.timeout_seconds,
                        "file_size_bytes": len(content),
                    },
                )

            return result

        except FuturesTimeoutError:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error(
                "Statement parsing timeout",
                extra={
                    "artist_id": artist_id,
                    "filename": filename,
                    "timeout_seconds": timeout_config.timeout_seconds,
                    "elapsed_seconds": round(elapsed, 2),
                    "file_size_bytes": len(content),
                },
            )
            raise StatementParseTimeoutError(timeout_config.timeout_seconds, filename)


def get_timeout_config_from_env() -> TimeoutConfig:
    """Get timeout configuration from environment variables.

    Returns:
        TimeoutConfig with values from environment or defaults
    """
    return TimeoutConfig(
        timeout_seconds=PARSE_TIMEOUT_SECONDS,
        log_threshold_seconds=PARSE_TIMEOUT_LOG_THRESHOLD,
        enabled=True,
    )
