"""
Shared test fixtures for the XR7 Engine 2 test suite.

Sets up a single in-memory SQLite database using StaticPool so that all
connections share the same instance.  Both test files (`test_widget_auth.py`
and `test_ingestion.py`) import from here to avoid stomping on each other's
`app.dependency_overrides[get_db]` registration.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import XR7.models.admin_audit_log  # noqa: F401
import XR7.models.advance_approval  # noqa: F401
import XR7.models.advance_offer  # noqa: F401
import XR7.models.advance_opportunity  # noqa: F401
import XR7.models.advance_recovery_packet  # noqa: F401
import XR7.models.agent_handoff  # noqa: F401
import XR7.models.api_key  # noqa: F401
import XR7.models.artist_message  # noqa: F401
import XR7.models.artist_referral  # noqa: F401
import XR7.models.batch_ingestion_job  # noqa: F401
import XR7.models.case_room  # noqa: F401
import XR7.models.catalog_graph_adj  # noqa: F401
import XR7.models.catalog_segment  # noqa: F401
import XR7.models.class_action_signal  # noqa: F401
import XR7.models.connector_sync_cursor  # noqa: F401
import XR7.models.data_residency  # noqa: F401
import XR7.models.forensic_universal_event  # noqa: F401
import XR7.models.identity_match  # noqa: F401
import XR7.models.invite  # noqa: F401
import XR7.models.legal_defensibility_event  # noqa: F401
import XR7.models.liquidity_advance  # noqa: F401
import XR7.models.metadata_issue  # noqa: F401
import XR7.models.ml_feedback  # noqa: F401
import XR7.models.model_registry  # noqa: F401
import XR7.models.notification_delivery_log  # noqa: F401
import XR7.models.platform_config  # noqa: F401
import XR7.models.review_queue  # noqa: F401
import XR7.models.rights_scan  # noqa: F401
import XR7.models.slo_metric  # noqa: F401
import XR7.models.society_signal_log  # noqa: F401

# Ensure all model tables are registered before create_all
import XR7.models.terms_acceptance  # noqa: F401
import XR7.models.trolley_transaction  # noqa: F401
import XR7.models.trust_trace  # noqa: F401
import XR7.models.tvfilm_portfolio_job  # noqa: F401
import XR7.models.vip  # noqa: F401
import XR7.models.webhook_event  # noqa: F401
import XR7.models.work  # noqa: F401
import XR7.models.xr7_idempotency  # noqa: F401
import XR7.models.xr7_royalty  # noqa: F401
from XR7.api.app import app
from XR7.models.base import Base, get_db

# Single shared in-memory SQLite engine for the entire test suite
TEST_DB_URL = "sqlite://"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=test_engine
)

# Create all tables once
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Register the override once, globally, for all tests
app.dependency_overrides[get_db] = override_get_db

# Patch the module-level SessionLocal used by two_agent_orchestrator_graph
# so that query_handoffs() (and other direct-session callers) use the test DB.
import XR7.agents.two_agent_orchestrator_graph as _two_agent_graph  # noqa: E402

_two_agent_graph.SessionLocal = TestSession


# Patch SessionLocal in agent modules so they use the test DB.
import XR7.agents.onboarding.catalog_agents as _catalog_agents  # noqa: E402
import XR7.agents.onboarding.core as _onboarding_core  # noqa: E402
import XR7.agents.onboarding.enrichment_agents as _enrichment_agents  # noqa: E402
import XR7.agents.specialized_agents as _specialized_agents  # noqa: E402
import XR7.agents.vip_persona_agent as _vip_persona_agent  # noqa: E402

_specialized_agents.SessionLocal = TestSession
_vip_persona_agent.SessionLocal = TestSession
_catalog_agents.SessionLocal = TestSession
_enrichment_agents.SessionLocal = TestSession
_onboarding_core.SessionLocal = TestSession
# Patch the base module SessionLocal so ALL code that imports it gets TestSession.
import XR7.models.base as _base_module  # noqa: E402

_base_module.SessionLocal = TestSession  # type: ignore[assignment]

# Bulk-patch SessionLocal across every XR7 module that has already imported it.
# This must run AFTER `from XR7.api.app import app` so all modules are loaded.
import sys as _sys  # noqa: E402

for _mod_name, _mod in list(_sys.modules.items()):
    if _mod_name.startswith("XR7") and hasattr(_mod, "SessionLocal"):
        setattr(_mod, "SessionLocal", TestSession)

# Configure Celery to run tasks synchronously in-process so tests don't
# attempt real Redis/broker connections (which cause ~20-second retry loops).
from XR7.celery_app import celery_app as _celery_app  # noqa: E402

_celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=False,
    broker_url="memory://",
    result_backend="cache+memory://",
)


# ---------------------------------------------------------------------------
# Integration-test marker auto-skip
# ---------------------------------------------------------------------------
# Tests marked with @pytest.mark.integration require live external credentials
# (PRO connectors, Trolley sandbox, etc.).  They are skipped by default in
# every CI run unless the caller passes --run-integration or sets the
# INTEGRATION_CREDS_AVAILABLE environment variable to a truthy value.
#
# To run integration tests locally:
#   pytest --run-integration
#   INTEGRATION_CREDS_AVAILABLE=1 pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Include tests marked @pytest.mark.integration (requires external credentials).",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    run_integration = config.getoption("--run-integration", default=False) or bool(
        os.environ.get("INTEGRATION_CREDS_AVAILABLE")
    )
    if run_integration:
        return  # let all tests run
    skip_marker = pytest.mark.skip(
        reason="requires external credentials — pass --run-integration to include"
    )
    for item in items:
        if item.get_closest_marker("integration"):
            item.add_marker(skip_marker)


# ---------------------------------------------------------------------------
# Test helper constants and functions
# ---------------------------------------------------------------------------
TEST_ARTIST_ID = "test-artist-123"


def create_test_artist(session, artist_id: str = TEST_ARTIST_ID, name: str = "Test Artist"):
    """Create a test artist in the database."""
    from XR7.models.artist import Artist

    artist = Artist(id=artist_id, name=name, email=f"{artist_id}@test.com")
    session.add(artist)
    session.commit()
    return artist


def create_test_terms(session, artist_id: str = TEST_ARTIST_ID):
    """Create test terms acceptance for an artist."""
    from datetime import datetime, timezone

    from XR7.models.terms_acceptance import TermsAcceptance

    terms = TermsAcceptance(
        artist_id=artist_id, version="1.0", accepted_at=datetime.now(timezone.utc)
    )
    session.add(terms)
    session.commit()
    return terms
