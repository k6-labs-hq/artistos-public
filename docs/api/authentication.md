# Authentication & Authorization

Base path: `/auth`
Tags: `auth`, `forensic-api`

---

## Endpoints

### `GET /auth/providers`

Returns the list of configured OAuth providers (Spotify, Apple Music, SoundCloud, etc.) available for DSP account linking.

**Auth:** None
**Response 200** — `ProvidersResponse`:
```json
{
  "providers": [
    { "id": "spotify",     "label": "Spotify",      "enabled": true },
    { "id": "apple_music", "label": "Apple Music",   "enabled": true },
    { "id": "soundcloud",  "label": "SoundCloud",    "enabled": false }
  ]
}
```

---

### `POST /auth/connect/{provider}`

Initiates an OAuth2 authorization code flow for the specified DSP provider. Returns a redirect URL to the provider's OAuth consent screen.

**Auth:** None
**Path params:** `provider` (string) — provider ID from `/auth/providers`

**Request body:**
```json
{ "redirect_uri": "https://app.xr7.artistos.io/oauth/callback", "state": "opaque" }
```

| Code | Description |
|------|-------------|
| 200 | OAuth redirect URL |
| 422 | Invalid provider or redirect_uri |

---

### `POST /auth/login/artist`

Authenticates an artist. Returns a signed JWT for use as `Authorization: Bearer <token>`.

**Auth:** None
**Request body** — `ArtistLoginRequest`:
```json
{ "email": "artist@example.com", "password": "••••••••", "mfa_code": "123456" }
```

**Response 200** — `TokenResponse`:
```json
{
  "access_token":  "eyJ...",
  "refresh_token": "eyJ...",
  "token_type":    "bearer",
  "expires_in":    86400,
  "role":          "artist",
  "tenant_id":     "t_abc123"
}
```

| Code | Description |
|------|-------------|
| 200 | JWT issued |
| 401 | Invalid credentials |
| 422 | Missing required fields |

---

### `POST /auth/login/admin`

Authenticates an internal admin. Tokens expire after 8 hours.

**Auth:** None
**Request body** — `AdminLoginRequest`:
```json
{ "email": "admin@artistos.io", "password": "••••••••" }
```

| Code | Description |
|------|-------------|
| 200 | Admin JWT issued |
| 401 | Invalid credentials |

---

### `GET /auth/me`

Returns the authenticated user profile.

**Auth:** Bearer
**Response 200:**
```json
{
  "user_id":        "usr_abc123",
  "email":          "artist@example.com",
  "role":           "artist",
  "tenant_id":      "t_abc123",
  "permissions":    ["earnings:read", "claims:write"],
  "dsp_connections": ["spotify", "apple_music"]
}
```

---

## JWT Claims Structure

```json
{
  "sub":        "usr_abc123",
  "role":       "artist",
  "tenant_id":  "t_abc123",
  "permissions": ["earnings:read"],
  "iat": 1700000000,
  "exp": 1700086400
}
```

## Token Lifetimes

| Role | Access token | Refresh token |
|------|-------------|---------------|
| `artist` | 24 hours | 30 days |
| `admin` | 8 hours | 24 hours |
| `manager` | 24 hours | 30 days |
| `analyst` | 24 hours | 7 days |

## Security Notes

- Tokens are RS256-signed in production; secret rotated every 90 days.
- `tenant_id` drives row-level security in all multi-tenant queries.
- Rotate API keys regularly; store only in environment variables or secrets managers.
- Enable immutable ledger logging for all privileged actions.
- Webhook endpoints (Trolley) require `X-Webhook-Signature` validation.

## Header Patterns

| Header | Used by |
|--------|---------|
| `Authorization: Bearer <token>` | All authenticated endpoints |
| `X-Admin-Key` | Admin console endpoints |
| `X-Analyst-Id` | Review queue workflows |
| `X-Team-Id` | Artist collaboration routes |
