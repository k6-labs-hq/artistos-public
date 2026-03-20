# Disaster Recovery and Backup Runbook

## Recovery Targets
- RPO: 15 minutes
- RTO: 60 minutes

## Daily Controls
1. Nightly Postgres dump job via cron in Kubernetes.
2. Backup object replication to secondary region.
3. Automatic integrity checks on backup artifacts.

## Weekly Restore Drill
1. Provision isolated restore target.
2. Run:
   - DB_URL=<target-url> scripts/ops/restore_drill.sh <backup-file.sql.gz>
3. Validate critical tables and record counts.
4. Capture drill result and remediation actions.

## Production Failover Sequence
1. Freeze writes on primary app.
2. Promote standby database.
3. Update secret + restart API and workers.
4. Verify health, queue processing, and customer-facing endpoints.
5. Complete incident review and update this runbook.
