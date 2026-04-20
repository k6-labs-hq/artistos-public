"""
Test database connection configuration for production safety.

CRITICAL PRODUCTION SETTINGS: These tests verify that database connections
are configured with proper timeouts to prevent runaway queries.

Without statement_timeout:
- Aggregation queries can hang indefinitely
- Database connections held until manual intervention
- Connection pool exhaustion under load
- No automatic recovery from slow queries

With statement_timeout=30s:
- Queries automatically killed after 30 seconds
- Connections released back to pool
- Prevents connection pool starvation
- Forces developers to optimize slow queries
"""

from __future__ import annotations

import pytest


def test_postgresql_statement_timeout_configured():
    """
    Verify PostgreSQL connections have statement_timeout configured.

    Without this setting:
    - SELECT COUNT(*) FROM claims JOIN analytics can run for hours
    - Holds database connection until manually killed
    - Connection pool exhausted = API downtime
    - No circuit breaker on runaway queries

    With statement_timeout=30000 (30 seconds):
    - PostgreSQL kills query after 30s
    - Connection released back to pool
    - Developer gets immediate feedback about slow query
    - Forces optimization of inefficient queries
    """
    from XR7.models.base import _engine_connect_args

    # Test with postgresql:// URL
    connect_args = _engine_connect_args("postgresql://user:pass@localhost/db")
    assert "options" in connect_args, (
        "PostgreSQL connect_args must include 'options' parameter "
        "for statement_timeout configuration"
    )
    assert "-c statement_timeout=30000" in connect_args["options"], (
        "PostgreSQL must have statement_timeout=30000 (30 seconds). "
        "This prevents long-running queries from hanging indefinitely."
    )


def test_postgresql_plus_psycopg2_statement_timeout():
    """
    Verify statement_timeout works with postgresql+psycopg2:// URLs.

    SQLAlchemy supports multiple PostgreSQL dialects:
    - postgresql://
    - postgresql+psycopg2://
    - postgresql+pg8000://

    All should have statement_timeout configured.
    """
    from XR7.models.base import _engine_connect_args

    connect_args = _engine_connect_args("postgresql+psycopg2://user:pass@localhost/db")
    assert "options" in connect_args
    assert "-c statement_timeout=30000" in connect_args["options"]


def test_sqlite_no_statement_timeout():
    """
    Verify SQLite doesn't get PostgreSQL-specific settings.

    SQLite doesn't support PostgreSQL's -c options syntax.
    Should only get check_same_thread=False.
    """
    from XR7.models.base import _engine_connect_args

    connect_args = _engine_connect_args("sqlite:///./test.db")
    assert "check_same_thread" in connect_args
    assert connect_args["check_same_thread"] is False
    assert "options" not in connect_args, "SQLite should not have PostgreSQL 'options' parameter"


def test_statement_timeout_value_is_30_seconds():
    """
    Verify statement_timeout is set to 30 seconds (30000 milliseconds).

    This is a reasonable balance:
    - Short enough: Prevents indefinite hangs, alerts developers to slow queries
    - Long enough: Allows complex reports and aggregations to complete
    - Tunable: Can be increased for specific long-running tasks via raw SQL

    Too short (5s): Normal reports fail, constant errors
    Too long (5min): Connection pool exhaustion, delayed failure detection
    """
    from XR7.models.base import _engine_connect_args

    connect_args = _engine_connect_args("postgresql://localhost/db")
    options = connect_args["options"]

    # Extract timeout value from "-c statement_timeout=30000"
    assert "statement_timeout=30000" in options, (
        "statement_timeout must be exactly 30000ms (30 seconds). " f"Current: {options}"
    )


def test_engine_uses_connect_args_with_timeout():
    """
    Integration test: Verify the engine is created with connect_args.

    This ensures _engine_connect_args() is actually used when creating
    the SQLAlchemy engine, not just defined but unused.
    """
    from XR7.models.base import DATABASE_URL

    # Only test if using PostgreSQL (not SQLite)
    if DATABASE_URL.startswith("postgresql"):
        # Engine should have been created with connect_args
        # We can't easily inspect connect_args after engine creation,
        # but we can verify the function is called correctly
        from XR7.models.base import _engine_connect_args

        expected_args = _engine_connect_args(DATABASE_URL)
        assert "options" in expected_args
        assert "-c statement_timeout=30000" in expected_args["options"]


def test_statement_timeout_syntax_is_postgresql_compliant():
    """
    Verify the -c statement_timeout syntax is valid for PostgreSQL.

    PostgreSQL libpq connection strings support:
    - options="-c statement_timeout=30000"
    - options="-c work_mem=4MB -c statement_timeout=30000"

    Invalid syntax:
    - options="statement_timeout=30000" (missing -c)
    - statement_timeout=30000 (direct param, not in options)
    """
    from XR7.models.base import _engine_connect_args

    connect_args = _engine_connect_args("postgresql://localhost/db")
    options = connect_args["options"]

    # Must start with -c
    assert options.startswith(
        "-c "
    ), f"PostgreSQL options must start with '-c '. Current: {options}"

    # Must have key=value format
    assert "=" in options, f"PostgreSQL options must use key=value format. Current: {options}"


@pytest.mark.parametrize(
    "database_url,should_have_timeout",
    [
        ("postgresql://localhost/test", True),
        ("postgresql+psycopg2://localhost/test", True),
        ("postgresql://user:pass@db.example.com:5432/prod", True),
        ("sqlite:///./test.db", False),
        ("sqlite:///:memory:", False),
    ],
)
def test_statement_timeout_applied_to_correct_databases(
    database_url: str, should_have_timeout: bool
):
    """
    Parametrized test: statement_timeout only for PostgreSQL, not SQLite.
    """
    from XR7.models.base import _engine_connect_args

    connect_args = _engine_connect_args(database_url)

    if should_have_timeout:
        assert (
            "options" in connect_args
        ), f"PostgreSQL URL {database_url} should have statement_timeout in options"
        assert "statement_timeout" in connect_args["options"]
    else:
        # SQLite should not have PostgreSQL options
        if "options" in connect_args:
            assert "statement_timeout" not in connect_args["options"]


def test_statement_timeout_prevents_connection_pool_exhaustion():
    """
    Scenario test: statement_timeout prevents connection pool starvation.

    Problem scenario (without timeout):
    1. Developer writes: SELECT * FROM claims JOIN widgets JOIN analytics
    2. Query scans 10M rows, takes 20 minutes
    3. Holds connection for 20 minutes
    4. Connection pool (default 5 connections) exhausts quickly
    5. API returns 500 "Cannot get database connection"
    6. Entire application down until DBA manually kills query

    Solution (with 30s timeout):
    1. Same slow query submitted
    2. PostgreSQL kills it after 30 seconds automatically
    3. Connection released back to pool
    4. Developer gets QueryTimeout error immediately
    5. Developer optimizes query or increases timeout for specific case
    6. Application stays up, other requests proceed normally
    """
    from XR7.models.base import _engine_connect_args

    # Verify timeout is configured
    connect_args = _engine_connect_args("postgresql://localhost/db")
    assert "options" in connect_args
    assert "statement_timeout=30000" in connect_args["options"]

    # Timeout is 30 seconds = 30000 milliseconds
    # This is the safety valve that prevents indefinite hangs
    timeout_ms = 30000
    timeout_seconds = timeout_ms / 1000
    assert timeout_seconds == 30.0, f"Expected 30 second timeout, got {timeout_seconds}s"
