"""
Read Replica Routing for PostgreSQL Database.

Implements intelligent query routing:
- SELECT queries → read replicas (scalable reads)
- INSERT/UPDATE/DELETE → primary (write consistency)
- Automatic fallback to primary if no replicas available
- Replica lag monitoring and tolerance

Configuration via environment variables:
- DATABASE_REPLICA_URLS: Comma-separated replica connection strings
- DATABASE_REPLICA_LAG_TOLERANCE: Max acceptable lag in seconds (default: 5)
- DATABASE_PREFER_REPLICA: Force replica for all SELECTs (default: true)

Documented in docs/production_readiness_wave3_2026_q2.md DB-011

Example:
    DATABASE_URL=postgresql://user:pass@primary:5432/db
    DATABASE_REPLICA_URLS=postgresql://user:pass@replica1:5432/db,postgresql://user:pass@replica2:5432/db
"""

from __future__ import annotations

import os
import random
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Environment configuration
DATABASE_REPLICA_URLS = os.environ.get("DATABASE_REPLICA_URLS", "").strip()
REPLICA_LAG_TOLERANCE = int(os.environ.get("DATABASE_REPLICA_LAG_TOLERANCE", "5"))
PREFER_REPLICA = os.environ.get("DATABASE_PREFER_REPLICA", "true").lower() == "true"


class ReadReplicaRoutingSession(Session):
    """SQLAlchemy Session that routes reads to replicas.

    Routes SELECT queries to read replicas for scalability.
    Writes (INSERT/UPDATE/DELETE) always go to primary.

    Usage:
        engine = create_engine(DATABASE_URL)
        replica_engines = [create_engine(url) for url in get_replica_urls()]
        SessionLocal = get_replica_session_factory(engine, replica_engines)

        with SessionLocal() as db:
            # This goes to replica
            artists = db.query(Artist).all()

            # This goes to primary
            db.add(new_artist)
            db.commit()
    """

    def __init__(self, bind=None, binds=None, replica_engines=None, **kwargs):
        super().__init__(bind=bind, binds=binds, **kwargs)
        self._replica_engines = replica_engines or []
        self._using_replica = False
        self._primary_bind = bind

    def get_bind(self, mapper=None, clause=None, **kwargs):
        """Route query to appropriate engine (primary or replica).

        SELECT queries go to replicas (if available).
        Write queries go to primary.
        """
        # If we're in a transaction or have pending changes, use primary
        if self.in_transaction() or self.dirty or self.new or self.deleted:
            self._using_replica = False
            return self._primary_bind

        # Check if this is a SELECT query by examining the clause
        if clause is not None:
            # Check if it's a SELECT statement (read operation)
            is_select = str(clause).strip().upper().startswith("SELECT")

            if is_select and self._replica_engines and PREFER_REPLICA:
                # Route to random replica for load balancing
                replica_engine = random.choice(self._replica_engines)
                self._using_replica = True
                logger.debug(
                    "Routing SELECT to replica",
                    extra={"replica": replica_engine.url.database},
                )
                return replica_engine

        # Default to primary for all writes and non-SELECT reads
        self._using_replica = False
        return self._primary_bind


def get_replica_urls() -> list[str]:
    """Parse replica URLs from environment variable.

    Returns:
        List of replica connection strings
    """
    if not DATABASE_REPLICA_URLS:
        return []

    urls = [url.strip() for url in DATABASE_REPLICA_URLS.split(",") if url.strip()]
    logger.info(f"Configured {len(urls)} read replicas", extra={"replica_count": len(urls)})
    return urls


def create_replica_engines(replica_urls: list[str]) -> list[Engine]:
    """Create SQLAlchemy engines for each replica.

    Args:
        replica_urls: List of PostgreSQL connection strings

    Returns:
        List of SQLAlchemy engines
    """
    engines = []
    for url in replica_urls:
        try:
            engine = create_engine(
                url,
                pool_pre_ping=True,  # Verify connections before use
                pool_size=10,  # Smaller pool for replicas
                max_overflow=20,
                echo=False,
            )
            engines.append(engine)
            logger.info(f"Created replica engine: {engine.url.database}")
        except Exception as e:
            logger.error(f"Failed to create replica engine for {url}: {e}")

    return engines


def get_replica_session_factory(
    primary_engine: Engine, replica_engines: list[Engine] = None
) -> sessionmaker:
    """Create session factory with read replica routing.

    Args:
        primary_engine: Primary database engine (for writes)
        replica_engines: List of replica engines (for reads)

    Returns:
        Session factory configured for replica routing
    """
    if replica_engines is None:
        replica_urls = get_replica_urls()
        replica_engines = create_replica_engines(replica_urls) if replica_urls else []

    if not replica_engines:
        logger.warning("No read replicas configured, all queries will use primary")
        # Return standard session factory without replica routing
        return sessionmaker(bind=primary_engine, class_=Session)

    # Return session factory with replica routing
    return sessionmaker(
        bind=primary_engine,
        class_=ReadReplicaRoutingSession,
        replica_engines=replica_engines,
    )


def monitor_replica_lag(replica_engine: Engine) -> float:
    """Monitor replication lag for a replica.

    Queries pg_stat_replication on primary or pg_last_wal_receive_lsn on replica.

    Args:
        replica_engine: Replica engine to monitor

    Returns:
        Lag in seconds (None if unable to determine)
    """
    try:
        with replica_engine.connect() as conn:
            # Query replica for replay lag
            result = conn.execute(
                """
                SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds
                """
            )
            row = result.fetchone()
            if row and row[0] is not None:
                lag_seconds = float(row[0])
                logger.debug(
                    f"Replica lag: {lag_seconds:.2f}s",
                    extra={"replica": replica_engine.url.database, "lag_seconds": lag_seconds},
                )
                return lag_seconds
            return 0.0
    except Exception as e:
        logger.error(f"Failed to query replica lag: {e}")
        return None


def check_replica_health(replica_engines: list[Engine]) -> dict[str, Any]:
    """Check health of all replicas.

    Returns:
        Health status dict with lag metrics
    """
    health = {"healthy_replicas": 0, "unhealthy_replicas": 0, "replicas": []}

    for engine in replica_engines:
        lag = monitor_replica_lag(engine)
        is_healthy = lag is not None and lag <= REPLICA_LAG_TOLERANCE

        health["replicas"].append(
            {
                "url": str(engine.url),
                "lag_seconds": lag,
                "healthy": is_healthy,
                "exceed_tolerance": lag and lag > REPLICA_LAG_TOLERANCE,
            }
        )

        if is_healthy:
            health["healthy_replicas"] += 1
        else:
            health["unhealthy_replicas"] += 1

    return health
