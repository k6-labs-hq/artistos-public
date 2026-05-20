# Sentry monitoring setup

Code is wired and ships dormant — both backend and frontend init are
**no-ops without a DSN**. Turning monitoring on for an environment is
a config-only step.

## One-time: create the Sentry projects

1. Sign up at <https://sentry.io> (free tier: 5K errors + 10K perf
   txn / month / single user — fine for QA + early prod).
2. Create one **organization** for K6 Labs.
3. Inside the org, create **two projects**:
   - `artistos-api` — platform: **Python / FastAPI**
   - `artistos-frontend` — platform: **JavaScript / React**
4. Copy each project's **DSN** from `Settings → Projects → <name> →
   Client Keys (DSN)`. The DSN looks like
   `https://<key>@oNNNNNN.ingest.us.sentry.io/PPPPPP`. It is not
   secret in the strict sense — it's safe in the frontend bundle —
   but treat the backend one as ops-only.

## Turning it on for QA

### Backend

```bash
ssh root@178.156.210.206
cd /opt/artistos
# Add the two env vars to .env.qa:
#   SENTRY_DSN=<artistos-api DSN>
#   SENTRY_ENVIRONMENT=qa
# (Also: SENTRY_TRACES_SAMPLE_RATE=0.05 is the default; raise if needed.)

# Reload only the api + worker so they pick up the new env.
docker compose -f docker-compose.prod.yml --env-file .env.qa up -d --force-recreate api worker
```

Verify in the api container logs:

```
Sentry: initialised (environment=qa traces_sample_rate=0.05)
```

If you see `SENTRY_DSN unset — error monitoring disabled.` the env
var didn't propagate; the env file isn't getting reloaded (`docker
compose restart` does not pick up env changes — force-recreate does).

### Frontend

Vite bakes env vars at **build time**, so the frontend DSN goes into
the build environment, not the runtime container.

Add to `frontend/.env` (or a per-environment overlay):

```
VITE_SENTRY_DSN=<artistos-frontend DSN>
VITE_SENTRY_ENVIRONMENT=qa
```

…then rebuild and redeploy `frontend-dist` as usual.

To verify it's live: open the QA site, open devtools → Network, look
for a request to `*.ingest.us.sentry.io`. (Sentry sends a session
init on page load even when there are no errors.)

## Free-tier-friendly defaults baked into the init

| Lever | Default | Why |
| --- | --- | --- |
| `errors_sample_rate` | 1.0 (implicit) | errors are rare; catch them all |
| `traces_sample_rate` | 0.05 | 5% of requests sampled; under the 10K/mo perf budget at current volumes |
| `profiles_sample_rate` | 0 | profiling burns the budget fast; off by default |
| Session Replay | off | heavy; opt in deliberately when needed |
| `send_default_pii` | false | no IP/cookies/user-id unless explicitly tagged |

Override via env (backend) or build-time env (frontend) when needed —
e.g. raise `SENTRY_TRACES_SAMPLE_RATE` to 0.2 during an incident.

## Extra PII scrubbing

`XR7.observability.sentry._scrub_sensitive_headers` is registered as
`before_send` and redacts `Authorization`, `Cookie`, and
`X-Admin-Key` from any captured request headers — belt-and-braces on
top of Sentry's own defaults so a future config change can't
accidentally start sending bearer tokens to a third-party service.

## Cost guardrail

The free tier silently rate-limits new events when you hit the
monthly cap. To prevent surprise blackouts:

1. In Sentry → Settings → Subscription, set **Spending caps** to
   block all paid event types (default in free tier, but verify).
2. Add a Slack notification for "monthly volume above 70%" on both
   projects so you have warning before saturation.
