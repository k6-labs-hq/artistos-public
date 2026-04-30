# Postmark setup runbook

**Status:** Required to take XR7 out of stub mode for outbound email + inbound dispute reply correlation. Without this, the recovery loop email path (#176/#178) cannot deliver real disputes.

**Estimated time:** ~2 hours including DNS propagation wait.

## Why Postmark

Decided in the [disruption analysis](../strategy/disruption-analysis-2026-04-29.md) and the conversation around the manual-recovery runbook. Short version: transactional-only IP pool (better deliverability than SendGrid's mixed pool), clean inbound parse for reply correlation, and stable ownership. The wrapper at [`XR7/services/postmark_client.py`](../../XR7/services/postmark_client.py) is the only outbound email path going forward.

## Step 1 — Create the Postmark account

1. Sign up at [postmarkapp.com](https://postmarkapp.com). The K6 Labs admin account should own this — not a personal account.
2. Pick the **Starter** tier (\$15/mo, 10k emails). We won't approach that ceiling for months.
3. Create one **Server** for the project. Name it `xr7-qa` initially. (Production gets its own server — separate keys, separate sender reputations.)

## Step 2 — Verify the sending domain

Using `xr7.k6-labs.com` as the sending domain (matches our existing app/api domains; lets us inherit their TLS reputation).

1. In Postmark → Sender Signatures → Add Domain → enter `xr7.k6-labs.com`.
2. Postmark will give you four DNS records to add:
   - 1 × DKIM (TXT) — the cryptographic signing key
   - 1 × Return-Path (CNAME) — bounce handling
   - SPF (TXT) — must be merged into existing SPF record if any
   - DMARC (TXT) — recommended, not required to start
3. Add these to the DNS provider for `k6-labs.com`. Hetzner DNS, Cloudflare, or wherever the existing app/api A records live.
4. Wait for verification (usually 10–30 minutes; can take up to a few hours).
5. Once verified, create two sender signatures:
   - `notifications@xr7.k6-labs.com` (user-facing notifications: anomaly alerts, deposit confirmations)
   - `disputes@xr7.k6-labs.com` (regulatory correspondence: dispute filings to PROs/DSPs)

   Keeping them split means deliverability monitoring is per-channel — a marketing-style email going to spam doesn't poison our dispute inbox reputation.

## Step 3 — Capture the API token

In Postmark → Servers → `xr7-qa` → API Tokens → copy the **Server API Token**. This is what `POSTMARK_API_TOKEN` gets set to.

> Treat this like a database password. Anyone with it can send email impersonating our domain.

## Step 4 — Configure inbound parse

This is what closes the dispute reply loop — when BMI emails back with a case-ref number, Postmark POSTs the parsed payload to our webhook.

1. In Postmark → Servers → `xr7-qa` → Inbound → enable the Inbound Stream.
2. Set the **Inbound Webhook URL** to:
   ```
   https://api.qa.xr7.k6-labs.com/webhooks/postmark/inbound
   ```
3. Generate a strong shared secret:
   ```bash
   openssl rand -hex 32
   ```
4. In Postmark, add a **custom header** for the inbound webhook:
   - Name: `X-Postmark-Webhook-Token`
   - Value: the secret you just generated
5. Set `POSTMARK_INBOUND_WEBHOOK_TOKEN` on QA to the same value (see Step 5 below).

The endpoint at [`XR7/api/routers/postmark_webhooks.py`](../../XR7/api/routers/postmark_webhooks.py) validates this header on every inbound POST. Without it the endpoint returns 401, and without the env var configured at all it returns 503 (so misconfiguration is visible in monitoring instead of silently accepting forged payloads).

## Step 5 — Wire env vars on QA

SSH to the QA host and edit `/opt/artistos/.env.qa`:

```bash
POSTMARK_API_TOKEN=<server-api-token-from-step-3>
POSTMARK_FROM_EMAIL=notifications@xr7.k6-labs.com
POSTMARK_DISPUTES_FROM_EMAIL=disputes@xr7.k6-labs.com
POSTMARK_INBOUND_WEBHOOK_TOKEN=<openssl-generated-secret-from-step-4>
```

Then restart the api + worker:

```bash
cd /opt/artistos
docker compose -f docker-compose.prod.yml --env-file .env.qa up -d api worker scheduler
```

## Step 6 — Smoke test

### Outbound

From the QA host, fire a test email to your own inbox:

```bash
docker exec artistos-api-1 python -c "
from XR7.services.postmark_client import get_postmark_client, reset_default_client
reset_default_client()
result = get_postmark_client().send_email(
    to='YOUR_EMAIL@example.com',
    subject='XR7 Postmark smoke test',
    text_body='If you got this, outbound is wired.',
    tag='smoke-test',
)
print(result)
"
```

Expected: `PostmarkSendResult(delivered=True, message_id='<uuid>', stubbed=False, ...)`. The email lands in the inbox within seconds. Stubbed=False is the proof the live path is wired.

### Inbound

Reply to that test email. Within ~30 seconds, check the API logs for an `postmark_inbound_received` log entry:

```bash
ssh root@178.156.210.206 'docker logs artistos-api-1 2>&1 | tail -50 | grep postmark_inbound'
```

If you see the log entry with the right subject + from address, inbound parse is wired. The immutable ledger will have an entry only if the reply's `Metadata.artist_id` matched a real Artist row — for a manual smoke test that field will be empty, which is fine.

## Step 7 — Production setup (when ready)

Production gets its own Postmark server (`xr7-prod`) with separate API token and DKIM keys. Don't share QA + prod sender reputation — a deliverability problem in QA shouldn't block real artists from getting their dispute filings out.

The same six steps apply, swapping `qa` → `prod` everywhere. Production-specific:

- Sender domain: same `xr7.k6-labs.com` is fine (one DKIM record per domain regardless of env)
- DMARC policy: bump to `p=quarantine` after 30 days of clean QA history; `p=reject` after 90
- Set up Postmark monitoring webhooks (bounces, spam reports) → Slack alerts; 5%+ bounce rate is a deliverability emergency

## Troubleshooting

**Smoke test returns `stubbed=True`** — the env var isn't loaded into the running container. Re-run `docker compose up -d api` after editing `.env.qa`. Check `docker exec artistos-api-1 env | grep POSTMARK` to confirm.

**Email lands in spam** — domain verification incomplete (some DNS record didn't propagate) or DMARC alignment issue. Check `https://www.mail-tester.com/` — send it a test from the same configuration and read the score.

**Inbound webhook returns 401 on Postmark's test send** — the `X-Postmark-Webhook-Token` header isn't configured in Postmark inbound settings, OR the value differs from `POSTMARK_INBOUND_WEBHOOK_TOKEN` on QA. Both must match exactly.

**Inbound webhook returns 503** — `POSTMARK_INBOUND_WEBHOOK_TOKEN` is unset on QA. Webhook explicitly refuses traffic without it; that's a feature, not a bug.

## What's NOT covered here

- **Per-payer dispute templates** — that's [#179](https://github.com/k6-labs-hq/ArtistOS/issues/179) and ships with the BMI playbook PR
- **Reply-to-claim correlation** — the inbound webhook currently writes a ledger entry for replay; the actual matching of "BMI reply → which claim" is the same #179 PR
- **PDF attachment of evidence packets** — separate work from email infrastructure; ships when the per-payer playbooks land
- **Bounce/complaint webhooks** — currently logged but not routed; production hardening adds this
