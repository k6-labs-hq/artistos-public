# RUNBOOK: Evidence Chain Integrity Failure

**Alert Name:** `chain_verification_tampering_detected` / `scheduled_chain_verification_failure`
**Severity:** P0 (Critical)
**Response Time:** Immediate (< 15 minutes)
**Escalation:** Security team + Engineering lead

---

## What This Alert Means

The SHA-256 hash-chained audit ledger has detected **tampering or corruption** in one or more evidence packets. This means:

- **An evidence packet's integrity verification failed** (packet_hash, chain_hash, line_hashes, or signature mismatch)
- **Evidence cannot be served to attorneys** until integrity is verified or restored
- **Potential security incident** (database compromise, insider threat, or infrastructure failure)

Evidence packets are used in legal proceedings. Serving tampered evidence creates **legal liability** and destroys platform credibility.

---

## First Thing to Check

### 1. Is this affecting multiple tenants or a single claim?

**Check alert context:**
```json
{
  "artist_id": "uuid",
  "claim_id": "uuid",
  "checks": {
    "packet_hash_matches": false,
    "chain_hash_matches": true,
    "line_hashes_match": true,
    "signature_valid": true
  }
}
```

- **Multiple tenants affected** → Database-level compromise or infrastructure failure (proceed to CONFIRMED below)
- **Single claim affected** → Isolated incident, investigate specific claim history

### 2. Which integrity check failed?

**Check the `checks` object in the alert:**

| Failed Check | Probable Cause | Critical? |
|--------------|----------------|-----------|
| `packet_hash_matches: false` | Evidence JSON modified after sealing | YES |
| `chain_hash_matches: false` | Prior packet deleted/modified OR sequence broken | YES |
| `line_hashes_match: false` | Individual ledger entries modified | YES |
| `signature_valid: false` | Signing key rotated without re-signing OR signature tampering | YES |

---

## Decision Tree: Confirmed vs. False Positive

### False Positive Indicators

✅ **Recent legitimate operations:**
- Evidence packet re-generation after claim update
- Database migration or schema change in last 24 hours
- Signing key rotation documented in change log

✅ **Check database logs:**
```sql
SELECT * FROM admin_audit_log
WHERE resource_type = 'claim'
AND resource_id = '<claim_id>'
AND action IN ('evidence_regenerated', 'evidence_updated')
ORDER BY created_at DESC LIMIT 10;
```

If admin action logged with valid justification → **FALSE POSITIVE**

### Confirmed Incident Indicators

🚨 **Evidence of tampering:**
- No admin audit log entry justifying evidence modification
- Multiple claims affected across different tenants
- Signature failure without documented key rotation
- Failed checks with no database migration activity

If confirmed → **Proceed to REMEDIATION STEPS**

---

## Remediation Steps (Confirmed Incident)

### Step 1: Block Evidence Serving (IMMEDIATE)

```python
# Emergency feature flag to halt all evidence exports
# Add to runtime.env
XR7_EVIDENCE_SERVING_ENABLED=false
```

Restart API pods. This prevents tampered evidence from reaching attorneys.

### Step 2: Isolate Affected Claims

Query all claims with failed verification:

```sql
-- Run this against read replica to avoid load
SELECT claim_id, artist_id, evidence->>'integrity'->>'packet_hash'
FROM claims
WHERE evidence IS NOT NULL
AND deleted_at IS NULL;
```

Export results to CSV for forensic analysis.

### Step 3: Determine Tampering Scope

Run full chain verification across all tenants:

```bash
# Trigger verification task manually
celery -A XR7.celery_app call xr7.chain_verification.verify_all_tenants_chain_integrity_task
```

Capture output containing `tampering_detected_count`. If > 1% of evidence packets affected → **Database compromise suspected**.

### Step 4: Notify Stakeholders

