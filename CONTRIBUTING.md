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

## Getting help

- Tag `@jtrent-k6` in an issue comment for unblocking
- Do not merge your own PRs
- Do not force-push to `main`
- Do not commit `.env` or any secret
