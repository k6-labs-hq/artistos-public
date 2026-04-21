# 06 — Identity & Auth

> **Status: TARGET with legacy fallback in production code today.** Provider decided in [#99](https://github.com/k6-labs-hq/ArtistOS/issues/99) (Supabase Auth). Implementation pending [#100](https://github.com/k6-labs-hq/ArtistOS/issues/100) (artist) and [#101](https://github.com/k6-labs-hq/ArtistOS/issues/101) (admin).

## TL;DR

- **Target provider:** Supabase Auth (managed SaaS).
- **Environments:** separate Supabase cloud projects for **dev**, **staging**, **prod** — no local Supabase containers.
- **Integration shape:** Supabase issues JWTs; FastAPI validates them and maps claims to roles. Existing `jwt_service` becomes a JWT-verification shim rather than an issuer.
- **Current code is unsafe for production.** Artist login accepts any `artist_id` with no password. Admin login uses a shared env-var credential. Both are gated off before pilot.

## Why Supabase (not local / not Cognito / not roll-your-own)

Recorded in [#99](https://github.com/k6-labs-hq/ArtistOS/issues/99). Short version:

- We're already on Postgres — Supabase is Postgres-native.
- Free tier (50k MAU) covers MVP + early pilot.
- Email+password, magic link, OAuth, MFA all out of the box.
- Migration path is cheap — if we outgrow Supabase later, only the JWT issuer changes; our validation layer stays.

We did **not** pick AWS Cognito (dev UX is rougher) or Auth0/Clerk (overkill at MVP) or roll-our-own (no).

## Environments — no local containers

Supabase has a local-dev mode (`supabase start` → Docker stack). We are **not** using it, because:

- Parity matters. Email templates, OAuth provider configs, and redirect URLs only behave identically against hosted Supabase. A local stack diverges.
- The team runs Podman and one dev is on Windows. Local Supabase adds Docker-socket/Podman-compat friction we don't need.
- The existing dev stack ([02-containers](02-containers.md)) is already running Postgres/Redis/MinIO via Compose. Local Supabase would either duplicate or replace that Postgres — both are bad.
- Auth schema doesn't iterate the way app schema does. Hosted dev is fine.

Setup:

| Env | Supabase project | Used by |
|---|---|---|
| Local dev | `artistos-dev` (shared) | All developers' local Compose stacks |
| Staging | `artistos-staging` | Staging env in AWS (see [03-deployment](03-deployment.md)) |
| Prod | `artistos-prod` | Production env in AWS |

**Shared dev project tradeoff:** one dev changing a redirect URL or OAuth setting affects everyone. Mitigation: document changes in `#eng` before making them; any dev who needs isolation can spin up their own free project and point their local `.env` at it.

## Target architecture

```mermaid
sequenceDiagram
    actor user as User
    participant fe as Frontend<br/>(React)
    participant sb as Supabase Auth
    participant api as API<br/>(FastAPI)
    participant db as Postgres

    user->>fe: Email + password / magic link / OAuth
    fe->>sb: Sign in
    sb-->>fe: Access JWT + refresh token
    fe->>api: API call + Bearer JWT

    api->>api: Verify JWT (signature via Supabase JWKS,<br/>iss/aud/exp/sub claims)
    api->>api: Map JWT claims → role (artist / admin / analyst / exec / legal)
    api->>db: Query scoped by tenant_id + role
    api-->>fe: Response

    Note over fe,sb: Refresh flow handled entirely<br/>between frontend and Supabase;<br/>API never sees the refresh token.
```

## Role model

Existing role claims in [`XR7/api/routers/auth.py`](../../XR7/api/routers/auth.py) stay the same:

- `artist` — default
- `analyst` — internal review queue
- `admin` — tenant/ops management
- `exec` / `executive` / `ceo` / `cfo` — read-only portfolio views
- `legal` — attorney review

Supabase stores these in `user_metadata` (self-service) or `app_metadata` (server-set, privileged). **We use `app_metadata`** so roles cannot be self-granted. Admin-invitation flows write `app_metadata` via the Supabase service key.

## JWT mapping

Supabase's access JWT → FastAPI claim shape:

| Supabase claim | FastAPI use |
|---|---|
| `sub` | Stable user ID; stored on `artists.auth_provider_id` |
| `email` | User-visible identifier |
| `app_metadata.role` | Drives `require_admin` / `require_analyst` / etc. |
| `app_metadata.tenant_id` | Multi-tenancy boundary — enforced in every query |
| `aud` | Must equal `authenticated` (Supabase default) or a project-scoped value we set |
| `iss` | Must match the Supabase project URL |

The existing [`XR7/auth/jwt_service.py`](../../XR7/auth/jwt_service.py) is the only file that needs structural change: swap local-secret HS256 verification for JWKS-based RS256 verification against Supabase. Everything downstream (`get_auth_payload`, `require_admin`, etc.) keeps working.

## Current (legacy) state

**Artist login** — [`XR7/api/routers/auth.py`](../../XR7/api/routers/auth.py):
- `POST /auth/login/artist` accepts `artist_id` (optional `email`). **No password.** Anyone who knows an artist's ID can log in as them.
- Issues an HS256 JWT signed with `XR7_JWT_SECRET`.

**Admin login** — same router:
- `POST /auth/login/admin` accepts `email` + `password`.
- Checks against `XR7_ADMIN_EMAIL` / `XR7_ADMIN_PASSWORD` env vars. Single shared admin account, no rotation, no per-admin audit identity.

**Both are production-blockers.** The soft-auth flag `XR7_ENFORCE_AUTH_GLOBALLY=0` means many endpoints still serve unauthenticated requests today. Must flip to `1` before any pilot.

## Migration plan

1. **Stand up Supabase projects** (dev, staging, prod).
2. **Add `artists.auth_provider_id`** column (Alembic migration).
3. **Back-fill** existing test artists with Supabase users (one-time admin script).
4. **Add Supabase JWKS verification path** to `jwt_service.py`; feature-flag which verifier is used.
5. **Switch frontend** to Supabase auth SDK; replace the `artist_id`-only login form with email/password + magic link.
6. **Replace admin creds** with Supabase-issued admin accounts ([#101](https://github.com/k6-labs-hq/ArtistOS/issues/101)). Delete `XR7_ADMIN_EMAIL`/`XR7_ADMIN_PASSWORD`.
7. **Flip** `XR7_ENFORCE_AUTH_GLOBALLY=1`.
8. **Delete** the legacy artist-login endpoint.

## Admin audit trail

Every admin action is already audited via `admin_audit_logs`. As part of #101, verify the audit row stores the actor's Supabase user ID — not the string `"admin"`.

## Open decisions

- [ ] Which Supabase plan for prod — free tier covers MVP; upgrade path is a line-item cost
- [ ] MFA policy — optional or required for admin accounts?
- [ ] OAuth providers to enable (Google / Apple at minimum for artist signup?)

## See also

- [#99](https://github.com/k6-labs-hq/ArtistOS/issues/99) — provider decision
- [#100](https://github.com/k6-labs-hq/ArtistOS/issues/100) — artist auth implementation
- [#101](https://github.com/k6-labs-hq/ArtistOS/issues/101) — admin auth implementation
- [`docs/security_hardening_plan.md`](../security_hardening_plan.md) — broader auth/authz strategy
- [08 — Security boundaries](08-security-boundaries.md) — trust zones and data classification