**Internal:**
- Engineering lead (Slack: #eng-incidents)
- Security team (PagerDuty escalation)
- CTO (if > 10 tenants affected)

**External (if evidence already delivered to attorneys):**
- Affected artists via support ticket (do NOT mention "tampering" — use "technical issue requiring evidence re-verification")
- Legal counsel (assess liability exposure)

### Step 5: Restore Evidence Integrity

**If database backup is clean:**

```bash
# Restore from last known-good backup
# See docs/operations/DISASTER-RECOVERY.md
./scripts/restore_from_backup.sh --date=YYYY-MM-DD --table=claims
```

**If backup is also compromised:**

Evidence must be **regenerated from source data**:

```python
from XR7.recovery.orchestrator import ClaimsOrchestrator
from XR7.db import get_db

db = next(get_db())
orchestrator = ClaimsOrchestrator(db)

# Regenerate evidence for affected claim
claim = db.query(Claim).filter(Claim.id == claim_id).first()
orchestrator.build_evidence_packet(claim)
db.commit()
```

**Verify regenerated evidence:**

```python
from XR7.core.integrity.evidence_crypto import verify_packet_integrity

verification = verify_packet_integrity(claim.evidence)
assert verification["valid"], f"Regeneration failed: {verification}"
```

### Step 6: Root Cause Analysis

**Database access logs:**
```sql
-- PostgreSQL audit log (requires pgaudit extension)
SELECT * FROM pg_audit_log
WHERE object_type = 'TABLE'
AND object_name = 'claims'
AND command_tag IN ('UPDATE', 'DELETE')
AND timestamp > NOW() - INTERVAL '7 days';
```

**Application audit logs:**
```bash
# Search structured logs for evidence modifications
jq 'select(.event == "evidence_modified" or .event == "claim_updated") | select(.extra.claim_id == "CLAIM_ID")' \
  /var/log/xr7/app.log.jsonl
```

**Infrastructure access:**
- Check AWS CloudTrail for database snapshot access
- Check Kubernetes audit logs for pod exec into database pods
- Review IAM temporary credential issuance in last 48 hours

### Step 7: Implement Additional Controls

**If insider threat suspected:**
```sql
-- Revoke all active admin sessions
DELETE FROM admin_sessions WHERE expires_at > NOW();
```

**If database compromise suspected:**
- Rotate all database credentials immediately
- Enable RDS query logging (if not already enabled)
- Review database security group rules
- Enable at-rest encryption if not already active

---

## Post-Incident Actions

### Required Documentation

1. **Incident timeline** (timestamp, action taken, outcome)
2. **Root cause summary** (what failed, why)
3. **Affected claims list** (exported CSV with claim_id, artist_id, remediation status)
4. **Evidence regeneration log** (which packets regenerated, verification results)

### Required Reviews

1. [ ] SOC 2 auditor notification (if in observation period)
2. [ ] Legal review of liability exposure
3. [ ] Customer communication plan (if attorneys received tampered evidence)
4. [ ] Engineering postmortem (5 Whys analysis)

### Follow-up Controls

1. [ ] Enable database-level audit logging (pgaudit)
2. [ ] Implement evidence packet immutability (WORM storage for sealed packets)
3. [ ] Add packet-level timestamp signature (blockchain anchoring)
4. [ ] Increase chain verification frequency (daily → hourly for VIP tenants)

---

## Escalation Path

| Severity | Escalation Trigger | Contact |
|----------|-------------------|---------|
| P0 | > 1 tenant affected OR evidence delivered to attorney | Engineering Lead + Security Team |
| P0 | > 10 tenants affected OR database compromise confirmed | CTO + Legal Counsel |
| P0 | > 100 tenants affected OR public disclosure risk | CEO + External Security Firm |

**On-call rotation:** See PagerDuty schedule `xr7-security-on-call`

---

## Prevention

### Proactive Monitoring

- **Scheduled verification job** runs daily (`xr7-chain-verification-daily`)
- **Verification on read** happens every time evidence is served
- **Anomaly detection** on claim update frequency (>3 evidence regenerations in 24h = investigation)

### Defense in Depth

- Database-level row-level security (RLS) preventing cross-tenant access
- Audit logging at application and database layers
- Immutable storage tier for sealed evidence packets (WORM compliance)
- Multi-signature requirement for evidence packet modification (future)

---

**Last Updated:** 2026-04-19
**Owner:** Security & Platform Engineering
**Review Cadence:** Quarterly or after any chain integrity incident
