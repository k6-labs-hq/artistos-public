"""
Shared test fixtures for the XR7 Engine 2 test suite.

Sets up a single in-memory SQLite database using StaticPool so that all
connections share the same instance.  Both test files (`test_widget_auth.py`
and `test_ingestion.py`) import from here to avoid stomping on each other's
`app.dependency_overrides[get_db]` registration.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from XR7.models.base import Base, get_db
from XR7.api.app import app
# Ensure all model tables are registered before create_all
import XR7.models.terms_acceptance  # noqa: F401
import XR7.models.forensic_universal_event  # noqa: F401
import XR7.models.catalog_graph_adj  # noqa: F401
import XR7.models.review_queue  # noqa: F401
import XR7.models.admin_audit_log  # noqa: F401
import XR7.models.ml_feedback  # noqa: F401
import XR7.models.model_registry  # noqa: F401
import XR7.models.catalog_segment  # noqa: F401
import XR7.models.metadata_issue  # noqa: F401
import XR7.models.trolley_transaction  # noqa: F401
import XR7.models.platform_config  # noqa: F401
import XR7.models.xr7_royalty  # noqa: F401
import XR7.models.identity_match  # noqa: F401
import XR7.models.trust_trace  # noqa: F401
import XR7.models.artist_referral  # noqa: F401
import XR7.models.liquidity_advance  # noqa: F401
import XR7.models.rights_scan  # noqa: F401
import XR7.models.artist_message  # noqa: F401
import XR7.models.class_action_signal  # noqa: F401
import XR7.models.advance_opportunity  # noqa: F401
import XR7.models.advance_approval  # noqa: F401
import XR7.models.advance_offer  # noqa: F401
import XR7.models.advance_recovery_packet  # noqa: F401
import XR7.models.tvfilm_portfolio_job  # noqa: F401
import XR7.models.invite  # noqa: F401
import XR7.models.legal_defensibility_event  # noqa: F401
import XR7.models.society_signal_log  # noqa: F401
import XR7.models.agent_handoff  # noqa: F401
import XR7.models.vip  # noqa: F401
import XR7.models.notification_delivery_log  # noqa: F401
import XR7.models.case_room  # noqa: F401
import XR7.models.data_residency  # noqa: F401
import XR7.models.connector_sync_cursor  # noqa: F401
import XR7.models.webhook_event  # noqa: F401
import XR7.models.slo_metric  # noqa: F401
import XR7.models.batch_ingestion_job  # noqa: F401
import XR7.models.xr7_idempotency  # noqa: F401

# Single shared in-memory SQLite engine for the entire test suite
TEST_DB_URL = "sqlite://"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=test_engine)

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
