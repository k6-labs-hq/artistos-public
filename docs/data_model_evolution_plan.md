# XR7 Data Model Evolution Plan

**Version:** 1.0  
**Scope:** Long-term roadmap for XR7 schema evolution across 3–5 major versions.  
**Horizon:** XR7 v2 (current) → XR7 v6 (target, ~2028)  
**Principle:** Every schema change is backward-compatible until an explicit deprecation period expires. No breaking changes without a 6-month notice period.

---

## Table of Contents

1. [Core Entity Inventory](#1-core-entity-inventory)
2. [Versioned Schema Evolution](#2-versioned-schema-evolution)
3. [Backward-Compatibility Strategy](#3-backward-compatibility-strategy)
4. [Forward-Compatible Migration Strategy](#4-forward-compatible-migration-strategy)
5. [New DSP/PRO Format Handling](#5-new-dspro-format-handling)
6. [Metadata Enrichment & Normalization Plans](#6-metadata-enrichment--normalization-plans)
7. [API and Service Versioning](#7-api-and-service-versioning)
8. [Deprecation Plan](#8-deprecation-plan)
9. [Schema Validation & Enforcement](#9-schema-validation--enforcement)
10. [Data Model Governance Guide](#10-data-model-governance-guide)
11. [Schema Change Approval Checklist](#11-schema-change-approval-checklist)
12. [Safe Migration Playbook](#12-safe-migration-playbook)

---

## 1. Core Entity Inventory

The eight canonical entities in XR7's domain model:

| Entity | Identifies | Primary key | Current version |
|--------|-----------|-------------|----------------|
| **Work** | A musical composition (song) | `work_id` (UUID) | v2 |
| **Recording** | A specific recorded performance of a Work | `recording_id` (UUID), ISRC | v2 |
| **Party** | A person or org holding rights | `party_id` (UUID), IPN, ISNI | v2 |
| **Statement** | A DSP royalty report for a period | `statement_id` (UUID) | v2 |
| **Claim** | A rights recovery claim against a DSP | `claim_id` (string) | v2 |
| **Match** | A resolved link between a Statement row and a Work/Recording | `match_id` (UUID) | v2 |
| **Reconciliation** | A computed comparison of actual vs. expected royalties | `reconciliation_id` (UUID) | v2 |
| **Recovery** | A capital advance event linked to a Claim | `recovery_id` (UUID) | v2 |

---

## 2. Versioned Schema Evolution

### 2.1 Work Entity

**v2 (current):**
```sql
CREATE TABLE works (
    work_id         UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL,
    iswc            VARCHAR(11),                -- T-034524680-1
    work_title      VARCHAR(500) NOT NULL,
    language        VARCHAR(5),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);
```

**v3 additions (XR7 3.0 — 2026 Q4):**
```sql
ALTER TABLE works
    ADD COLUMN work_title_normalized   VARCHAR(500),  -- lowercase, no punct
    ADD COLUMN alternate_titles        JSONB,          -- {"en": [...], "es": [...]}
    ADD COLUMN duration_seconds        INTEGER,
    ADD COLUMN genre                   VARCHAR(50),
    ADD COLUMN language_of_text        VARCHAR(5),
    ADD COLUMN copyright_year          SMALLINT,
    ADD COLUMN original_publisher_id   UUID REFERENCES parties(party_id),
    ADD COLUMN cue_sheet_eligible      BOOLEAN DEFAULT FALSE;
-- Rationale: support TV/film sync cue sheets and metadata enrichment
```

**v4 additions (XR7 4.0 — 2027 Q2):**
```sql
ALTER TABLE works
    ADD COLUMN iswc_list       JSONB,   -- works can have multiple ISWCs (foreign society variations)
    ADD COLUMN society_codes   JSONB,   -- {"ascap": "...", "bmi": "...", "prs": "..."}
    ADD COLUMN catalog_version INTEGER DEFAULT 1;  -- optimistic locking
```

**v5 additions (XR7 5.0 — 2027 Q4):**
```sql
ALTER TABLE works
    ADD COLUMN ai_generated           BOOLEAN DEFAULT FALSE,
    ADD COLUMN stem_work_ids          UUID[],   -- for AI-derived or sampled works
    ADD COLUMN metadata_confidence    NUMERIC(4,3),  -- 0.000–1.000 from enrichment ML
    ADD COLUMN enrichment_source      VARCHAR(50);   -- "musicbrainz", "allmusic", "manual"
```

---

### 2.2 Recording Entity

**v2 (current):**
```sql
CREATE TABLE recordings (
    recording_id    UUID PRIMARY KEY,
    work_id         UUID REFERENCES works(work_id),
    tenant_id       UUID NOT NULL,
    isrc            VARCHAR(12) NOT NULL,
    recording_title VARCHAR(500),
    artist_id       UUID REFERENCES users(id),
    label_id        UUID,
    release_date    DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**v3 additions:**
```sql
ALTER TABLE recordings
    ADD COLUMN isrc_list           JSONB,          -- multiple ISRCs for the same recording
    ADD COLUMN duration_seconds    INTEGER,
    ADD COLUMN explicit_content    BOOLEAN DEFAULT FALSE,
    ADD COLUMN territory_codes     JSONB,          -- ISO 3166-1 alpha-2 list
    ADD COLUMN dsp_ids             JSONB;          -- {"spotify": "...", "apple": "..."}
-- dsp_ids enables direct DSP→recording resolution without ISRC lookup
```

**v4 additions:**
```sql
ALTER TABLE recordings
    ADD COLUMN audio_fingerprint_id   UUID,        -- links to fingerprint_registry
    ADD COLUMN sample_recordings      UUID[],       -- recordings this one samples
    ADD COLUMN remixed_from_id        UUID REFERENCES recordings(recording_id),
    ADD COLUMN dolby_atmos            BOOLEAN DEFAULT FALSE,
    ADD COLUMN spatial_audio_type     VARCHAR(20);  -- "atmos", "sony360", "binaural"
```

---

### 2.3 Party Entity

**v2 (current):**
```sql
CREATE TABLE parties (
    party_id    UUID PRIMARY KEY,
    tenant_id   UUID NOT NULL,
    name        VARCHAR(500) NOT NULL,
    party_type  VARCHAR(20) NOT NULL,  -- 'artist', 'songwriter', 'publisher', 'label'
    ipn         VARCHAR(11),           -- International Performer Number
    isni        VARCHAR(16),           -- International Standard Name Identifier
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**v3 additions:**
```sql
ALTER TABLE parties
    ADD COLUMN name_normalized      VARCHAR(500),   -- ASCII-folded, lowercase
    ADD COLUMN alternate_names      JSONB,
    ADD COLUMN ipi_number           VARCHAR(11),    -- Interested Party Information (CAE/IPI)
    ADD COLUMN dpid                 VARCHAR(20),    -- DDEX Party Identifier
    ADD COLUMN territories          JSONB,
    ADD COLUMN society_memberships  JSONB;          -- [{"society": "ASCAP", "id": "..."}]
```

**v5 additions (AI era):**
```sql
ALTER TABLE parties
    ADD COLUMN is_ai_entity          BOOLEAN DEFAULT FALSE,
    ADD COLUMN human_collaborators   UUID[],        -- for AI-collab works
    ADD COLUMN identity_verified     BOOLEAN DEFAULT FALSE,
    ADD COLUMN verification_source   VARCHAR(50);
```

---

### 2.4 Statement Entity

**v2 (current):**
```sql
CREATE TABLE statements (
    statement_id    UUID PRIMARY KEY,
    tenant_id       UUID NOT NULL,
    dsp             VARCHAR(50) NOT NULL,
    period_from     DATE NOT NULL,
    period_to       DATE NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'USD',
    ingestion_id    UUID,
    raw_file_key    VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**v3 additions:**
```sql
ALTER TABLE statements
    ADD COLUMN format_version    VARCHAR(20),       -- "DDEX_ERN_3.8.2", "CRB_2024", etc.
    ADD COLUMN row_count         INTEGER,
    ADD COLUMN total_reported    NUMERIC(14,4),
    ADD COLUMN checksum          VARCHAR(64),       -- SHA-256 of raw file
    ADD COLUMN territory         CHAR(2),           -- ISO territory for this statement
    ADD COLUMN statement_type    VARCHAR(30);       -- 'streaming', 'download', 'performance'
```

**v4 additions:**
```sql
ALTER TABLE statements
    ADD COLUMN multi_territory   BOOLEAN DEFAULT FALSE,    -- single file covers multiple territories
    ADD COLUMN pro_ref           VARCHAR(50),               -- PRO statement reference number
    ADD COLUMN exchange_rate_snapshot JSONB,               -- rates at statement date
    ADD COLUMN statement_version  INTEGER DEFAULT 1,       -- amended statement tracking
    ADD COLUMN parent_statement_id UUID REFERENCES statements(statement_id);
```

---

### 2.5 Claim Entity

**v2 (current):**
```sql
CREATE TABLE claims (
    claim_id    VARCHAR(50) PRIMARY KEY,
    tenant_id   UUID NOT NULL,
    artist_id   UUID NOT NULL,
    isrc        VARCHAR(12),
    work_title  VARCHAR(500),
    payer       VARCHAR(50),
    state       VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    amount_usd  NUMERIC(12,2),
    period_from DATE,
    period_to   DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**v3 additions:**
```sql
ALTER TABLE claims
    ADD COLUMN claim_type        VARCHAR(20) DEFAULT 'underpayment',
    -- 'underpayment', 'non_payment', 'metadata_error', 'rate_dispute'
    ADD COLUMN priority          VARCHAR(10) DEFAULT 'standard',
    -- 'standard', 'high', 'urgent'
    ADD COLUMN evidence_hash     VARCHAR(64),          -- SHA-256 of sealed evidence
    ADD COLUMN dsp_reference     VARCHAR(100),          -- DSP's internal ticket/ref number
    ADD COLUMN legal_escalated   BOOLEAN DEFAULT FALSE,
    ADD COLUMN assigned_analyst  UUID;
```

**v4 additions:**
```sql
ALTER TABLE claims
    ADD COLUMN recovery_id           UUID REFERENCES recoveries(recovery_id),
    ADD COLUMN bundles               UUID[],            -- claims grouped into submission bundles
    ADD COLUMN estimated_settle_usd  NUMERIC(12,2),     -- ML estimate of likely settlement
    ADD COLUMN settlement_probability NUMERIC(4,3);     -- 0–1 confidence from xr7-ml
```

---

### 2.6 Reconciliation Entity

**v3 additions:**
```sql
ALTER TABLE reconciliation_runs
    ADD COLUMN confidence_score     NUMERIC(4,3),
    ADD COLUMN ml_anomaly_count     INTEGER DEFAULT 0,
    ADD COLUMN variance_row_count   INTEGER DEFAULT 0,
    ADD COLUMN run_type             VARCHAR(20) DEFAULT 'auto',
    -- 'auto', 'manual', 'rerun'
    ADD COLUMN comparison_basis     VARCHAR(30);
    -- 'contract_rate', 'statutory_rate', 'historical_avg'
```

---

## 3. Backward-Compatibility Strategy

### The Rules

1. **Never drop a column** in a backward-incompatible release. Move to a deprecation queue (see Section 8).
2. **Never rename a column** directly. Add the new column, dual-write, verify, then deprecate old.
3. **Never change a column's type** if existing rows would be invalid under the new type.
4. **Never change a required field to required with new constraints** without a migration period.
5. **All API response fields are additive only** for minor versions.

### Column Deprecation Queue

Maintain a `deprecated_columns` table tracking the lifecycle:

```sql
CREATE TABLE schema_deprecations (
    id              SERIAL PRIMARY KEY,
    table_name      VARCHAR(100) NOT NULL,
    column_name     VARCHAR(100) NOT NULL,
    deprecated_in   VARCHAR(10) NOT NULL,   -- 'v3.0'
    remove_in       VARCHAR(10) NOT NULL,   -- 'v5.0'
    replaced_by     VARCHAR(100),
    reason          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. Forward-Compatible Migration Strategy

### Expand-Contract Pattern

Every schema change follows this 3-phase pattern:

**Phase 1 — Expand** (non-breaking, deploy immediately):
```sql
-- Add new nullable column with default
ALTER TABLE works ADD COLUMN work_title_normalized VARCHAR(500);
```

**Phase 2 — Backfill** (background job, no downtime):
```python
# Celery task: backfill_work_title_normalized
async def backfill():
    async for work in Work.iter_all():
        if not work.work_title_normalized:
            work.work_title_normalized = normalize(work.work_title)
            await db.flush()
```

**Phase 3 — Contract** (after all rows backfilled + 1 sprint soak):
```sql
-- Make NOT NULL (safe now — all rows have values)
ALTER TABLE works ALTER COLUMN work_title_normalized SET NOT NULL;
```

### Zero-Downtime Index Creation

```sql
-- CONCURRENT creation — does not lock the table
CREATE INDEX CONCURRENTLY idx_works_title_normalized
    ON works(work_title_normalized);
```

---

## 5. New DSP/PRO Format Handling

### DSP Format Registry

```sql
CREATE TABLE dsp_format_registry (
    format_id       UUID PRIMARY KEY,
    dsp             VARCHAR(50) NOT NULL,
    format_name     VARCHAR(100) NOT NULL,   -- "DDEX_ERN_3.8.2", "Spotify_C2P_v4"
    effective_from  DATE NOT NULL,
    effective_to    DATE,
    parser_class    VARCHAR(200) NOT NULL,   -- Python class path
    field_map       JSONB NOT NULL,          -- {"dsp_field": "xr7_field", ...}
    notes           TEXT
);
```

When a DSP releases a new statement format:

1. Add a row to `dsp_format_registry` with the new parser class path
2. Implement the parser in `XR7/ingestion/parsers/<dsp>_<version>.py`
3. Map DSP fields to XR7 canonical fields in `field_map`
4. No existing code changes required — the ingestion service resolves the parser dynamically

### PRO Format Variations

| PRO | Format | Notes |
|-----|--------|-------|
| ASCAP | CSV (IPI-based) | Quarterly; uses IPI not ISNI |
| BMI | TSV (own format) | Quarterly; uses BMI Work ID |
| PRS (UK) | DDEX-like XML | Monthly |
| SOCAN (CA) | Proprietary CSV | Quarterly |
| SESAC | JSON API | Real-time push |
| GEMA (DE) | XML (GVL variant) | Quarterly |

Each PRO has its own parser class. New societies are onboarded by adding a parser + registry entry — no core changes.

### Foreign Society Variations

Foreign societies often use different identifiers (BUMA/STEMRA uses Dutch work numbers, JASRAC uses Japanese catalog IDs). XR7 resolves these via the `society_codes` JSONB field on the Work entity (added in v4).

---

## 6. Metadata Enrichment & Normalization Plans

### v3: Basic Normalization

- `work_title_normalized`: ASCII-folded, lowercase, punctuation stripped, "feat." removed
- `party.name_normalized`: same rules for artist/party names
- Enables fuzzy title matching for DSPs that use slightly different work titles

### v4: Enrichment Pipeline

A new `xr7-enrichment` background service queries:
- **MusicBrainz** (open database) for ISRC/ISWC cross-references
- **AllMusic** for genre, duration, release date
- **Discogs** for label history

Enrichment data is stored in a separate `enrichment` schema to avoid contaminating canonical data:

```sql
CREATE TABLE enrichment.work_enrichments (
    work_id         UUID REFERENCES works(work_id),
    source          VARCHAR(50),       -- 'musicbrainz', 'allmusic'
    source_id       VARCHAR(100),
    field_name      VARCHAR(100),
    field_value     TEXT,
    confidence      NUMERIC(4,3),
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (work_id, source, field_name)
);
```

Enrichment values are only **promoted** to canonical fields after a confidence threshold (>0.9) and analyst approval.

### v5: ML-Assisted Metadata Repair

- ML model trained on known-good metadata to detect likely errors
- Flags records where `work_title` + `isrc` combination appears anomalous
- Generates repair suggestions stored in `enrichment.repair_suggestions`
- Requires analyst approval before any canonical field is updated

---

## 7. API and Service Versioning

### URL Versioning (introduced in v3)

Starting in XR7 v3.0, all API routes gain a version prefix:

```
/v2/artists/{id}/earnings   ← current (remains supported)
/v3/artists/{id}/earnings   ← v3 additions (richer response)
```

Both are served simultaneously. `/v2` remains supported for 2 major versions after its introduction.

### API Version Policy

| Version | Status | Support ends |
|---------|--------|-------------|
| v2 | Current (2026) | 2028 Q2 |
| v3 | Planned (2026 Q4) | 2029 Q2 |
| v4 | Planned (2027 Q3) | 2030 Q2 |

### Response Schema Versioning

Use `Accept-Version` header for non-URL versioned responses:

```
GET /artists/{id}/earnings
Accept-Version: 2
→ Returns v2 schema (backward-compatible)

GET /artists/{id}/earnings
Accept-Version: 3
→ Returns v3 schema (richer, may add fields)
```

---

## 8. Deprecation Plan

### Deprecated Fields in v2 (remove in v4 — 2027 Q2)

| Table | Column | Deprecated in | Remove in | Replacement |
|-------|--------|---------------|-----------|-------------|
| `statement_rows` | `track_count` | v3.0 | v5.0 | `work_count` |
| `statement_rows` | `track_title` | v3.0 | v5.0 | `work_title` |
| `anomaly_events` | `entity_type = 'track'` | v3.0 | v5.0 | `entity_type = 'recording'` |

### Deprecation Announcement Process

1. Announce in `CHANGELOG.md` under "Deprecations" section
2. Add `X-Deprecated-Field` response header for API endpoints that still return deprecated fields
3. Log a warning when deprecated fields are written to or read from
4. Add to `schema_deprecations` table
5. Send email to enterprise API consumers 6 months before removal

---

## 9. Schema Validation & Enforcement

### Alembic Contract Tests

After every migration, run a contract test that verifies the schema matches expected structure:

```python
# tests/test_schema_contract.py
def test_works_table_has_required_columns(db_inspector):
    cols = {c["name"] for c in db_inspector.get_columns("works")}
    required = {"work_id", "tenant_id", "iswc", "work_title", "created_at"}
    assert required.issubset(cols)

def test_no_deprecated_columns_remain_past_removal_version(db_inspector):
    # Reads schema_deprecations table
    # Fails if any column marred 'remove_in <= current_version' still exists
    ...
```

### Pydantic Model Validation

Every entity has a Pydantic model that is the canonical validator. When a new field is added to the DB, the Pydantic model is the first place it is documented:

```python
class WorkV3(WorkV2):
    """XR7 v3 Work schema — adds normalization + cue sheet fields."""
    work_title_normalized: str | None = None
    duration_seconds: int | None = Field(None, ge=0, le=86400)
    cue_sheet_eligible: bool = False
    alternate_titles: dict[str, list[str]] = {}
```

### JSON Schema Registry

All public API schemas are exported as JSON Schema and stored in `openapi/schemas/v<N>/`. CI validates that the committed schemas match the running application:

```bash
python -c "
from XR7.api.app import app
import json
schemas = app.openapi()['components']['schemas']
with open('openapi/schemas/v3/schemas.json', 'w') as f:
    json.dump(schemas, f, indent=2)
"
```

---

## 10. Data Model Governance Guide

### Who Owns Schema Changes

| Change type | Owner | Approvers needed |
|-------------|-------|-----------------|
| Add nullable column, no default | Feature team | Senior engineer + tech lead |
| Add NOT NULL column | Feature team | Senior engineer + tech lead + DBA |
| Add new table | Feature team | Architecture review (3 approvers) |
| Rename column / table | Migration lead | Architecture review + all API consumers notified |
| Drop column / table | Migration lead | Architecture review + 6-month deprecation period verified |
| Change column type | DBA | Architecture review + DBA |
| Add index | Feature team | DBA review |
| Change foreign key | Feature team | Architecture review |

### The Schema Council

For XR7 v3+, form a **Schema Council** meeting bi-weekly:
- Technical Lead (chair)
- Senior engineer per domain
- DBA / data engineer
- Product representative

The Schema Council reviews all non-additive schema changes before they enter any sprint.

### Golden Rules

1. **The Pydantic model is the contract.** If it's not in the model, it doesn't exist.
2. **ISRC is immutable.** Once an ISRC is assigned to a recording, it never changes.
3. **tenant_id travels everywhere.** Every table has a `tenant_id` column. No exceptions.
4. **Monetary values are `NUMERIC(14,4)`.** Never `FLOAT`. Never `DOUBLE`. Money is exact.
5. **Timestamps are `TIMESTAMPTZ` (UTC stored).** Never local time. Never naive datetime.
6. **UUIDs for PKs.** Never auto-increment integers in multi-tenant, multi-region schemas.
7. **JSONB for flexibility, not avoidance.** JSONB columns must have a documented schema even if enforced in application code.

---

## 11. Schema Change Approval Checklist

Use this checklist for every schema change PR before merging:

### Additive Changes (new nullable column, new table)

- [ ] Pydantic model updated to reflect the new field
- [ ] Alembic migration uses `ADD COLUMN IF NOT EXISTS` pattern
- [ ] New column has an appropriate default or is nullable
- [ ] Index added for any foreign key or commonly-queried filter column
- [ ] Contract test updated in `tests/test_schema_contract.py`
- [ ] `openapi/openapi.json` regenerated
- [ ] CHANGELOG.md entry under "Added"

### Non-Additive Changes (NOT NULL, type change, rename)

All of the above, plus:

- [ ] Expand phase migration deployed and verified in staging for ≥ 1 week
- [ ] Backfill script written, tested, and run on staging
- [ ] Zero-downtime strategy documented
- [ ] Rollback procedure tested
- [ ] Schema Council approval recorded (GitHub PR approval from ≥ 3 council members)
- [ ] API consumers notified (if response shape changes)
- [ ] `schema_deprecations` table updated
- [ ] Removal version set and communicated

### Destructive Changes (drop column, drop table)

All of the above, plus:

- [ ] Deprecation period has elapsed (≥ 6 months / 2 major versions)
- [ ] All code references to the column have been removed and verified via grep
- [ ] All API response models no longer include the field
- [ ] All test fixtures updated
- [ ] DBA sign-off on physical removal
- [ ] Monitoring confirms zero reads/writes to column for ≥ 30 days (from DB access logs)

---

## 12. Safe Migration Playbook

### Pre-Migration Checklist

- [ ] Migration tested on a production-size data snapshot (not just toy data)
- [ ] Migration runtime measured — flag for off-hours if > 5 minutes on production size
- [ ] Lock assessment: does the migration acquire an `ACCESS EXCLUSIVE` lock? If yes, plan for lock timeout + retry
- [ ] Staging deployment passes all tests
- [ ] Monitoring alerts configured for DB connection pool exhaustion during migration

### Migration Execution Steps

```bash
# 1. Take a snapshot (if destructive migration)
pg_dump $DATABASE_URL | gzip > backup_pre_migration_$(date +%Y%m%d).sql.gz

# 2. Apply migration in a transaction (Alembic default)
alembic upgrade head

# 3. Verify: run contract tests immediately
pytest tests/test_schema_contract.py -v

# 4. Verify: run smoke tests
python scripts/smoke_test.py

# 5. Monitor for 15 minutes:
# - Error rate in Grafana/Datadog
# - DB connection pool saturation
# - p99 query latency for affected tables
```

### Rollback Execution

```bash
# Rollback last migration
alembic downgrade -1

# If data was written during the migration (dangerous):
# 1. Restore from pre-migration snapshot
pg_restore --no-owner -d $DATABASE_URL backup_pre_migration_YYYYMMDD.sql.gz

# 2. Notify users of potential data loss window
# 3. Replay any events from the event bus for the loss window
```

### Large Table Migrations (>10M rows)

For tables with >10M rows, never run `ALTER TABLE` directly:

1. Create a new table with the desired schema
2. Copy rows in batches of 10,000 (background job)
3. Create triggers to keep old + new tables in sync during copy
4. Swap table names atomically (`RENAME TABLE` is fast)
5. Remove old table and triggers

This pattern (pg_repack / ghost table) ensures zero locking regardless of table size.
