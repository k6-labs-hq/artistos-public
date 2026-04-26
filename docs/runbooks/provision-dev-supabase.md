# Provision the shared dev Supabase project (artistos-dev)

End-to-end CLI runbook for #145. You'll do one web step (generate a personal
access token), everything else is shell.

## What you're building

A shared Supabase project the team uses for local auth testing. App data
(artists, works, claims) stays in each dev's local Postgres; Supabase only
handles login. Two values — URL and anon key — plus one seeded test user
(`nova@example.com`), distributed via the team vault.

**Signing mode:** ES256 via JWKS. Supabase projects created from ~2026
onward sign tokens with asymmetric keys and publish the public key at
`{SUPABASE_URL}/auth/v1/.well-known/jwks.json`. The XR7 backend
(`XR7/auth/supabase.py`) fetches that JWKS automatically — no shared
`SUPABASE_JWT_SECRET` env var is needed for new projects. For older
projects still using HS256, the backend falls back to the shared secret
if `SUPABASE_JWT_SECRET` is set.

## 0. One-time prereqs

```bash
# Install the Supabase CLI (macOS via brew, Linux/Windows via curl per docs)
brew install supabase/tap/supabase   # macOS
# or: https://supabase.com/docs/guides/cli/getting-started

# Generate a personal access token (WEB STEP — unavoidable)
#   https://supabase.com/dashboard/account/tokens
#   Name: "artistos-cli"  Scope: default
# Paste the token into your shell env (do NOT commit):
export SUPABASE_ACCESS_TOKEN="sbp_..."
```

## 1. Create the project

```bash
# Find your org id
supabase orgs list
# → note the id for k6-labs (or whichever org owns artistos)
export ORG_ID="<paste>"

# Pick a DB password (save it — you'll need it for SQL access)
export DB_PASS="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
echo "DB password: $DB_PASS"   # copy into vault now

# Create the project in us-east-1 (match Supabase/Hetzner region)
supabase projects create artistos-dev \
  --org-id "$ORG_ID" \
  --db-password "$DB_PASS" \
  --region us-east-1
# → note the project ref from the output (looks like: abcdefghijklmno)
export PROJECT_REF="<paste>"
```

Provisioning takes ~2 minutes. Confirm ready:
```bash
supabase projects list | grep artistos-dev
```

## 2. Fetch the three creds

```bash
# URL (derivable from ref)
export SUPABASE_URL="https://${PROJECT_REF}.supabase.co"
echo "SUPABASE_URL=$SUPABASE_URL"

# Anon (public) key — legacy HS256
export SUPABASE_ANON_KEY="$(curl -sS \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/${PROJECT_REF}/api-keys" \
  | python3 -c 'import json,sys; k=json.load(sys.stdin); print(next(x["api_key"] for x in k if x["name"]=="anon"))')"
echo "SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:0:20}..."

# Service role key — admin, used for seeding. NEVER ship to frontend.
export SUPABASE_SERVICE_ROLE_KEY="$(curl -sS \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/${PROJECT_REF}/api-keys" \
  | python3 -c 'import json,sys; k=json.load(sys.stdin); print(next(x["api_key"] for x in k if x["name"]=="service_role"))')"

# Sanity: verify the JWKS endpoint is reachable (used by the backend for verification)
curl -sS "${SUPABASE_URL}/auth/v1/.well-known/jwks.json" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print("JWKS keys:", len(d["keys"]), "algs:", [k["alg"] for k in d["keys"]])'
# Expect: "JWKS keys: 1 algs: ['ES256']"  (or similar)
```

**Note on JWT secret:** new Supabase projects use ES256 signing keys and do
not expose a shared HS256 secret via the Management API. If you're
provisioning a legacy project that still uses HS256, also grab:

```bash
export SUPABASE_JWT_SECRET="$(curl -sS \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/${PROJECT_REF}/config/auth" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin).get("jwt_secret") or "")')"
```
An empty value here confirms the project is ES256-only — no action needed,
the backend uses JWKS.

## 3. Save to the team vault

Store under a single entry named **`artistos-dev Supabase`** with these fields:

| Field | Value | Audience |
|---|---|---|
| `SUPABASE_URL` | `$SUPABASE_URL` | team |
| `SUPABASE_ANON_KEY` | `$SUPABASE_ANON_KEY` | team |
| `SUPABASE_JWT_SECRET` | `$SUPABASE_JWT_SECRET` *(if present; often empty for 2026+ projects)* | team |
| Signing mode | ES256 via JWKS (or HS256 if legacy) | team |
| `SUPABASE_SERVICE_ROLE_KEY` | `$SUPABASE_SERVICE_ROLE_KEY` | admins only |
| `DB password` | `$DB_PASS` | admins only |
| `Project ref` | `$PROJECT_REF` | admins only |
| Test user | `nova@example.com` / password seeded in step 5 | team |

