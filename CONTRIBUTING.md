# Contributing

## Workflow

1. **Pick up a task** — find an issue assigned to you on the [Project board](https://github.com/orgs/k6-labs-hq/projects), or self-assign one from the backlog.
2. **Move it to "In Progress"** on the Project board.
3. **Create a branch** from `main`:
   ```bash
   git checkout main && git pull
   git checkout -b <type>/<short-description>   # e.g. fix/claims-state-bug
   ```
4. **Keep PRs scoped to one issue.** A PR should address a single issue or task. If you discover adjacent work while coding, open a separate issue and PR for it. This keeps reviews fast, reverts safe, and the audit trail clean.
5. **Commit** using conventional messages (`fix:`, `feat:`, `chore:`, `docs:`, `refactor:`, `test:`). Write a short subject line that explains *what changed*, not just a number or WIP label.
   ```
   feat(dashboard): add payer health score card
   fix(auth): validate JWT secret on startup
   ```
6. **Open a PR** targeting `main`. The PR template requires:
   - A linked issue (`Closes #123`) — this auto-updates the project board
   - A summary of what changed and why
   - How you tested it
7. **Wait for review** — a CODEOWNER review is required before merge.
8. **Merge** once approved and CI is green. The merge closes the linked issue automatically.

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

### Frontend

- Write components as `.tsx` files. **Do not commit compiled `.js` files** alongside `.tsx` source — they shadow the real code during dev and cause stale builds. If you see `.js` files next to `.tsx` in `frontend/src/`, those are legacy artifacts being cleaned up (see issue #5).
- Tests go in `.test.tsx` files (not `.test.js`).
- Use `npm run dev` on Node 22+ to verify your changes render correctly before pushing.

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
- Do not commit compiled `.js` alongside `.tsx` source files
