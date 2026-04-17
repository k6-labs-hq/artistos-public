# XR7 Security Hardening Plan

**Version:** 1.0
**Compliance targets:** SOC 2 Type II, ISO 27001, OWASP ASVS Level 2
**Scope:** XR7 application, infrastructure, CI/CD pipeline, and third-party integrations
**Owner:** Security Lead + Engineering Lead
**Review cadence:** Quarterly + after any incident

---

## Table of Contents

1. [STRIDE Threat Model](#1-stride-threat-model)
2. [Authentication & Authorization Strategy](#2-authentication--authorization-strategy)
3. [Secrets Management](#3-secrets-management)
4. [Encryption: Transit and At Rest](#4-encryption-transit-and-at-rest)
5. [API Security](#5-api-security)
6. [Input Validation & Output Encoding](#6-input-validation--output-encoding)
7. [Audit Logging](#7-audit-logging)
8. [Least-Privilege Architecture](#8-least-privilege-architecture)
9. [Secure Microservice Communication](#9-secure-microservice-communication)
10. [Dependency & Supply-Chain Security](#10-dependency--supply-chain-security)
11. [Incident Response Plan](#11-incident-response-plan)
12. [Security Hardening Checklist](#12-security-hardening-checklist)
13. [Security Review Playbook](#13-security-review-playbook)

---

## 1. STRIDE Threat Model

STRIDE categorizes threats into six types. This section maps each to XR7-specific attack vectors and mitigations.

### 1.1 Spoofing (Identity Attacks)

**Threats:**
- An attacker claims to be a legitimate artist/admin by replaying a stolen JWT
- A malicious API consumer sends forged `tenant_id` headers
- A compromised n8n workflow acts as an authenticated service

**Mitigations:**
- Short-lived JWTs (access: 15 min; refresh: 7 days) — limits the replay window
- JWT signed with RS256 (asymmetric); public key published at `/.well-known/jwks`
- `tenant_id` extracted from JWT claims, never from request body or headers at trust boundary
- Service-to-service calls use separate, non-expiring service tokens with explicit service scope
- n8n webhooks validate HMAC-SHA256 request signatures

**Residual risk:** MEDIUM — mitigated by short expiry + refresh rotation

---

### 1.2 Tampering (Data Integrity)

**Threats:**
- A statement row is silently modified after ingestion (audit bypass)
- An attacker modifies reconciliation output before it reaches the claims engine
- A database migration is altered post-review

**Mitigations:**
- Every ingested statement file is hashed (SHA-256) at ingestion time; verified at any re-read
- Evidence bundles are sealed with HMAC-SHA256 at generation; signature verified before submission
- All database writes go through SQLAlchemy's ORM layer; raw SQL only in explicitly audited migration files
- Alembic migration files are committed to Git and reviewed in PR before applying
- Immutable event log: every domain event appended, never updated

**Residual risk:** LOW

---

### 1.3 Repudiation (Denial of Actions)

**Threats:**
- An analyst denies approving a claim they approved
- A DSP denies receiving a submission
- A system change is made without traceable authorship

**Mitigations:**
- All write operations log the acting `user_id`, `tenant_id`, `action`, and timestamp to an immutable audit table
- Evidence submission to DSPs returns a signed receipt that is stored alongside the claim
- JWT `jti` (JWT ID) is logged on every authenticated request for non-repudiation
- Git commit signatures (GPG-signed) for all code changes

**Residual risk:** LOW

---

### 1.4 Information Disclosure

**Threats:**
- Tenant A accesses Tenant B's royalty data (horizontal privilege escalation)
- API error messages expose internal stack traces, field names, or SQL
- Log aggregation exposes PII (artist names, earnings amounts) to unauthorized log readers
- Statement files in S3 are accessible without authentication

**Mitigations:**
- Every DB query includes `WHERE tenant_id = :tenant_id` enforced at the repository layer; tested with cross-tenant isolation tests
- All API error responses return generic error codes; stack traces only in debug mode (never in production)
- PII fields (artist name, earnings, ISRC) masked in logs; full values only in encrypted audit logs
- S3/Blob Storage uses pre-signed URLs with 15-minute expiry; no bucket-level public access
- Database credentials never in application logs or error responses

**Residual risk:** LOW (pending log masking implementation)

---

### 1.5 Denial of Service

**Threats:**
- A large malicious statement file (1 TB) crashes the ingestion service
- A rate-limit bypass floods the claims API
- A large SQL query from a tenant freezes the shared DB connection pool

**Mitigations:**
- File upload size cap: 500 MB max (enforced at API gateway + nginx)
- Rate limiting: 100 req/min per tenant by default; configurable per tier (via Redis token bucket)
- Query timeout: 30 seconds max per query (PostgreSQL `statement_timeout`)
- Connection pool limits per tenant segment; connection pool monitoring alert at 80% saturation
- Celery queue depth monitored; automatic worker scaling via KEDA

**Residual risk:** MEDIUM (large file attack partially mitigated; DDoS mitigation requires CDN layer)

---

### 1.6 Elevation of Privilege

**Threats:**
- A regular user accesses admin-only endpoints by guessing/crafting a URL
- A service worker JWT is compromised and used to access arbitrary tenant data
- A Celery worker running as root executes an arbitrary command injection

**Mitigations:**
- RBAC enforced at the FastAPI dependency layer; every endpoint has an explicit `Requires[role]` dependency
- Service tokens scoped to specific service names; cannot access tenant data directly
- Celery workers run as `nobody` (non-root, no shell); no `eval`, `exec`, or `subprocess` in worker code
- SQL injection: SQLAlchemy ORM exclusively; no f-string SQL; bandit scan in CI detects raw SQL

**Residual risk:** LOW

---

## 2. Authentication & Authorization Strategy

### 2.1 Authentication Flow

```
[Client] ──POST /auth/token──► [FastAPI Auth Service]
         username+password        │
                                  ├─ bcrypt password verify
                                  ├─ Check account_active
                                  └─ Issue RS256 JWT

JWT Payload:
{
  "sub": "user_id",
  "tenant_id": "uuid",
  "role": "artist|admin|analyst|service",
  "iat": <epoch>,
  "exp": <epoch + 900>,   ← 15 minutes
  "jti": "unique-jwt-id"
}
```

### 2.2 JWT Public Key Rotation

- RS256 key pair rotated every 90 days
- Old public key remains in JWKS for 24 hours after rotation (JWT grace period)
- Rotation automated via `scripts/rotate_jwt_keys.py`; requires two human approvals

### 2.3 RBAC Roles

| Role | Description | Scope |
|------|-------------|-------|
| `artist` | Read own earnings, claims; submit new claims | `tenant_id` = own |
| `analyst` | Read/write all tenant data; approve claims | `tenant_id` = any |
| `admin` | Full system access including user management | Global |
| `service` | Internal service-to-service; no user data access | Scoped by service name |
| `readonly` | Read-only access to own tenant; no write | `tenant_id` = own |

---

## 3. Secrets Management

### 3.1 Secret Categories

| Secret type | Storage | Rotation |
|-------------|---------|---------|
| Database credentials | HashiCorp Vault (dynamic) | Every 2 hours (dynamic) |
| JWT signing key (RSA private) | Vault KV v2 | Every 90 days |
| DSP API credentials | Vault KV v2 | Per DSP agreement |
| Redis password | Vault KV v2 | Every 30 days |
| S3 access keys | AWS IAM roles (no long-lived keys) | Automatic (STS) |
| Stripe / payment keys | Vault KV v2 | Annually |

### 3.2 Secret Injection (No Hard-Coded Secrets)

Application reads secrets via Vault Agent sidecar:
```python
# config.py — reads from environment (populated by Vault Agent)
class Settings(BaseSettings):
    database_url: SecretStr          # VAULT_INJECT: db/creds/xr7
    jwt_private_key: SecretStr       # VAULT_INJECT: kv/jwt/private_key
    redis_url: SecretStr             # VAULT_INJECT: kv/redis/url

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
```

### 3.3 CI/CD Secrets

- GitHub Actions secrets used only for deployment credentials
- Never print secrets in CI logs: `add-mask` applied to all secret values
- bandit CI scan catches any accidental hard-coded credentials (`B105`, `B106`, `B107`)

---

## 4. Encryption: Transit and At Rest

### 4.1 In Transit

| Channel | Protocol | Notes |
|---------|----------|-------|
| Client → API Gateway | TLS 1.3 minimum; TLS 1.2 deprecated | HSTS enforced (max-age=31536000) |
| Service → Service | mTLS (mutual TLS) via Istio sidecar | Certificate rotation: 24h |
| App → Database | TLS with server cert validation | `ssl_mode=verify-full` |
| App → Redis | TLS (stunnel in non-Kubernetes deployments) | Auth via username+password |
| App → S3/Blob | HTTPS; AWS SigV4 signing | No HTTP allowed |

### 4.2 At Rest

| Data | Algorithm | Key management |
|------|-----------|---------------|
| Database (full) | AES-256-GCM (PostgreSQL Transparent Data Encryption) | Cloud KMS |
| Statement files (S3) | AES-256 SSE-S3 (server-side encryption) | AWS KMS |
| Evidence bundles | AES-256-GCM + HMAC-SHA256 seal | Vault KMS |
| PII fields (artist name, earnings) | AES-256 column encryption at application layer | Vault Transit |
| JWT private key | Vault Transit (never leaves Vault; operations in Vault) | Vault KMS |

### 4.3 PII Encryption at Application Layer

For the highest-sensitivity fields, encrypt before DB insert:
```python
from XR7.security.vault_transit import vault_encrypt, vault_decrypt

class Party(Base):
    name_encrypted: str  # encrypted blob stored in DB

    @property
    def name(self) -> str:
        return vault_decrypt(self.name_encrypted)

    @name.setter
    def name(self, value: str):
        self.name_encrypted = vault_encrypt(value)
```

---

## 5. API Security

### 5.1 OWASP API Security Top 10 — XR7 Mitigations

| OWASP API Risk | XR7 Mitigation |
|---------------|---------------|
| **API1: Broken Object Level Auth** | Every query includes `WHERE tenant_id = :tid`; cross-tenant tests in CI |
| **API2: Broken Authentication** | RS256 JWT; 15-min expiry; refresh rotation; no Basic Auth on production |
| **API3: Excessive Data Exposure** | Pydantic response models explicitly list allowed fields; no ORM-to-JSON serialization shortcuts |
| **API4: Lack of Resources & Rate Limiting** | 100 req/min per tenant; 10 MB request body max; Redis token bucket rate limiter |
| **API5: Broken Function Level Auth** | Every endpoint has explicit RBAC dependency; tests verify unauthorized access returns 403 |
| **API6: Mass Assignment** | SQLAlchemy model update only allows explicitly whitelisted fields via `model_update()` |
| **API7: Security Misconfiguration** | Helmet-equivalent headers via `starlette.middleware.cors + SecurityHeadersMiddleware` |
| **API8: Injection** | Pydantic validation; SQLAlchemy ORM only; no raw SQL; bandit scan in CI |
| **API9: Improper Assets Management** | Single versioned OpenAPI spec; no shadow/test endpoints in production |
| **API10: Insufficient Logging** | Every request logged with `request_id`, `user_id`, `tenant_id`, `status_code`, `latency_ms` |

### 5.2 Security Headers

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=()"
        return response
```

### 5.3 CORS Policy

```python
CORSMiddleware(
    app,
    allow_origins=settings.cors_allowed_origins,  # from Vault; never "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
```

---

## 6. Input Validation & Output Encoding

### 6.1 Pydantic as the Trust Boundary

All inputs entering XR7 via API pass through a Pydantic model before any processing:
- String fields: max-length constraints enforced
- UUID fields: validated as UUID v4
- Date fields: ISO 8601 format enforced
- Monetary fields: `Decimal` type; negative value check where appropriate
- Enum fields: only allowed values accepted; unknown values return 422

### 6.2 File Upload Validation

Ingested statement files are validated before any parsing:
```python
ALLOWED_CONTENT_TYPES = {"text/csv", "application/xml", "application/json", "application/zip"}
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

async def validate_upload(file: UploadFile):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    content = await file.read(MAX_FILE_SIZE_BYTES + 1)
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    return content
```

### 6.3 SQL Injection Prevention

- SQLAlchemy ORM exclusively for all queries
- `Text()` literals only in migration scripts (reviewed separately)
- bandit rule `B608` (SQL injection via string formatting) enabled in CI

---

## 7. Audit Logging

### 7.1 Audit Event Schema

```sql
CREATE TABLE audit_events (
    event_id       UUID PRIMARY KEY,
    tenant_id      UUID NOT NULL,
    user_id        UUID,
    service_name   VARCHAR(50),
    action         VARCHAR(100) NOT NULL,  -- 'claim.submitted', 'user.created'
    entity_type    VARCHAR(50),
    entity_id      VARCHAR(100),
    old_value      JSONB,                  -- for updates: previous value
    new_value      JSONB,                  -- for updates: new value
    ip_address     INET,
    user_agent     TEXT,
    request_id     UUID,
    jti            VARCHAR(100),           -- JWT ID for non-repudiation
    occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_occurred ON audit_events (tenant_id, occurred_at);
CREATE INDEX idx_audit_entity ON audit_events (entity_type, entity_id, occurred_at);
```

### 7.2 What Is Always Audited

- User login / logout / token refresh
- Any write to `claims`, `recoveries`, `parties` (creates, updates, state changes)
- File ingestion start and completion
- Evidence bundle generation and sealing
- Admin actions: user creation, role change, tenant creation
- Authentication failures > 3 consecutive attempts

### 7.3 Audit Log Retention

- Hot (PostgreSQL): 90 days
- Cold (S3, compressed, immutable bucket policy): 7 years (SOC 2 + regulatory requirement)
- Audit logs are excluded from standard log redaction rules (they are separately encrypted)

---

## 8. Least-Privilege Architecture

### 8.1 Database Roles

```sql
-- Application reads/writes (most operations)
CREATE ROLE xr7_app LOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO xr7_app;
REVOKE TRUNCATE, DROP, ALTER ON ALL TABLES IN SCHEMA public FROM xr7_app;

-- Migration runner (only during deployments)
CREATE ROLE xr7_migration LOGIN;
GRANT ALL ON ALL TABLES IN SCHEMA public TO xr7_migration;
-- Password stored only in Vault; rotated after each migration run

-- Read-only analytics (reporting queries, BI tools)
CREATE ROLE xr7_readonly LOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO xr7_readonly;
```

### 8.2 Kubernetes RBAC

```yaml
# Each microservice has its own ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: xr7-ingestion-role
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    resourceNames: ["xr7-ingestion-config"]   # Only its own config
    verbs: ["get", "watch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: []   # No pod management
```

### 8.3 Cloud IAM (AWS / GCP / Azure)

- Each microservice has its own cloud IAM role with minimal permissions
- Ingestion service: `s3:GetObject`, `s3:PutObject` on ingestion bucket only
- ML service: `s3:GetObject` on model artifacts bucket; no write
- No IAM roles with `*` actions or `*` resources
- IAM role trust policies scoped to specific Kubernetes namespace + service account

---

## 9. Secure Microservice Communication

### 9.1 Service Mesh (Istio)

All pod-to-pod traffic enforced mTLS via Istio:
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: xr7
spec:
  mtls:
    mode: STRICT   # No plaintext pod-to-pod allowed
```

### 9.2 Authorization Policies

```yaml
# xr7-claims may only be called from xr7-recovery and xr7-gateway
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: xr7-claims-access
spec:
  selector:
    matchLabels:
      app: xr7-claims
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/xr7/sa/xr7-recovery"
              - "cluster.local/ns/xr7/sa/xr7-gateway"
```

---

## 10. Dependency & Supply-Chain Security

### 10.1 Dependency Scanning

- `pip-audit` runs in nightly CI (`nightly-analysis.yml`)
- Critical/High CVEs block production deployment
- Dependabot configured for Python dependencies (weekly PR)

### 10.2 Container Image Scanning

- Trivy full-image scan on every Docker build (in `production-deploy.yml`)
- Base image: `python:3.12-slim-bookworm` (minimal attack surface)
- No packages installed as root in Dockerfile; non-root user at runtime

```dockerfile
FROM python:3.12-slim-bookworm
RUN groupadd -r xr7 && useradd -r -g xr7 xr7
# ... install deps ...
USER xr7
```

### 10.3 Software Bill of Materials (SBOM)

Generated on every production build:
```bash
syft packages . --output cyclonedx-json > sbom-$(git rev-parse --short HEAD).json
```

SBOM stored in the release artifact; enables rapid identification of affected builds when new CVEs are published.

### 10.4 Pinned Dependencies

All `requirements.txt` entries are pinned to exact versions (`==`). Upgrades happen explicitly via PRs, not floating `>=` ranges. This prevents silent supply-chain attacks via dependency updates.

---

## 11. Incident Response Plan

### 11.1 Severity Levels

| Level | Examples | Response time |
|-------|----------|--------------|
| **P0 Critical** | Data breach; PII exposed; system-wide outage | < 15 minutes |
| **P1 High** | Cross-tenant data leak; authentication bypass; claims data corruption | < 1 hour |
| **P2 Medium** | Performance degradation >50%; single-tenant outage; ML model failure | < 4 hours |
| **P3 Low** | Non-critical feature failure; elevated error rate <10% | < 24 hours |

### 11.2 Response Procedure

**P0/P1 Steps:**

1. **Detect** — Automated alert fires (Grafana/Datadog/PagerDuty)
2. **Contain** — On-call engineer: isolate affected service (Kubernetes namespace netpol block); revoke compromised credentials in Vault
3. **Assess** — Security lead joins; determine scope: how many tenants affected, what data accessed
4. **Communicate (internal)** — Incident Slack channel `#incident-response`; status page update
5. **Eradicate** — Patch + redeploy; rotate all credentials in affected path
6. **Recover** — Restore from last clean snapshot if data integrity compromised; replay events from event bus
7. **Communicate (external)** — If PII breach: notify affected tenants; GDPR 72-hour notification clock starts at detection
8. **Post-mortem** — Blameless post-mortem within 5 business days; published as internal RFC

### 11.3 Data Breach Response (GDPR/CCPA)

- GDPR breach notification: 72 hours to supervisory authority after becoming "aware"
- CCPA breach: notify affected California residents "in the most expedient time possible"
- Template breach notification letter stored at `docs/templates/breach_notification_template.md`

---

## 12. Security Hardening Checklist

### Authentication & Authorization
- [ ] JWT access tokens expire in ≤ 15 minutes
- [ ] JWT refresh tokens expire in ≤ 7 days; single-use (rotated on use)
- [ ] RS256 signing (asymmetric); no HS256 (symmetric) in production
- [ ] JWKS endpoint published; signature verified on every request
- [ ] Every API endpoint has explicit RBAC dependency annotated
- [ ] Cross-tenant isolation tested: tenant A cannot read tenant B's data
- [ ] Password stored as bcrypt (cost factor ≥ 12); no MD5/SHA1 passwords

### Secrets Management
- [ ] Zero hard-coded secrets in codebase (bandit B105/B106/B107 scan passing)
- [ ] All secrets injected via Vault Agent or environment variables
- [ ] Database credentials rotated every 2 hours (Vault dynamic credentials)
- [ ] JWT signing key rotated every 90 days (automated)
- [ ] No secrets in Docker build context; no `ENV` secrets in Dockerfile

### Encryption
- [ ] TLS 1.3 enforced for all external traffic; TLS 1.1 disabled
- [ ] HSTS header with max-age ≥ 31536000 deployed
- [ ] mTLS enforced for all pod-to-pod traffic (Istio STRICT mode)
- [ ] Database connections use `ssl_mode=verify-full`
- [ ] S3 objects encrypted with SSE-KMS; no public buckets
- [ ] PII fields encrypted at application layer before DB insert

### API Security
- [ ] Rate limiting: 100 req/min per tenant (configurable)
- [ ] File upload size limit: 500 MB enforced at gateway + application
- [ ] CORS `allow_origins` does not include `*` in production
- [ ] All security headers present (CSP, HSTS, X-Frame-Options, X-Content-Type)
- [ ] No stack traces in production error responses
- [ ] OpenAPI spec has no endpoints without security requirements

### Input Validation
- [ ] All API inputs validated through Pydantic models
- [ ] File uploads: content-type validation + magic-bytes check
- [ ] No f-string SQL; SQLAlchemy ORM exclusively
- [ ] No `eval()`, `exec()`, `__import__()` in application code (bandit scan)
- [ ] No SSRF risk: URL parameters not used for server-side HTTP calls without allowlist

### Audit & Logging
- [ ] All write operations logged to `audit_events` table with user_id + tenant_id
- [ ] Authentication failures logged; alert on ≥ 5 failures/minute per IP
- [ ] PII fields masked in application logs
- [ ] Audit logs retained 7 years in immutable cold storage
- [ ] JWT `jti` logged on every authenticated request

### Infrastructure
- [ ] Kubernetes RBAC: no `cluster-admin` for application service accounts
- [ ] Pod security: all containers run as non-root
- [ ] Network policies: deny-all default; explicit allow for required paths
- [ ] Trivy scan passing on every container build (no Critical/High CVEs)
- [ ] pip-audit passing in nightly CI (no Critical CVEs unaddressed)
- [ ] SBOM generated per production build
- [ ] Dependencies pinned to exact versions in `requirements.txt`

### Incident Response
- [ ] PagerDuty/OpsGenie on-call rotation configured
- [ ] Security incident runbook accessible to all engineers
- [ ] Breach notification templates prepared (GDPR + CCPA)
- [ ] Post-mortem process documented

---

## 13. Security Review Playbook

### When to Trigger a Security Review

A security review is required for any PR that:
- Adds a new authentication or authorization mechanism
- Changes JWT handling, password hashing, or session management
- Adds new external API integrations (DSP, PRO, payment processor)
- Introduces file upload or processing functionality
- Adds new database tables containing PII or financial data
- Changes encryption key management
- Modifies CORS, CSP, or security header configuration
- Introduces any new dependency that handles cryptography

### Security Review Process

**Step 1: Self-Review (author)**
- Complete the Security Hardening Checklist items relevant to the change
- Run `bandit -r XR7/ shared/` locally; zero high/critical issues

**Step 2: Automated Scan (CI)**
- CI runs bandit, pip-audit, Trivy on branch
- All findings documented in PR; critical/high block merge

**Step 3: Peer Security Review (reviewer)**
- Reviewer uses [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- Reviewer evaluates: injection risk, auth bypass risk, data exposure risk
- For auth changes: reviewer must test the change manually in staging

**Step 4: Security Lead Sign-Off (for architectural changes)**
- Any change to authentication flows, encryption schemes, or new external integrations
- Security lead documents their review in the PR as a review comment

### Security Regression Testing

After any security review, run the security test suite:
```bash
pytest tests/security/ -v
```

Security tests cover:
- `test_cross_tenant_isolation.py` — tenant A cannot access tenant B's records
- `test_auth_bypass_attempts.py` — invalid JWTs, expired JWTs, tampered JWTs all return 401
- `test_input_validation.py` — oversized files, invalid types, SQL injection attempts return 422/413/415
- `test_rate_limiting.py` — requests beyond rate limit return 429
- `test_rbac_enforcement.py` — artist role cannot access admin endpoints