Service role key, DB password, and project ref are admin-only (per
`docs/decisions/access-policy.md` — offshore devs get URL + anon key
only). Do **not** put the service role key in anyone's local `.env`.

## 4. Populate your local `.env` files

Backend:
```bash
cat >> .env <<EOF
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
# SUPABASE_JWT_SECRET — only needed if project uses HS256; leave unset for ES256/JWKS projects
EOF
```

Frontend:
```bash
cat >> frontend/.env <<EOF
VITE_SUPABASE_URL=$SUPABASE_URL
VITE_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
EOF
```

Confirm `.env` and `frontend/.env` are both gitignored (they are per
repo config — verify with `git check-ignore .env frontend/.env`).

## 5. Seed the shared test user

```bash
# Pick a password for nova — store it in the vault entry from step 3
export NOVA_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')"
echo "nova@example.com password: $NOVA_PASSWORD"

# Create the user via admin API (auto-confirms email so login just works)
curl -sS -X POST "${SUPABASE_URL}/auth/v1/admin/users" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"nova@example.com\",
    \"password\": \"$NOVA_PASSWORD\",
    \"email_confirm\": true,
    \"user_metadata\": {\"artist_name\": \"Nova (test artist)\"}
  }" | python3 -m json.tool
```

Expected: JSON response with `"id": "<uuid>"`. Add the password to the vault
entry — this is the password testers will use.

## 6. Verify end-to-end

Backend verification (from the repo root, with the updated `.env`):
```bash
# Sign in as nova → get a Supabase access token
SUPABASE_ACCESS=$(curl -sS -X POST "${SUPABASE_URL}/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"nova@example.com\",\"password\":\"$NOVA_PASSWORD\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

# Make sure the API is running locally (in another terminal)
#   PYTHONPATH=. uvicorn XR7.api.app:app --reload

# Exchange for an XR7 JWT
curl -sS -X POST http://localhost:8000/auth/supabase/exchange \
  -H "Authorization: Bearer $SUPABASE_ACCESS" | python3 -m json.tool
# → expect: {"access_token": "eyJ..."}
```

Frontend verification:
```bash
cd frontend && npm run dev
# Visit http://localhost:5173/login
# Sign in with nova@example.com / <the password>
# → should redirect to / with localStorage.xr7_access_token populated
```

## 7. Distribute

Post the Discord draft at `/tmp/discord-draft.md` (or wherever you saved
it) so the team pulls the vault entry and updates their `.env`. Everyone's
local backend data stays on their laptop; only the auth login round-trips
to Supabase.

## 8. Idempotency / re-running

- Re-running step 2 is safe — it just re-reads creds.
- `supabase projects create` fails cleanly if the project already exists.
- Re-running the admin user POST returns HTTP 422 if the email is taken —
  that's fine.

## Troubleshooting

**`supabase orgs list` returns nothing** — the personal access token was
scoped to the wrong account. Regenerate at
https://supabase.com/dashboard/account/tokens.

**`/auth/supabase/exchange` returns 401 "invalid JWT"** — either:
1. The token was signed by a different project than `SUPABASE_URL` points at.
2. The backend can't reach the project's JWKS endpoint from its network.
3. (HS256 legacy only) The `SUPABASE_JWT_SECRET` in `.env` doesn't match.

Diagnose:
```bash
# Confirm token header and issuer
python3 -c "
import jwt, json
t = '$SUPABASE_ACCESS'
h = jwt.get_unverified_header(t)
c = jwt.decode(t, options={'verify_signature': False})
print('header:', h)
print('iss:', c.get('iss'))
"

# Confirm backend can fetch JWKS
curl -sS "$SUPABASE_URL/auth/v1/.well-known/jwks.json" | python3 -m json.tool
```

**Project uses ES256 by default (JWKS-only)** — expected for 2026+ projects.
The backend at `XR7/auth/supabase.py` handles both ES256 (via JWKS) and
HS256 (via shared secret) automatically; no action needed.

## References

- Access policy: [`docs/decisions/access-policy.md`](../decisions/access-policy.md)
- Backend Supabase verifier: [`XR7/auth/supabase.py`](../../XR7/auth/supabase.py)
- Frontend Supabase client: [`frontend/src/lib/supabase.ts`](../../frontend/src/lib/supabase.ts)
- Related issues: #145 (provisioning), #124 (frontend login), #99 (identity-provider decision)
