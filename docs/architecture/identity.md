# Identity & Authentication

Decision record and integration guide.

## Decision (MVP)

**Supabase Auth is the MVP identity provider.**

Why Supabase:
- Already on Postgres — shared mental model.
- Email+password, magic link, OAuth (Google, Apple), MFA all work out of the box.
- Free up to 50k MAU — covers MVP pilot and early growth.
- Standard HS256 JWTs — we validate locally with a shared secret, no extra network hop.
- Migration path to Cognito / Auth0 later is a JWT-issuer swap, not a rewrite.

Tracking issue: #99.

## Flow

```
Browser ──(email+password / magic link / OAuth)──▶ Supabase
                                                      │
                                                      ▼
                                            Supabase-signed JWT
                                                      │
Browser ──Authorization: Bearer <supabase-jwt>──▶ XR7 API /auth/supabase/exchange
                                                      │
                                                XR7-signed JWT (maps to Artist)
                                                      │
Browser ──Authorization: Bearer <xr7-jwt>──▶ XR7 API (all other endpoints)
```

## Why the exchange step

Supabase issues tokens keyed on its own `sub` (user UUID). The rest of the XR7 API
expects an `artist_id` claim and XR7-specific role data. `/auth/supabase/exchange`:

1. Validates the Supabase JWT (HS256 + audience + issuer check).
2. Looks up the linked `Artist` record by `artist.supabase_user_id` or falls back to `email`.
3. Issues an XR7 JWT carrying `artist_id`, `role`, `tenant_id`.

Existing endpoints keep working unchanged because they still see a JWT signed
by `XR7_JWT_SECRET` with familiar claims.

## Environment variables

| Variable | Required | Source |
|----------|----------|--------|
| `SUPABASE_URL` | yes | Supabase Settings → API → Project URL |
| `SUPABASE_JWT_SECRET` | yes | Supabase Settings → API → JWT Settings → JWT Secret |
| `SUPABASE_JWT_AUDIENCE` | no | defaults to `authenticated` |
| `SUPABASE_JWT_ISSUER` | no | defaults to `{SUPABASE_URL}/auth/v1` |
| `SUPABASE_ANON_KEY` | frontend | public key for Supabase JS client |
| `SUPABASE_SERVICE_ROLE_KEY` | admin tasks | server-side user mgmt |

## Onboarding (MVP manual flow)

1. Admin creates the Supabase user via Supabase dashboard (or invites by email).
2. Admin creates the `Artist` record in XR7 with the matching email address.
3. First login: user authenticates with Supabase → calls `/auth/supabase/exchange`.
4. XR7 resolves the Artist by email, back-fills `supabase_user_id`.
5. Subsequent logins match directly by `supabase_user_id`.

Auto-provisioning (Supabase user → Artist record on first login) is deferred
until self-serve signup is in scope.

## Code references

- `XR7/auth/supabase.py` — JWT verification + Artist resolution.
- `XR7/api/routers/auth.py` — `/auth/supabase/exchange` endpoint.
- `XR7/models/artist.py` — `supabase_user_id` column.
- `alembic/versions/20260421_0033_add_supabase_user_id_to_artists.py` — schema migration.

## Future work

- **#100** Replace legacy artist_login with Supabase exchange as the only path.
- **#101** Migrate admin credentials out of env vars; use Supabase admin role.
- Auto-provision Artist on first Supabase login (post-MVP, with self-serve).
- Row-level security policies in Postgres if we ever expose Supabase direct to clients.
