"""Statement parsing with timeout enforcement.

Prevents DoS attacks from malformed or malicious statement files that could
cause parser to hang or consume excessive CPU/memory.
"""

from __future__ import annotations

import signal
from typing import Any, Callable

from xr7_common.logging import get_logger

logger = get_logger(__name__)


# Default timeout for statement parsing (seconds)
DEFAULT_PARSE_TIMEOUT = 30


class TimeoutConfig:
    """Configuration for parse timeout settings."""

    def __init__(self, timeout_seconds: int = DEFAULT_PARSE_TIMEOUT) -> None:
        """Initialize timeout configuration.

        Args:
            timeout_seconds: Timeout in seconds
        """
        self.timeout_seconds = timeout_seconds


class StatementParseTimeoutError(Exception):
    """Raised when statement parsing exceeds timeout threshold.

    Attributes:
        timeout_seconds: Timeout value that was exceeded
        message: Error message
    """

    def __init__(self, timeout_seconds: int, message: str | None = None) -> None:
        """Initialize timeout error.

        Args:
            timeout_seconds: Timeout that was exceeded
            message: Optional custom error message
        """
        self.timeout_seconds = timeout_seconds
        default_msg = f"Statement parsing timed out after {timeout_seconds} seconds"
        super().__init__(message or default_msg)


def _timeout_handler(signum, frame):
    """Signal handler for SIGALRM timeout."""
    raise StatementParseTimeoutError(
        DEFAULT_PARSE_TIMEOUT,
        f"Operation timed out after {DEFAULT_PARSE_TIMEOUT} seconds",
    )


def parse_with_timeout(
    func: Callable,
    *args,
    timeout_seconds: int = DEFAULT_PARSE_TIMEOUT,
    **kwargs,
) -> Any:
    """Execute a parsing function with timeout enforcement.

    Wraps the provided function in a timeout mechanism. If execution exceeds
    the timeout, raises StatementParseTimeoutError to prevent resource exhaustion.

    Args:
        func: Function to execute with timeout
        *args: Positional arguments for func
        timeout_seconds: Maximum execution time in seconds (default: 30)
        **kwargs: Keyword arguments for func

    Returns:
        Result from func execution

    Raises:
        StatementParseTimeoutError: If execution exceeds timeout

    Example::

        try:
            result = parse_with_timeout(
                parse_statement_file,
                file_content,
                artist_id,
                filename="statement.csv",
                timeout_seconds=30,
            )
        except StatementParseTimeoutError as e:
            logger.error(f"Parsing timed out: {e}")

    Notes:
        - Uses SIGALRM signal on Unix/Linux (not Windows compatible)
        - For Windows, consider using threading.Timer or multiprocessing
        - TODO: Replace with multiprocessing-based timeout for Windows support
    """
    # TODO: Add Windows-compatible timeout mechanism
    # Current implementation uses SIGALRM which is Unix-only
    # For production on Windows, use multiprocessing.Process with join(timeout)

    try:
        # Set up signal-based timeout (Unix only)
        if hasattr(signal, "SIGALRM"):
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout_seconds)

            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            finally:
                # Restore original handler
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows or no signal support: execute without timeout
            # TODO: Implement multiprocessing-based timeout for Windows
            logger.warning(
                "parse_timeout_not_supported_on_platform",
                extra={"timeout_seconds": timeout_seconds},
            )
            return func(*args, **kwargs)

    except StatementParseTimeoutError:
        # Re-raise timeout errors
        raise

    except Exception as exc:
        # Log other errors
        logger.error(
            "parse_with_timeout_unexpected_error",
            extra={"error": str(exc), "error_type": type(exc).__name__},
        )
        raise


def parse_with_timeout_multiprocessing(
    func: Callable,
    *args,
    timeout_seconds: int = DEFAULT_PARSE_TIMEOUT,
    **kwargs,
) -> Any:
    """Execute parsing with timeout using multiprocessing (Windows-compatible).

    Alternative to signal-based timeout that works on Windows.
    Uses multiprocessing.Process with join(timeout) to enforce timeout.

    Args:
        func: Function to execute
        *args: Positional arguments
        timeout_seconds: Timeout in seconds
        **kwargs: Keyword arguments

    Returns:
        Result from func

    Raises:
        StatementParseTimeoutError: If timeout exceeded

    Notes:
        - More overhead than signal-based approach
        - Works on Windows
        - Requires func to be picklable
        - Result passed via multiprocessing.Queue

    TODO: Make this the default implementation for cross-platform compatibility
    """
    from multiprocessing import Process, Queue

    def _worker(queue: Queue, func: Callable, args: tuple, kwargs: dict) -> None:
        """Worker function that puts result in queue."""
        try:
            result = func(*args, **kwargs)
            queue.put(("success", result))
        except Exception as exc:
            queue.put(("error", exc))

    result_queue: Queue = Queue()
    process = Process(target=_worker, args=(result_queue, func, args, kwargs))

    process.start()
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        # Timeout occurred
        process.terminate()
        process.join()
        raise StatementParseTimeoutError(timeout_seconds)

    # Get result from queue
    if not result_queue.empty():
        status, value = result_queue.get()
        if status == "success":
            return value
        else:
            raise value

    raise RuntimeError("Worker process completed but no result available")
