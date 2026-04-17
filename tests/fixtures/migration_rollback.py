"""
Migration rollback test fixtures.

Provides pytest fixtures for testing Alembic upgrade / downgrade cycles
against a temporary PostgreSQL-compatible SQLite database.  The fixtures
verify that:

  1. Every migration can be applied (``upgrade head``).
  2. Every migration can be rolled back to the previous revision (``downgrade -1``).
  3. A full downgrade to ``base`` succeeds.

Usage::

    from tests.fixtures.migration_rollback import alembic_runner, alembic_engine

    def test_all_migrations_upgrade_and_downgrade(alembic_runner):
        alembic_runner.run_migrations_up()
        alembic_runner.run_migrations_down()
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _REPO_ROOT / "alembic.ini"


def _make_alembic_config(db_url: str) -> AlembicConfig:
    """Return an Alembic Config pointed at the repo alembic.ini with the given DB URL."""
    cfg = AlembicConfig(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", db_url)
    # Override script_location so it resolves relative to repo root
    cfg.set_main_option("script_location", str(_REPO_ROOT / "alembic"))
    return cfg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def migration_db_url(tmp_path_factory) -> str:
    """Return a SQLite DB URL in a temporary directory.

    Override this fixture in your test module to use a real PostgreSQL URL
    (e.g. via ``MIGRATION_TEST_DB_URL`` env var) for production-fidelity checks.
    """
    env_url = os.environ.get("MIGRATION_TEST_DB_URL")
    if env_url:
        return env_url
    tmp = tmp_path_factory.mktemp("migration_db")
    return f"sqlite:///{tmp / 'test_migrations.db'}"


@pytest.fixture(scope="session")
def alembic_cfg(migration_db_url: str) -> AlembicConfig:
    """Alembic config fixture bound to the migration test database."""
    return _make_alembic_config(migration_db_url)


@pytest.fixture(scope="session")
def migration_engine(migration_db_url: str):
    """SQLAlchemy engine pointed at the migration test database."""
    kwargs: dict = {}
    if migration_db_url.startswith("sqlite"):
        kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    engine = create_engine(migration_db_url, **kwargs)
    yield engine
    engine.dispose()


class AlembicRunner:
    """Helper wrapper around alembic.command for use in tests."""

    def __init__(self, cfg: AlembicConfig) -> None:
        self.cfg = cfg

    def run_migrations_up(self, revision: str = "head") -> None:
        """Apply all (or up-to ``revision``) migrations."""
        alembic_command.upgrade(self.cfg, revision)

    def run_migrations_down(self, revision: str = "base") -> None:
        """Revert all (or down-to ``revision``) migrations."""
        alembic_command.downgrade(self.cfg, revision)

    def current_revision(self) -> str | None:
        """Return the current migration revision string."""
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine as _ce

        db_url = self.cfg.get_main_option("sqlalchemy.url")
        eng = _ce(db_url)
        with eng.connect() as conn:
            ctx = MigrationContext.configure(conn)
            rev = ctx.get_current_revision()
        eng.dispose()
        return rev

    def step_down_one(self) -> None:
        """Revert exactly one migration."""
        alembic_command.downgrade(self.cfg, "-1")

    def step_up_one(self) -> None:
        """Apply exactly one pending migration."""
        alembic_command.upgrade(self.cfg, "+1")


@pytest.fixture(scope="session")
def alembic_runner(alembic_cfg: AlembicConfig) -> AlembicRunner:
    """Return an :class:`AlembicRunner` for the migration test database."""
    return AlembicRunner(alembic_cfg)


# ---------------------------------------------------------------------------
# Pre-built tests — import into your test module to run automatically
# ---------------------------------------------------------------------------


def test_migrations_upgrade_to_head(alembic_runner: AlembicRunner) -> None:
    """All migrations apply cleanly to ``head``."""
    alembic_runner.run_migrations_up("head")
    assert alembic_runner.current_revision() is not None


def test_migrations_downgrade_to_base(alembic_runner: AlembicRunner) -> None:
    """All migrations roll back cleanly to ``base``."""
    alembic_runner.run_migrations_up("head")
    alembic_runner.run_migrations_down("base")
    assert alembic_runner.current_revision() is None


def test_migrations_round_trip(alembic_runner: AlembicRunner) -> None:
    """Upgrade to head, downgrade to base, upgrade again — no errors."""
    alembic_runner.run_migrations_up("head")
    alembic_runner.run_migrations_down("base")
    alembic_runner.run_migrations_up("head")
    assert alembic_runner.current_revision() is not None
