# 05 — Integrations

**Status:** Current. This doc distinguishes what's **implemented in code** from what's **aspirational** — the ingestion surface is generic, so "supports Spotify" usually means "the parser handles Spotify-format CSVs," not "there's a Spotify API client."

## Matrix

| System | Purpose | Direction | Auth method | Data contract | Implementation | Failure mode |
|---|---|---|---|---|---|---|
| **Trolley** | Payouts to artists | Outbound | API key | REST JSON | [`XR7/trolley/client.py`](../../XR7/trolley/client.py), router [`XR7/api/routers/trolley.py`](../../XR7/api/routers/trolley.py) | Claim → `DISBURSEMENT_FAILED`; retry per [`trolley_failure_playbook.md`](../trolley_failure_playbook.md) |
| **HubSpot** | CRM: contacts, lifecycle | Bi-directional | Private-app token | REST JSON | [`XR7/services/hubspot_client.py`](../../XR7/services/hubspot_client.py), Celery [`XR7/tasks/hubspot.py`](../../XR7/tasks/hubspot.py) | Retry with bounded backoff; sync drift surfaced in admin audit |
| **LLM — OpenAI** | Claim drafting, advisory, negotiation | Outbound | API key | REST (via LangChain `ChatOpenAI`) | [`XR7/llm/claim_drafter.py`](../../XR7/llm/claim_drafter.py) | Degrade to "draft unavailable, retry later"; confidence gating in [`XR7/ml/confidence_gating.py`](../../XR7/ml/confidence_gating.py) |
| **LLM — xAI** | Same as OpenAI, alternate provider | Outbound | API key | REST (via LangChain `ChatXAI`) | [`XR7/llm/claim_drafter.py`](../../XR7/llm/claim_drafter.py) (dynamic `importlib` load) | Fallback to other provider |
| **YouTube Studio** | Creator earnings ingestion | Inbound | User-provided export / OAuth (see env `YOUTUBE_OAUTH_*`) | CSV | [`XR7/ingestion/creator_parsers.py`](../../XR7/ingestion/creator_parsers.py) | Row-level parse errors → quarantine; statement-level failure → user-visible error |
| **Generic statement upload** (Spotify, Apple Music, PROs, etc.) | Royalty-statement ingestion | Inbound | User-authenticated file upload | CSV / XLSX in PRO/DSP native format | [`XR7/ingestion/statement_parser.py`](../../XR7/ingestion/statement_parser.py) + format-specific detectors | Parse failures route to analyst review |
| **Supabase Auth** (target) | Identity | Bi-directional | OAuth / magic link / password | JWT | Not yet integrated — see [06-identity](06-identity.md); legacy self-signed JWT today | n/a until integrated |
| **AWS CloudWatch / S3 / RDS** (target) | Infra services | — | IAM role | AWS SDK | Not yet deployed — see [03-deployment](03-deployment.md) | n/a until deployed |
| **Prometheus / Grafana** (target) | Metrics + alerting | Outbound (scrape) | mTLS | `/metrics` exposition | Pending [#94](https://github.com/k6-labs-hq/ArtistOS/issues/94)–[#96](https://github.com/k6-labs-hq/ArtistOS/issues/96) — see [07-observability](07-observability.md) | n/a until wired |

## Notes on PRO / DSP coverage

The EPIC asks about "PROs and DSPs" as if each were a first-class integration. In practice today:

- **Inbound statements** are handled by a generic file-upload pipeline — there is **no per-provider API client** for ASCAP, BMI, SESAC, SoundExchange, Apple Music, or Spotify in the repo. Test fixtures exist for ASCAP, BMI, and Spotify CSV shapes ([`tests/test_data/`](../../tests/test_data/)) which is how we know the parser covers them.
- **Outbound claim submission** is dispatched per destination but the transport is usually email / portal upload, not API. Route logic is in `XR7/recovery/`.
- **YouTube** is the only DSP with a dedicated parser for creator-specific data ([`XR7/ingestion/creator_parsers.py`](../../XR7/ingestion/creator_parsers.py)).

If you're picking up work to add a first-class PRO or DSP API integration, see [`docs/partner_integration_architecture.md`](../partner_integration_architecture.md) for the patterns we've converged on (webhook ingestion, idempotency keys, data-contract versioning).

## Idempotency & retries

- **Inbound (statements, webhooks):** dedupe on `(tenant_id, source, provider_statement_id)` at the DB layer.
- **Outbound (Trolley, HubSpot):** idempotency keys passed through where the provider supports them; Celery tasks idempotent on `(claim_id, attempt_no)` via audit-log check.
- **LLM:** not idempotent; each draft is a new generation. Drafts are stored and versioned, not retried.

## Secrets

All external-system credentials are loaded via [`xr7_common/settings.py`](../../xr7_common/settings.py) from environment variables. In prod these come from AWS Secrets Manager (see [03-deployment](03-deployment.md)). The canonical var list is in [`.env.example`](../../.env.example).

## See also

- [`docs/partner_integration_architecture.md`](../partner_integration_architecture.md) — integration patterns deep-dive
- [`docs/partner_distributor_integration_guide.md`](../partner_distributor_integration_guide.md) — distributor-specific integration notes
- [`docs/ingestion_format_catalog.md`](../ingestion_format_catalog.md) — per-format statement quirks
- [`docs/trolley_failure_playbook.md`](../trolley_failure_playbook.md) — disbursement recovery
