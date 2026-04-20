import logging
import time
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, with_loader_criteria

from XR7.exceptions import TenantIsolationViolation
from XR7.services.tenant_context import get_current_actor_sub, get_current_tenant_id
from xr7_common.settings import settings

DATABASE_URL = settings.database_url
logger = logging.getLogger(__name__)


def _engine_connect_args(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    if url.startswith("postgresql"):
        # Prevent long-running queries from hanging indefinitely
        # statement_timeout: Kill queries running longer than 30 seconds
        return {"options": "-c statement_timeout=30000"}
    return {}


def _engine_pool_kwargs(url: str) -> dict[str, object]:
    """Return pool settings only for non-SQLite databases."""
    if url.startswith("sqlite"):
        # SQLite does not support connection pooling via SQLAlchemy pool
        return {}
    return {
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
        "pool_recycle": settings.db_pool_recycle,
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=_engine_connect_args(DATABASE_URL),
    pool_pre_ping=True,
    **_engine_pool_kwargs(DATABASE_URL),
)


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    start_times = conn.info.get("query_start_time", [])
    if not start_times:
        return
    total = time.perf_counter() - start_times.pop(-1)
    duration_ms = total * 1000

    # Slow query logging threshold: >100ms
    if duration_ms > 100:
        logger.warning(
            "slow_query_detected",
            extra={
                "duration_ms": round(duration_ms, 2),
                "statement": statement[:500],
            },
        )

    # Lightweight N+1 heuristic: repeated SELECT statements on same connection.
    normalized = " ".join((statement or "").split())[:300]
    if normalized.lower().startswith("select"):
        counts = conn.info.setdefault("query_seen_counts", {})
        counts[normalized] = counts.get(normalized, 0) + 1
        if counts[normalized] == 10:
            logger.warning(
                "n_plus_one_suspected",
                extra={"statement": normalized, "repeat_count": counts[normalized]},
            )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(SessionLocal, "do_orm_execute")
def _enforce_tenant_scope(execute_state) -> None:
    """Enforce tenant isolation on all SELECT queries.

    Automatically filters queries to only return rows matching the current
    tenant ID from the JWT context. This prevents accidental or malicious
    cross-tenant data access.

    For write operations (INSERT/UPDATE/DELETE), see _enforce_tenant_writes.
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return

    actor_sub = get_current_actor_sub()
    params = execute_state.parameters
    if isinstance(params, dict):
        explicit_tenant = str(params.get("tenant_id") or "").strip()
        if explicit_tenant and explicit_tenant != tenant_id:
            logger.warning(
                "cross_tenant_parameter_attempt",
                extra={
                    "tenant_from_jwt": tenant_id,
                    "tenant_from_query": explicit_tenant,
                    "actor": actor_sub,
                },
            )

    if execute_state.is_select:
        tenant_entities: list[type] = []
        for mapper in Base.registry.mappers:
            model_cls = mapper.class_
            if hasattr(model_cls, "tenant_id"):
                tenant_entities.append(model_cls)

        if tenant_entities:
            execute_state.statement = execute_state.statement.options(
                *[
                    with_loader_criteria(
                        entity,
                        lambda cls, tenant_id=tenant_id: cls.tenant_id == tenant_id,
                        include_aliases=True,
                    )
                    for entity in tenant_entities
                ]
            )


@event.listens_for(SessionLocal, "before_flush")
def _enforce_tenant_writes(session, flush_context, instances) -> None:
    """Enforce tenant isolation on write operations (INSERT/UPDATE/DELETE).

    Validates that:
    1. INSERT: Auto-injects current tenant_id if model has one
    2. UPDATE: Verifies target object belongs to current tenant
    3. DELETE: Verifies target object belongs to current tenant

    Raises:
        TenantIsolationViolation: If write operation crosses tenant boundary

    Compliance: SOC 2 CC6.7 — Logical access controls (tenant isolation)
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        # No tenant context set (e.g., system migrations, tests)
        return

    actor_sub = get_current_actor_sub()

    # Check new objects (INSERT)
    for obj in session.new:
        if hasattr(obj, "tenant_id"):
            if obj.tenant_id is None:
                # Auto-inject tenant_id for new objects
                obj.tenant_id = tenant_id
                logger.debug(
                    "tenant_id_auto_injected",
                    extra={
                        "model": obj.__class__.__name__,
                        "tenant_id": tenant_id,
                        "actor": actor_sub,
                    },
                )
            elif obj.tenant_id != tenant_id:
                # Attempting to INSERT with wrong tenant_id
                logger.error(
                    "tenant_isolation_violation_insert",
                    extra={
                        "model": obj.__class__.__name__,
                        "current_tenant": tenant_id,
                        "target_tenant": obj.tenant_id,
                        "actor": actor_sub,
                    },
                )
                raise TenantIsolationViolation(
                    current_tenant=tenant_id,
                    target_tenant=obj.tenant_id,
                    operation="INSERT",
                    model=obj.__class__.__name__,
                    actor_sub=actor_sub,
                )

    # Check modified objects (UPDATE)
    for obj in session.dirty:
        if hasattr(obj, "tenant_id"):
            obj_tenant = getattr(obj, "tenant_id", None)
            if obj_tenant and obj_tenant != tenant_id:
                logger.error(
                    "tenant_isolation_violation_update",
                    extra={
                        "model": obj.__class__.__name__,
                        "current_tenant": tenant_id,
                        "target_tenant": obj_tenant,
                        "actor": actor_sub,
                        "object_id": getattr(obj, "id", "unknown"),
                    },
                )
                raise TenantIsolationViolation(
                    current_tenant=tenant_id,
                    target_tenant=obj_tenant,
                    operation="UPDATE",
                    model=obj.__class__.__name__,
                    actor_sub=actor_sub,
                )

    # Check deleted objects (DELETE)
    for obj in session.deleted:
        if hasattr(obj, "tenant_id"):
            obj_tenant = getattr(obj, "tenant_id", None)
            if obj_tenant and obj_tenant != tenant_id:
                logger.error(
                    "tenant_isolation_violation_delete",
                    extra={
                        "model": obj.__class__.__name__,
                        "current_tenant": tenant_id,
                        "target_tenant": obj_tenant,
                        "actor": actor_sub,
                        "object_id": getattr(obj, "id", "unknown"),
                    },
                )
                raise TenantIsolationViolation(
                    current_tenant=tenant_id,
                    target_tenant=obj_tenant,
                    operation="DELETE",
                    model=obj.__class__.__name__,
                    actor_sub=actor_sub,
                )


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""


def get_db() -> Generator[Any, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
