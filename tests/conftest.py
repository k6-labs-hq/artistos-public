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

# Single shared in-memory SQLite engine for the entire test suite
TEST_DB_URL = "sqlite://"

test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

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
