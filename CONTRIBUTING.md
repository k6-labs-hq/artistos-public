# Contributing

## Workflow

1. **Pick up a task** — find an issue assigned to you on the [Project board](https://github.com/orgs/k6-labs-hq/projects), or self-assign one from the backlog.
2. **Move it to "In Progress"** on the Project board.
3. **Create a branch** from `main`:
   ```bash
   git checkout main && git pull
   git checkout -b <type>/<short-description>   # e.g. fix/claims-state-bug
   ```
4. **Commit** using conventional messages (`fix:`, `feat:`, `chore:`, `docs:`, `refactor:`, `test:`).
5. **Open a PR** targeting `main`. The PR template requires a linked issue (`Closes #123`).
6. **Wait for review** — a CODEOWNER review is required before merge.
7. **Merge** once approved and CI is green. The merge closes the linked issue automatically.

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
