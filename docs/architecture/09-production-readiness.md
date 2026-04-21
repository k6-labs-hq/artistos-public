# 09 — Production Readiness Checklist

> **Gate for: putting ArtistOS on a public URL that handles a real artist's data.**
> This is the deploy-time go/no-go. Every item must be **✅ done** or **🟡 risk-accepted** before prod cutover. Link each check to a PR or runbook as evidence.

## How to use this doc

- Work the checklist top-to-bottom. Top items block later items.
- Every `☐` must become `✅` (done) or `🟡 <reason>` (risk accepted with an owner and follow-up issue) before prod launch.
- The **Evidence** column is mandatory — a link to a PR, test, screenshot, or runbook proving the check passes.
- Re-run this checklist end-to-end before any major release, not just first launch.

---

## 1. Code that starts and does its job

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 1.1 | ☐ API container starts cleanly on a fresh DB with `alembic upgrade head` + `uvicorn` and serves `/health` 200 | | [#104](https://github.com/k6-labs-hq/ArtistOS/issues/104) |
| 1.2 | ☐ Frontend builds and serves without missing imports | | |
| 1.3 | ☐ Celery worker + beat start and process at least one task type end-to-end | | |
| 1.4 | ☐ Full MVP happy path works locally: artist created → statement uploaded → anomaly surfaced → claim drafted → PDF bundle generated | | |
| 1.5 | ☐ Test suite passes on CI (not admin-merged past failures) | | |

## 2. Schema + data integrity

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 2.1 | ☐ No code column/constraint references that have no Alembic migration (e.g., `artists.deleted_at`, ON CONFLICT constraints) | | |
| 2.2 | ☐ `alembic upgrade head` runs clean against both empty DB and production-shaped DB | | [#51](https://github.com/k6-labs-hq/ArtistOS/issues/51) |
| 2.3 | ☐ At least one restore-from-backup drill completed on a staging DB | | [#49](https://github.com/k6-labs-hq/ArtistOS/issues/49) |
| 2.4 | ☐ PII column inventory produced; data classification applied | | |

## 3. Secrets + identity

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 3.1 | ☐ No secrets in the repo or container image (grep for `minioadmin`, `change-me`, `admin-secret`) | | [#3](https://github.com/k6-labs-hq/ArtistOS/issues/3) |
| 3.2 | ☐ `.env` is in `.gitignore`; example file has placeholder values only | | |
| 3.3 | ☐ Production secrets stored in Secrets Manager / 1Password / Doppler (not env vars in CI) | | |
| 3.4 | ☐ Supabase Auth live: artist login goes through `/auth/supabase/exchange`, legacy `artist_login` disabled in prod | | [#100](https://github.com/k6-labs-hq/ArtistOS/issues/100) |
| 3.5 | ☐ Admin auth live: no hardcoded email/password env vars in prod | | [#101](https://github.com/k6-labs-hq/ArtistOS/issues/101) |
| 3.6 | ☐ `XR7_ENFORCE_AUTH_GLOBALLY=1` in prod | | |
| 3.7 | ☐ Production JWT secret has ≥ 48 bytes of entropy and is rotated on launch | | |

## 4. External dependencies + money paths

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 4.1 | ☐ Trolley integration pointed at **sandbox** for pilot; production mode gated behind feature flag | | |
| 4.2 | ☐ Circuit breaker + retry verified for Trolley, HubSpot, LLM providers | | [#27](https://github.com/k6-labs-hq/ArtistOS/issues/27), [#50](https://github.com/k6-labs-hq/ArtistOS/issues/50), [#72](https://github.com/k6-labs-hq/ArtistOS/issues/72) |
| 4.3 | ☐ Billing invariants enforced (fee < gross, artist_net ≥ 0) verified by tests | | [#81](https://github.com/k6-labs-hq/ArtistOS/issues/81) |
| 4.4 | ☐ ISO 4217 currency validation enforced on all claim amount paths | | [#77](https://github.com/k6-labs-hq/ArtistOS/issues/77) |
| 4.5 | ☐ Immutable audit log writes on every claim status transition | | [#76](https://github.com/k6-labs-hq/ArtistOS/issues/76) |

## 5. Observability

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 5.1 | ☐ Prometheus `/metrics` endpoint live; HTTP + business metrics exported | | [#94](https://github.com/k6-labs-hq/ArtistOS/issues/94) |
| 5.2 | ☐ Celery metrics exported (queue depth, task duration, failure rate) | | [#95](https://github.com/k6-labs-hq/ArtistOS/issues/95) |
| 5.3 | ☐ Grafana dashboard covering API latency p95/p99, error rate, Celery backlog, DB connections | | [#96](https://github.com/k6-labs-hq/ArtistOS/issues/96) |
| 5.4 | ☐ Alert on p95 latency > 1s, error rate > 5%, DB pool > 80% — fires to a channel someone actually watches | | |
| 5.5 | ☐ Structured logging with request trace IDs; logs aggregated (CloudWatch / Loki / hosted) | | [#36](https://github.com/k6-labs-hq/ArtistOS/issues/36) |
| 5.6 | ☐ Health endpoint verifies real dependencies (DB, Redis, S3), not just app liveness | | [#74](https://github.com/k6-labs-hq/ArtistOS/issues/74) |

## 6. Infrastructure

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 6.1 | ☐ Compute target provisioned (ECS Fargate / App Runner / Hetzner VM) | | [#102](https://github.com/k6-labs-hq/ArtistOS/issues/102) |
| 6.2 | ☐ Managed Postgres with automated daily backups + point-in-time recovery | | |
| 6.3 | ☐ Redis / queue with persistence or replication | | |
| 6.4 | ☐ S3 bucket for uploads + evidence bundles; lifecycle + versioning enabled | | |
| 6.5 | ☐ TLS termination via ACM / Let's Encrypt; HTTP → HTTPS redirect | | |
| 6.6 | ☐ DNS record + domain configured | | |
| 6.7 | ☐ Outbound egress only to known third parties (Trolley, Supabase, LLM provider) | | |
| 6.8 | ☐ Database connection pool bounded (`pool_size`, `pool_recycle`) | | [#42](https://github.com/k6-labs-hq/ArtistOS/issues/42) |
| 6.9 | ☐ Request body size limit middleware active | | [#73](https://github.com/k6-labs-hq/ArtistOS/issues/73) |
| 6.10 | ☐ Upload rate limiting on per-artist basis | | [#80](https://github.com/k6-labs-hq/ArtistOS/issues/80) |

## 7. Deployment + rollback

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 7.1 | ☐ CI builds and pushes a Docker image on merge to `main` | | |
| 7.2 | ☐ Staging environment exists and is on the same commit as prod before prod deploys | | [#41](https://github.com/k6-labs-hq/ArtistOS/issues/41) |
| 7.3 | ☐ Smoke test runs automatically against staging after each deploy | | |
| 7.4 | ☐ Rollback playbook: last-known-good image + migration downgrade procedure documented | | |
| 7.5 | ☐ Alembic migrations are reversible OR explicitly marked one-way with pre-deploy backup | | |
| 7.6 | ☐ Maintenance-mode response (static 503) if API is down | | |

## 8. Compliance + legal

| # | Check | Evidence | Blocker issue |
|---|-------|----------|---------------|
| 8.1 | ☐ Terms of Service visible; artists must accept before first upload | | |
| 8.2 | ☐ Privacy policy published at a stable URL | | |
| 8.3 | ☐ GDPR erasure endpoint tested end-to-end with an audit trail | | [#28](https://github.com/k6-labs-hq/ArtistOS/issues/28), [#32](https://github.com/k6-labs-hq/ArtistOS/issues/32) |
| 8.4 | ☐ Data export ("give me my data") endpoint live | | |
| 8.5 | ☐ Contractual scope of data processing defined with first pilot artist | | |

## 9. Go / no-go sign-off

Before cutting over:

| # | Check | Sign-off |
|---|-------|----------|
| 9.1 | ☐ CTO sign-off on sections 1–6 | |
| 9.2 | ☐ Product/CEO sign-off on section 8 | |
| 9.3 | ☐ Pilot artist expectations documented (SLA, communication channel, support hours) | |
| 9.4 | ☐ Incident response: who gets paged, at what phone number, who is backup | |

---

## Notes

- This is a deploy-time gate, **not** a code-quality gate. See [architecture_acceptance_checklist.md](../architecture_acceptance_checklist.md) and [code_review_checklist.md](../code_review_checklist.md) for those.
- Hetzner vs AWS: section 6 maps to both. Some items (e.g., ACM → Let's Encrypt, App Runner → Docker + Caddy on a VM) change vendor but the check itself stays the same.
- Post-launch: revisit section 5 (observability) weekly for the first month. Alerts are only real if someone responds.
