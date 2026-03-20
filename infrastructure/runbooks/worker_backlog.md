# Worker Backlog Runbook

## Trigger
- Alert: XR7WorkerBacklogHigh
- Queue depth > 500 for 15 minutes

## Diagnose
1. Inspect worker and scheduler status:
   - kubectl -n xr7 get deploy xr7-worker xr7-scheduler
2. Check worker logs:
   - kubectl -n xr7 logs deploy/xr7-worker --tail=200
3. Confirm Redis broker availability and latency.

## Mitigate
1. Scale workers:
   - kubectl -n xr7 scale deploy/xr7-worker --replicas=15
2. Pause non-critical scheduled tasks temporarily.
3. Increase worker concurrency if CPU headroom exists.

## Verify
1. Queue depth trending down for 20+ minutes.
2. End-to-end job latency under SLO.
3. Error ratio below 2%.
