# XR7 Naming Convention Standard & Audit

## Purpose
This document defines the authoritative naming standard for the XR7 codebase, documents all identified violations, and classifies each violation by action required.

---

## 1. Naming Standard

### Domain Entity Names

| Concept | **Canonical Term** | Do Not Use |
|---|---|---|
| Musical composition (lyrics + melody) | `work` | `song`, `composition` |
| Specific performed recording of a work | `recording` | `track` (in new code) |
| Legal entity with ownership stake | `party` | `writer`, `composer`, `songwriter` (in new code) |
| Payment from a DSP/PRO/distributor | `statement` | `report`, `payment_statement` |
| Detected royalty discrepancy | `anomaly` | `issue`, `problem`, `discrepancy` |
| Recovery action against payer | `claim` | `dispute`, `case` |
| Supporting proof bundle | `evidence_packet` | `proof_bundle`, `evidence_doc` |

### Field-Name Convention

| Field | **Canonical Name** | Do Not Use |
|---|---|---|
| Composition identifier | `work_id` | `song_id`, `composition_id` |
| Composition title | `work_title` | `song_title`, `track_title` |
| Number of compositions | `work_count` | `song_count`, `track_count` |
| Recording identifier (internal) | `recording_id` | `track_id` (in new ORM columns) |
| Entity type discriminator | `"entity": "recording"` | `"entity": "track"` |
| Rights holder identifier | `party_id` | `writer_id` (in new code) |

### File/Module Naming

| Layer | Convention | Example |
|---|---|---|
| Python modules | `snake_case.py` | `metadata_repair_engine.py` |
| Test files | `test_<domain>_<module>.py` | `test_core_claims_state_machine.py` |
| Classes | `PascalCase` | `MetadataRepairEngine` |
| Public functions | `snake_case()` | `compute_identity_match()` |
| Constants | `UPPER_SNAKE_CASE` | `EXPECTED_PAYOUT_UPLIFT` |
| Private helpers | `_snake_case()` | `_band_for_score()` |

---

## 2. Full Violation Audit

### Legend
- ✅ **Fixed** — corrected in a previous session
- 🔄 **Requires DB Migration** — ORM column or stored DB value; change needs an Alembic migration
- 🔌 **External Vendor Term** — originates from a third-party API; must use vendor terminology to match their data
- 📁 **Parser Column Alias** — used to match DSP-provided CSV headers; must remain as-is for parsing

---

### Category A: Fixed in Previous Sessions ✅

| File | Old Term | New Term | Status |
|---|---|---|---|
| Multiple files | `track_title` | `work_title` | ✅ Fixed |
| Multiple files | `track_count` | `work_count` | ✅ Fixed |
| Multiple files | `"entity": "track"` | `"entity": "recording"` | ✅ Fixed |
| `utils/*.py` | Duplicate `_safe_float` (×5) | consolidated to `shared/utils/numbers.py` | ✅ Fixed |
| `utils/*.py` | Duplicate `_ensure_utc` (×7) | consolidated to `shared/utils/dates.py` | ✅ Fixed |
| `services/statement_signal_extractor.py` | path in `services/` | moved to `ingestion/` | ✅ Fixed |
| `services/identity_matching.py` | path in `services/` | moved to `fingerprinting/matching/` | ✅ Fixed |
| `services/gap_explainer_service.py` | path in `services/` | moved to `recovery/gap_explainer.py` | ✅ Fixed |
| `services/modules.py` | thin proxy | deleted | ✅ Fixed |
| `ml/anomaly_detector.py` | deleted (regression) | restored from git | ✅ Fixed |
| `universal_schema.py` | private `utc_now()` | removed, use `shared/utils/dates.py` | ✅ Fixed |
| `IngestionConnector` | duplicate `@abstractmethod` | deduplicated | ✅ Fixed |

---

### Category B: Requires Alembic Migration 🔄

These violations exist in ORM models or as stored database string values. **Do not change these without a migration.** A migration script must be created and reviewed before renaming.

