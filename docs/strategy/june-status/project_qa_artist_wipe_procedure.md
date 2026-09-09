---
name: project-qa-artist-wipe-procedure
description: Proven procedure to fully reset a single artist on QA (DB + S3 + Supabase) for fresh demo walkthroughs
metadata: 
  node_type: memory
  type: project
  originSessionId: 534fc797-ff47-46c1-9c64-7e8e4000b165
---

Used 3 times in the 2026-05-26 → 2026-05-28 demo prep sessions for David Tolliver. The user repeatedly wants to walk through signup → upload → recovery from scratch; this is the proven reset.

**Scope of a "full artist wipe":**

1. **DB rows** — artist row + every table with an `artist_id` column. ~70 tables exist with that column on the current schema, but only a handful have data for a typical artist (statements, events, payments, anomalies, claims, review_items, artist_identity_matches, terms_acceptances, sometimes ml_calibration_snapshots, notification_preferences, invoices).
2. **S3 objects** — everything under `s3://xr7-artifacts/statements/<artist_id>/` (MinIO on QA).
3. **Supabase Auth user** — Jason deletes this manually via the Supabase console. Without this, the email can't be re-used for fresh signup.

**Recipe:**

```bash
# 1. Get the artist_id
ssh root@178.156.210.206 'docker exec artistos-db-1 psql -U xr7 -d xr7 \
  -c "SELECT id, name, email FROM artists WHERE name ILIKE '\''%<name>%'\''"'

# 2. Enumerate every table with artist_id (re-derive if schema has drifted):
#    SELECT table_name FROM information_schema.columns
#    WHERE column_name = 'artist_id' AND table_schema = 'public';

# 3. Build a single-transaction SQL script (the saved one lives at
#    /tmp/wipe-david.sql on Jason's laptop, but /tmp is ephemeral —
#    re-derive from the FK enumeration query if it's gone).
#    Order matters: children of claims/anomalies/review_items/
#    artist_identity_matches/xr7_royalty_statements first, parents
#    after, artist row last. ON_ERROR_STOP + BEGIN/COMMIT ensure
#    atomicity if anything is missed.

# 4. Apply:
scp /tmp/wipe-david.sql root@178.156.210.206:/tmp/wipe-david.sql
ssh root@178.156.210.206 'docker cp /tmp/wipe-david.sql artistos-db-1:/tmp/ && \
  docker exec artistos-db-1 psql -U xr7 -d xr7 -f /tmp/wipe-david.sql'

# 5. S3:
ssh root@178.156.210.206 'docker exec artistos-minio-1 sh -c \
  "mc alias set local http://localhost:9000 \$MINIO_ROOT_USER \$MINIO_ROOT_PASSWORD && \
   mc rm --recursive --force local/xr7-artifacts/statements/<artist_id>/"'

# 6. Tell Jason to delete the Supabase Auth user.
```

**FK gotchas to watch for (caught us mid-session):**

- `artist_identity_match_audits` references `artist_identity_matches` — must delete audits first.
- `xr7_royalty_statement_lines` references `xr7_royalty_statements` — must delete lines first.
- `review_decisions` and `review_assignments` reference `review_items` — both before review_items.
- Most other tables have plain `artist_id` FKs (no children pointing at them) so order among them doesn't matter.

**Why:** Jason has done this 3 times this session for demo prep. The pattern will keep coming up because closed-beta demos benefit from a clean canvas; we don't have a "demo reset" button in /ops yet.

**How to apply:**
- When Jason asks to "reset" or "wipe" an artist, this is the procedure — don't ad-hoc DELETE.
- Always preserve OTHER artists. Scope every query to the specific artist_id; never use unscoped DELETE.
- Confirm scope with Jason before running (he tends to want "full wipe including Supabase user" but Supabase part is his to do).
- A future ops feature ("/ops > admin wipe artist with confirm") would replace this — file when there's time, but the manual procedure works.
