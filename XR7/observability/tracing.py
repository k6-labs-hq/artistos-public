"""
Distributed Tracing configuration for XR7 Engine using OpenTelemetry.

Instruments:
- FastAPI (HTTP requests/responses)
- SQLAlchemy (database queries)
- Redis (cache operations)
- Celery (background tasks)

Environment variables:
- JAEGER_HOST: Jaeger agent hostname (default: localhost)
- JAEGER_PORT: Jaeger agent port (default: 6831)
- OTEL_SERVICE_NAME: Service name in traces (default: xr7-engine)
- OTEL_EXPORTER_ENABLED: Enable/disable tracing (default: false for dev)

Documented in docs/observability_monitoring_handbook.md
"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from xr7_common.logging import get_logger

logger = get_logger(__name__)


def configure_tracing() -> None:
    """Configure OpenTelemetry distributed tracing.

    Should be called at application startup (in lifespan context).

    Instrumentors are imported conditionally to avoid dependency errors
    when OpenTelemetry packages are not installed.

    Production requirements:
    - JAEGER_HOST must be set to Jaeger collector endpoint
    - OTEL_EXPORTER_ENABLED=true to enable tracing
    - Service name should be 'xr7-engine' or environment-specific
    """
    # Only enable tracing if explicitly configured
    enabled = os.environ.get("OTEL_EXPORTER_ENABLED", "false").lower() == "true"
    if not enabled:
        logger.info("Distributed tracing disabled (OTEL_EXPORTER_ENABLED != true)")
        return

    service_name = os.environ.get("OTEL_SERVICE_NAME", "xr7-engine")
    jaeger_host = os.environ.get("JAEGER_HOST", "localhost")
    jaeger_port = int(os.environ.get("JAEGER_PORT", "6831"))

    # Create tracer provider with service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "xr7",
            "deployment.environment": os.environ.get("XR7_ENV", "development"),
        }
    )
    provider = TracerProvider(resource=resource)

    # Configure Jaeger exporter (conditional import to handle version compatibility)
    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter

        exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except ImportError:
        logger.warning(
            "Jaeger exporter not available - tracing enabled but exports will be dropped. "
            "Install opentelemetry-exporter-jaeger<1.21.0 or use alternative exporter."
        )

    # Set as global tracer provider
    trace.set_tracer_provider(provider)

    logger.info(
        "Distributed tracing configured",
        extra={
            "service_name": service_name,
            "jaeger_host": jaeger_host,
            "jaeger_port": jaeger_port,
        },
    )

    # Auto-instrument frameworks (import only when enabled to avoid dep errors)
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor().instrument()
        logger.info("FastAPI tracing instrumentation enabled")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-fastapi not installed")

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy tracing instrumentation enabled")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-sqlalchemy not installed")

    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
        logger.info("Redis tracing instrumentation enabled")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-redis not installed")

    try:
        from opentelemetry.instrumentation.celery import CeleryInstrumentor

        CeleryInstrumentor().instrument()
        logger.info("Celery tracing instrumentation enabled")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-celery not installed")

    logger.info("Distributed tracing fully configured")


def get_current_span():
    """Get the current active span for manual instrumentation.

    Returns:
        Span: Current active span or no-op span if tracing disabled

    Example:
        span = get_current_span()
        span.set_attribute("artist_id", artist_id)
        span.set_attribute("dsp", "spotify")
    """
    return trace.get_current_span()


def get_tracer(name: str):
    """Get a tracer for manual span creation.

    Args:
        name: Tracer name (typically __name__)

    Returns:
        Tracer: OpenTelemetry tracer instance

    Example:
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("process_statement"):
            # Your code here
            pass
    """
    return trace.get_tracer(name)
