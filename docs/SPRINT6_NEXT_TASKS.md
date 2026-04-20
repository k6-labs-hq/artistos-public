# Sprint 6: Top 3 Production Hardening Tasks

**Date:** April 19, 2026  
**Status:** Ready to implement  
**Estimated Time:** 6-8 hours total

---

## ✅ Completed Today (Sprint 5)

### Intelligence Layer - Systems 1-3 (MERGED)
- **System 1**: Platform Self-Monitor with 7-domain detection + GitHub issue filing
- **System 2**: Weekly Intelligence Briefing Engine with 4 report sections
- **System 3**: Natural Language Operations Interface with confidence-rated responses
- **Total**: 37 production files, ~3,400 lines, comprehensive documentation
- **PRs**: #91 and #92 merged to main

---

## 🎯 Top 3 Priority Tasks for Next Session

### 1. Wire System 1 Monitor into CI/CD (2-3 hours)
**Priority:** HIGH  
**Business Value:** Automated platform monitoring catches issues before customers

**Scope:**
- Create `.github/workflows/platform-monitor.yml`
- Run `python -m intelligence.monitor.cli --file-issues` on schedule (daily 6 AM)
- Run on main branch pushes
- Auto-files GitHub issues for P0 findings
- Notify Slack channel on critical findings

**Acceptance Criteria:**
- Workflow triggers daily and on main push
- P0 findings create GitHub issues automatically
- Workflow fails if P0 findings detected (prevents bad deploys)
- Deduplication works (no duplicate issues)

**Files to Create:**
```yaml
# .github/workflows/platform-monitor.yml
name: Platform Self-Monitor
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Run Platform Monitor
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m intelligence.monitor.cli --file-issues --output json > monitor-results.json
          cat monitor-results.json
      - name: Check for P0 findings
        run: |
          if grep -q '"severity": "P0"' monitor-results.json; then
            echo "::error::P0 findings detected - blocking deployment"
            exit 1
          fi
```

---

### 2. Issue #74: Real Dependency Health Checks (2 hours)
**Priority:** P1  
**Business Value:** Prevents cascading failures, improves incident response

**Current State:**
`/health` endpoint exists but doesn't check external dependencies

**Scope:**
- Add health checks for: Redis, PostgreSQL, Celery, Trolley API
- Return detailed status per dependency
- Separate endpoints: `/health` (liveness) and `/health/ready` (readiness)
- Cache health check results (30s TTL) to prevent overwhelming dependencies

**Implementation:**

**File:** `XR7/api/routers/health.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from redis import Redis
from celery import Celery
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter()

# Cache health check results
_health_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = timedelta(seconds=30)

async def check_postgres(db: Session) -> Dict[str, Any]:
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis() -> Dict[str, Any]:
    try:
        redis = Redis.from_url(settings.REDIS_URL)
        redis.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_celery() -> Dict[str, Any]:
    try:
        celery_app = Celery(broker=settings.CELERY_BROKER_URL)
        stats = celery_app.control.inspect().stats()
        worker_count = len(stats) if stats else 0
        return {
            "status": "healthy" if worker_count > 0 else "degraded",
            "worker_count": worker_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_trolley() -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.TROLLEY_BASE_URL}/health",
                timeout=2.0
            )
            return {"status": "healthy" if response.status_code == 200 else "degraded"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health")
async def health_liveness():
    """Kubernetes liveness probe - returns 200 if app is running"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/health/ready")
async def health_readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - checks all dependencies"""
    now = datetime.utcnow()
    
    # Check cache
    if "ready" in _health_cache:
        cached = _health_cache["ready"]
        if now - cached["timestamp"] < _cache_ttl:
            return cached["result"]
    
    # Run checks
    checks = {
        "postgres": await check_postgres(db),
        "redis": await check_redis(),
        "celery": await check_celery(),
        "trolley": await check_trolley(),
    }
    
    # Determine overall status
    all_healthy = all(c["status"] == "healthy" for c in checks.values())
    any_unhealthy = any(c["status"] == "unhealthy" for c in checks.values())
    
    overall_status = "healthy" if all_healthy else ("degraded" if not any_unhealthy else "unhealthy")
    
    result = {
        "status": overall_status,
        "timestamp": now.isoformat(),
        "checks": checks
    }
    
    # Cache result
    _health_cache["ready"] = {
        "timestamp": now,
        "result": result
    }
    
    return result
```

**Test:** `tests/test_health_checks.py`
```python
def test_health_liveness_always_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health_readiness_checks_postgres(client, db):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert "postgres" in response.json()["checks"]
    assert response.json()["checks"]["postgres"]["status"] == "healthy"

def test_health_readiness_caches_results(client, monkeypatch):
    # First call
    response1 = client.get("/health/ready")
    time1 = response1.json()["timestamp"]
    
    # Second call within 30s should return cached
    response2 = client.get("/health/ready")
    time2 = response2.json()["timestamp"]
    
    assert time1 == time2  # Same cached result
```

**Acceptance Criteria:**
- `/health` returns 200 always (liveness)
- `/health/ready` checks 4 dependencies
- Results cached for 30s
- Tests pass
- Kubernetes manifests updated to use new endpoints

