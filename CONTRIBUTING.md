# Contributing

`main` is the source of truth. All work goes through pull requests. Do not push directly to `main`.

## Workflow

**1. Pick a task**
- Open the [Project board](https://github.com/orgs/k6-labs-hq/projects/1).
- Either work an item already **Assigned** to you, OR grab one from **Backlog**.
- If grabbing from Backlog: add yourself as assignee on the issue.
- Move the card to **In Progress**.

**2. Branch from main**
```bash
git checkout main
git pull
git checkout -b <type>/<short-description>
# types: feat, fix, chore, docs, refactor, test
# example: feat/idempotency-middleware
```

**3. Work the task**
- Keep PRs scoped to one issue. Don't bundle unrelated work.
- Commit with conventional messages that reference the issue:
  ```
  feat(api): add idempotency middleware (#44)
  fix(auth): reject malformed tokens
  ```
- Pre-commit hooks auto-run black + ruff before each commit. After cloning, run `pre-commit install` once.
- Push your branch early — draft PRs are fine and encouraged.

**4. Open a PR**
- **Base**: `main`.
- PR title: same conventional format as commits.
- PR description **must** include `Closes #N` where N is the issue number — this auto-closes the issue and links the project card.
- Move the card to **In Review**.

**5. Get reviewed**
- Request a reviewer (another team member). **Don't approve your own PR.**
- CI must be green.
- If changes are requested, push more commits. The card stays in **In Review**.

**6. Merge**
- **The reviewer merges the PR, not the author.**
- Use "Squash and merge" for a clean history.
- The linked issue auto-closes → card auto-moves to **Done**.
- Delete the branch after merge.

## Key rules

- ❌ Never commit directly to `main`
- ❌ Never merge your own PR
- ❌ One PR = one issue — don't bundle multiple tasks
- ❌ No compiled artifacts (`.js` files alongside `.tsx` sources)
- ✅ Small PRs, reviewed fast, merged often
- ✅ Use `Closes #N` in every PR description
- ✅ Move cards through columns as you work

## Branch naming

- `feat/<desc>` — new feature
- `fix/<desc>` — bug fix
- `chore/<desc>` — maintenance, deps, tooling
- `docs/<desc>` — docs only
- `refactor/<desc>` — internal cleanup, no behavior change

## Local setup

See [README.md § Dev Workflow](README.md#5-dev-workflow). Short version:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
podman-compose up -d postgres redis minio   # or docker compose
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. uvicorn XR7.api.app:app --reload
```

Frontend requires Node 22+:
```bash
cd frontend && npm install && npm run dev
```

### Dev Supabase (shared project for auth testing)

Auth goes through Supabase in every environment, including local. All devs share a single **`artistos-dev`** Supabase project for convenience. Your app data (artists, works, claims, events) stays in your local Postgres container — Supabase is *only* for authentication.

**Get your credentials** from the engineering lead (see the `#dev` channel). You need two values:

- `SUPABASE_URL` — shared across all devs
- `SUPABASE_ANON_KEY` — shared, safe to have in a dev `.env`

Drop them into your local `.env`:

```bash
SUPABASE_URL=https://<dev-project>.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_JWT_AUDIENCE=authenticated
```

The frontend `.env` needs the same URL + anon key with `VITE_` prefix:

```bash
VITE_SUPABASE_URL=https://<dev-project>.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

A shared **test user** (`nova@example.com`) is seeded in the dev project so you can log in immediately without creating your own. Passwords are in the team password manager.

The API verifies Supabase-issued JWTs by fetching the project's public signing key from `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` (ES256). No shared JWT secret is needed for new projects. Legacy HS256 projects can still set `SUPABASE_JWT_SECRET` and the backend will fall back to it. For full flow testing, the frontend (`npm run dev`) and the API (`uvicorn ...`) both need to be running.

## Code standards

- Python 3.12 · FastAPI · SQLAlchemy 2.0 · Pydantic v2
- Run `make check` before pushing (naming + domain boundary checks)
- Run `make test` — don't break existing passing tests

## Daily check-in

Leave a comment on the issue you're working on each day:

```
### YYYY-MM-DD
- Done: ...
- Next: ...
- Blocked: ... (or "none")
```

## Secret Management

**CRITICAL:** Never commit secrets to version control.

### Development Setup

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your local credentials:**
   - Use the provided dev defaults (minioadmin, dev JWT secret, etc.)
   - For local development, these insecure defaults are acceptable
   - `.env` is in `.gitignore` and will not be committed

3. **Generate secure secrets for shared environments:**
   ```bash
   # JWT secret (production)
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"

   # Widget admin key (production)
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

### What Goes Where

| File | Purpose | Committed | Contains |
|------|---------|-----------|----------|
| `.env.example` | Template with placeholder values | ✅ Yes | Safe placeholders only |
| `.env` | Your actual local secrets | ❌ **NEVER** | Real credentials |
| `infrastructure/secrets/runtime.env` | Production secrets (Terraform managed) | ❌ **NEVER** | Real credentials |

### Production Secret Validation

When `XR7_ENV=production`, the application validates required secrets at startup:

**Required in Production:**
- `XR7_JWT_SECRET` — must not be dev default (`change-me-in-production`)
- `DATABASE_URL` — must be PostgreSQL (not SQLite)
- `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` — must not be `minioadmin`
- `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` — required for email
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_FROM_NUMBER` — required for SMS
- `WIDGET_ALLOWED_ORIGINS` — must not be `*` (wildcard)

If validation fails, the app exits with error details before accepting requests.

### Common Mistakes to Avoid

❌ **Don't do this:**
```bash
git add .env                    # NEVER commit .env
git commit -m "Add my config"   # Contains real secrets!
```

❌ **Don't do this:**
```python
# In code
DATABASE_URL = "postgresql://user:password@..."  # Hardcoded secret!
```

✅ **Do this instead:**
```python
# In code
from xr7_common.settings import settings
db_url = settings.database_url  # Reads from environment
```

✅ **Do this instead:**
```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@..."
```

### If You Accidentally Commit a Secret

1. **Rotate the secret immediately** (generate new value, update in deployment)
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Notify the team** in #engineering Slack
4. **Document in postmortem** what happened and how to prevent recurrence

### Getting Shared Secrets

For staging/production deployments:
- Secrets are managed in 1Password (Engineering vault)
- Terraform applies them via `infrastructure/secrets/runtime.env`
- Ask `@jtrent-k6` for access if deploying to shared environments

## Getting help

- Tag `@jtrent-k6` in an issue comment for unblocking
- Do not merge your own PRs
- Do not force-push to `main`
- Do not commit `.env` or any secret
