# Incident Response Runbook

## Scope
This runbook covers production incidents for API availability, worker backlog, and data pipeline failures.

## Severity Model
- SEV-1: platform outage or data loss risk
- SEV-2: partial outage or severe degradation
- SEV-3: non-critical defect with workaround

## Response Flow
1. Acknowledge alert and assign incident commander.
2. Open incident channel and timeline doc.
3. Execute nearest runbook action (API, workers, DB, or infra).
4. Decide rollback vs. forward fix within 15 minutes.
5. Post mitigation summary and schedule postmortem in 24 hours.

## Immediate Actions
- API crash loop:
  - kubectl -n xr7 get pods
  - kubectl -n xr7 logs deploy/xr7-api --tail=200
  - kubectl -n xr7 rollout undo deploy/xr7-api
- Worker backlog spike:
  - kubectl -n xr7 get hpa
  - kubectl -n xr7 scale deploy/xr7-worker --replicas=10
  - verify broker health and drain rate
- Data layer fault:
  - fail over to read replica
  - halt destructive jobs
  - begin restore drill if needed

## Exit Criteria
- SLOs recovered for 30+ minutes.
- No active data corruption indicators.
- Incident timeline and owner handoff complete.
