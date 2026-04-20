"""
Health check endpoints for Kubernetes liveness and readiness probes.

Provides two endpoints:
- /health: Liveness probe (always returns 200 if app is running)
- /health/ready: Readiness probe (checks all dependencies)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from XR7.database.session import get_db
from xr7_common.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Cache health check results to prevent overwhelming dependencies
_health_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = timedelta(seconds=30)


async def check_postgres(db: Session) -> Dict[str, Any]:
    """Check PostgreSQL database connectivity."""
    try:
        start = datetime.utcnow()
        db.execute("SELECT 1")
        elapsed_ms = (datetime.utcnow() - start).total_seconds() * 1000
        return {
            "status": "healthy",
            "latency_ms": round(elapsed_ms, 2)
        }
    except Exception as e:
        logger.error(f"Postgres health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        import redis
        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        client.ping()
        return {"status": "healthy"}
    except ImportError:
        return {"status": "skipped", "reason": "redis not installed"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_celery() -> Dict[str, Any]:
    """Check Celery worker availability."""
    try:
        from celery import Celery
        celery_app = Celery(broker=settings.CELERY_BROKER_URL)
        stats = celery_app.control.inspect(timeout=2.0).stats()
        worker_count = len(stats) if stats else 0
        
        return {
            "status": "healthy" if worker_count > 0 else "degraded",
            "worker_count": worker_count
        }
    except ImportError:
        return {"status": "skipped", "reason": "celery not installed"}
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "worker_count": 0
        }


async def check_trolley() -> Dict[str, Any]:
    """Check Trolley API connectivity."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.TROLLEY_BASE_URL}/v1/health",
                timeout=2.0,
                headers={"Authorization": f"Bearer {settings.TROLLEY_API_KEY}"}
            )
            return {
                "status": "healthy" if response.status_code == 200 else "degraded",
                "status_code": response.status_code
            }
    except ImportError:
        return {"status": "skipped", "reason": "httpx not installed"}
    except Exception as e:
        logger.warning(f"Trolley health check failed: {e}")
        return {
            "status": "degraded",
            "error": "Trolley API unreachable"
        }


@router.get("/health")
async def health_liveness():
    """
    Kubernetes liveness probe - returns 200 if application is running.
    
    This endpoint should always return quickly and indicate the service is alive.
    Does not check dependencies.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "artistos-api"
    }


@router.get("/health/ready")
async def health_readiness(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe - checks all dependencies.
    
    Returns 200 if the service is ready to handle requests.
    Returns 503 if any critical dependencies are unhealthy.
    
    Results are cached for 30 seconds to prevent overwhelming dependencies.
    """
    now = datetime.utcnow()
    
    # Check cache
    cache_key = "ready"
    if cache_key in _health_cache:
        cached = _health_cache[cache_key]
        if now - cached["timestamp"] < _cache_ttl:
            return cached["result"]
    
    # Run health checks
    checks = {
        "postgres": await check_postgres(db),
        "redis": await check_redis(),
        "celery": await check_celery(),
        "trolley": await check_trolley(),
    }
    
    # Determine overall status
    # Critical: postgres must be healthy
    # Non-critical: redis, celery, trolley can be degraded
    postgres_healthy  = checks["postgres"]["status"] == "healthy"
    any_unhealthy = any(
        c["status"] == "unhealthy" 
        for c in checks.values()
    )
    
    if not postgres_healthy:
        overall_status = "unhealthy"
    elif any_unhealthy:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    result = {
        "status": overall_status,
        "timestamp": now.isoformat(),
        "checks": checks
    }
    
    # Cache result
    _health_cache[cache_key] = {
        "timestamp": now,
        "result": result
    }
    
    # Return 503 if unhealthy (tells Kubernetes we're not ready)
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=result)
    
    return result