| File | Violation | Correct Term | Migration Required |
|---|---|---|---|
| `XR7/models/xr7_royalty.py:41` | `__tablename__ = "xr7_tracks"` | `"xr7_recordings"` | `ALTER TABLE xr7_tracks RENAME TO xr7_recordings` |
| `XR7/models/xr7_royalty.py:95,120` | `track_id` (FK to `xr7_tracks.id`) | `recording_id` | Rename column + FK |
| `XR7/models/fingerprint_match.py:28` | `track_id: Mapped[str | None]` | `recording_id` | Rename column |
| `XR7/models/invite.py:37` | `InviteRole.WRITER = "writer"` | `InviteRole.PARTY = "party"` | UPDATE all stored values |
| `XR7/services/catalog_graph_adjacency.py:16` | `"Writer"` node type in graph | `"Party"` | UPDATE stored `node_type` values |
| `XR7/services/catalog_graph_adjacency.py:159-161` | `writer_id = f"writer:..."` | `party_id = f"party:..."` | Depends on graph migration above |

**To execute these changes:**
1. Create a new Alembic migration: `alembic revision --autogenerate -m "rename_tracks_to_recordings_and_writer_to_party"`
2. Write explicit `op.rename_table`, `op.alter_column` calls
3. Add a data migration step to update stored string values (`UPDATE catalog_graph_nodes SET node_type='Party' WHERE node_type='Writer'`)
4. Test against a staging database before running on production

---

### Category C: External Vendor Terms (Do Not Rename) 🔌

These `track_id` usages come directly from external fingerprinting service APIs. Renaming them would break the vendor-response parsing logic.

| File | Term | Vendor | Reason to Keep |
|---|---|---|---|
| `XR7/fingerprinting/adapters/gracenote.py` | `track_id` | Gracenote | Gracenote API field name |
| `XR7/fingerprinting/adapters/audible_magic.py` | `track_id` | AudibleMagic | AudibleMagic response field |
| `XR7/fingerprinting/adapters/soundmouse.py` | `track_id` | SoundMouse | SoundMouse response field |
| `XR7/fingerprinting/schema.py:69` | `track_id: str | None` | Multiple | Shared fingerprint result schema mirroring vendor APIs |
| `XR7/fingerprinting/orchestrator.py:438` | `track_id=r.track_id` | Multiple | Reading from fingerprint schema |
| `XR7/api/routers/fingerprinting.py:84` | `track_id` response field | Multiple | Public API — breaking change |

---

### Category D: Parser Column Aliases (Do Not Rename) 📁

These `"song"`, `"track"` values are fallback column names used when parsing DSP-provided CSV files. DSPs name their columns inconsistently — these aliases ensure we can read files that use `"song"` as the title column.

| File | Term | Context |
|---|---|---|
| `XR7/ingestion/statement_parser.py` | `"song"` in `_col()` calls | DSP CSV header alias — matches incoming vendor files |
| `XR7/ingestion/statement_signal_extractor.py:129` | `"song"` in column list | DSP CSV header alias |
| `XR7/tasks/blackbox.py` | `"writer_alias_keywords"` | Keyword list for PRO data scanning |
| `XR7/services/tvfilm_vertical.py:56` | `"writer"` in keyword list | TV/Film PRO domain keyword |

---

## 3. Recommended Migration Execution Order

For teams ready to execute the Category B migrations:

```
Sprint N:
  1. alembic revision: rename xr7_tracks → xr7_recordings
  2. alembic revision: rename track_id columns in xr7_royalty + fingerprint_match
  3. alembic revision: update InviteRole.WRITER stored values
  4. alembic revision: update catalog_graph node_type "Writer" → "Party"
  5. Update fingerprinting/schema.py track_id → recording_id
  6. Update api/routers/fingerprinting.py response schema
  7. Version bump the API (v2 endpoint) to avoid breaking clients
```

---

## 4. Going Forward: Pre-Commit Convention Checks

Add the following checks to `.pre-commit-config.yaml` or CI:

```yaml
# Reject new uses of forbidden field names in new code
- repo: local
  hooks:
    - id: naming-conventions
      name: Domain Naming Convention Check
      language: python
      entry: python scripts/check_naming_conventions.py
      files: XR7/.*\.py$
      exclude: |
        (?x)
        XR7/ingestion/statement_parser\.py|
        XR7/fingerprinting/adapters/|
        XR7/tasks/blackbox\.py|
        XR7/models/xr7_royalty\.py|
        XR7/models/fingerprint_match\.py|
        XR7/models/invite\.py
```

Proposed `scripts/check_naming_conventions.py` checks:
- New files must not introduce `track_title`, `track_count`, or `song_id` as variable/field names
- New files must not create `entity: "track"` string literals
- New core/ files must not contain `sqlalchemy` or `SessionLocal` imports