---

### 3. Issue #78: Celery Graceful Shutdown (2-3 hours)
**Priority:** P1  
**Business Value:** Prevents task loss during deployments

**Current State:**
Celery workers receive SIGTERM and immediately stop, losing in-flight tasks

**Scope:**
- Configure Celery worker graceful shutdown timeout
- Update Kubernetes deployment with proper termination grace period
- Add signal handlers to complete current tasks before shutdown
- Test with simulated deployment

**Implementation:**

**File:** `XR7/tasks/celery_app.py`
```python
from celery import Celery, signals
from celery.signals import worker_shutting_down
import logging

logger = logging.getLogger(__name__)

app = Celery('xr7')
app.config_from_object('xr7_common.celery_config')

@worker_shutting_down.connect
def on_worker_shutdown(sender, **kwargs):
    """Log graceful shutdown"""
    logger.warning("Celery worker shutting down gracefully - completing current tasks")

# Configure graceful shutdown
app.conf.task_soft_time_limit = 300  # 5 minutes
app.conf.task_time_limit = 600  # 10 minutes (hard limit)
app.conf.worker_prefetch_multiplier = 1  # Take one task at a time during shutdown
```

**File:** `infrastructure/kubernetes/base/celery-worker.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 3
  template:
    spec:
      terminationGracePeriodSeconds: 600  # 10 minutes
      containers:
      - name: worker
        image: artistos:latest
        command: ["celery", "-A", "XR7.tasks", "worker", "--loglevel=info"]
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 5"]  # Give time to finish current task
        env:
        - name: CELERY_BROKER_URL
          valueFrom:
            secretKeyRef:
              name: runtime-secret
              key: CELERY_BROKER_URL
```

**Test:** `tests/test_celery_graceful_shutdown.py`
```python
import signal
import time
from multiprocessing import Process
from XR7.tasks.celery_app import app

@app.task
def long_running_task():
    """Simulate a task that takes 10 seconds"""
    time.sleep(10)
    return "completed"

def test_graceful_shutdown_completes_tasks():
    # Start worker in subprocess
    def run_worker():
        worker = app.Worker()
        worker.start()
    
    worker_process = Process(target=run_worker)
    worker_process.start()
    
    # Queue a task
    result = long_running_task.delay()
    
    # Send SIGTERM after 2 seconds
    time.sleep(2)
    worker_process.terminate()
    
    # Wait for graceful shutdown (should complete task)
    worker_process.join(timeout=15)
    
    # Task should have completed
    assert result.ready()
    assert result.get() == "completed"
```

**Acceptance Criteria:**
- Workers complete current tasks before shutdown (up to 10 min)
- Kubernetes termination grace period = 600s
- Signal handlers log shutdown events
- Test demonstrates graceful shutdown
- No task loss during rolling deployments

---

## 📋 Quick Start for Next Session

```bash
# 1. Start fresh from main
git checkout main
git pull

# 2. Create feature branch
git checkout -b xr7/sprint6-production-hardening

# 3. Implement Task 1: CI/CD Monitor Workflow
# Create .github/workflows/platform-monitor.yml (see above)

# 4. Implement Task 2: Health Checks
# Edit XR7/api/routers/health.py
# Edit tests/test_health_checks.py

# 5. Implement Task 3: Celery Graceful Shutdown
# Edit XR7/tasks/celery_app.py
# Edit infrastructure/kubernetes/base/celery-worker.yaml
# Create tests/test_celery_graceful_shutdown.py

# 6. Test all changes
pytest tests/test_health_checks.py -v
pytest tests/test_celery_graceful_shutdown.py -v

# 7. Commit and push
git add -A
git commit -m "feat(ops): CI monitor + health checks + graceful shutdown"
git push -u origin xr7/sprint6-production-hardening
gh pr create --base main --title "feat(ops): Production hardening - monitor CI + health checks + graceful shutdown"
```

---

## 🚀 Expected Impact

After completing these 3 tasks:

1. **Automated Monitoring**: Platform issues caught before customers report them
2. **Better Observability**: Kubernetes knows when pods are truly ready
3. **Zero Task Loss**: Deployments complete in-flight work before shutdown

**Total Time:** 6-8 hours  
**Risk:** Low - all changes are additive  
**Value:** High - production reliability fundamentals

---

## 📚 Reference Documentation

- Intelligence Layer: `intelligence/README.md`
- System 1 Monitor: `intelligence/monitor/README.md`
- CI/CD Pipelines: `docs/cicd_pipeline_reference.md`
- Celery Workflows: `docs/celery_workflows.md`
- Health Checks: `docs/observability_monitoring_handbook.md`

---

## 🎯 Success Criteria

Session complete when:
- [ ] Platform monitor runs automatically in CI
- [ ] `/health/ready` checks all 4 dependencies
- [ ] Celery workers gracefully shutdown in ≤10 minutes
- [ ] All tests pass
- [ ] PR created and passing CI
- [ ] Documentation updated

**Ready to ship!** 🚢
