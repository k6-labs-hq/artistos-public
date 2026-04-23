# Access Policy

**Who can do what, where.** The team includes offshore contract developers; this doc is the source of truth for which credentials they get and which they don't.

## Principle

1. **Local dev: everyone gets full power.** That's the point — they code and test on their laptop.
2. **QA: everyone can deploy to, read from.** QA contains only fake/seed data.
3. **Prod: admins only.** No offshore dev ever logs into a prod VM or sees a production secret.
4. **No real artist data outside prod.** Ever.

## Role matrix

| Resource | Admin (Jason, Matt) | Maintain (Saqib) | Write (offshore devs) |
|----------|:-------------------:|:----------------:|:---------------------:|
| GitHub repo — read | ✅ | ✅ | ✅ |
| GitHub repo — push branches | ✅ | ✅ | ✅ |
| GitHub repo — merge PRs | ✅ | ✅ | ❌ (open PR, admin merges) |
| GitHub repo — change settings | ✅ | ❌ | ❌ |
| Local dev environment | ✅ | ✅ | ✅ |
| QA — push to deploy (auto via CI) | ✅ | ✅ | ✅ (via PR → merge) |
| QA VM — SSH | ✅ | ✅ | ❌ |
| QA — secrets (Hetzner QA token, Supabase test project, Trolley sandbox) | ✅ | ✅ (read-only) | ❌ |
| Prod — trigger deploy | ✅ | ❌ | ❌ |
| Prod — approve deploy | ✅ | ❌ | ❌ |
| Prod VM — SSH | ✅ | ❌ | ❌ |
| Prod — secrets (real Supabase, real Trolley, JWT signing keys, DB creds) | ✅ | ❌ | ❌ |
| Real artist data (read) | ✅ | ❌ | ❌ |
| Hetzner Cloud Console | ✅ | ❌ | ❌ |
| DNS (Porkbun) | ✅ | ❌ | ❌ |
| Billing (Hetzner, Supabase, etc.) | ✅ | ❌ | ❌ |

## How this is enforced

| Boundary | Mechanism |
|----------|-----------|
| PR merge control | Branch protection: `main` requires PR + 1 admin review; no direct pushes |
| Prod deploy gate | GitHub Environment `prod` with required reviewers = admins |
| Prod secret access | GitHub Environment `prod` secrets — only reviewable inside workflow runs approved by admins |
| Prod VM SSH | Only admin public keys in the Terraform `ssh_key_names` for the prod VM |
| Prod DB access | No direct DB credentials issued to non-admins; all queries go through the API with scoped JWT |
| Repo admin actions | Only admins can change settings, invite users, manage secrets |

## Onboarding checklist (new offshore dev)

1. Invite to repo with **Write** access only.
2. Add them to the `developers` team (not `admins`).
3. Share the local dev runbook link ([CONTRIBUTING.md](../../CONTRIBUTING.md)).
4. They get a Supabase test project user so they can exercise auth in QA.
5. They get seed data from `scripts/seed_data.py`. **Never share prod dumps.**
6. Confirm in writing they understand: **no prod access ever, no real artist data on their machine.**

## Offboarding checklist (dev leaves)

1. Remove from GitHub repo (immediate).
2. Rotate any QA credentials they might have observed (Supabase test key, Trolley sandbox).
3. If they had any prod-adjacent access (should not have), rotate every prod secret.
4. Revoke any API tokens they were issued.
5. Audit recent repo activity for unusual pulls or clones.

## Emergency access

If an admin is unreachable and a prod issue needs immediate attention:

1. Other admin acts solo.
2. If sole admin is unreachable → document the incident, decision to wait or escalate, and resume review discipline once they're back.

Never share admin credentials to work around this. If we can't reach the second admin we fix that structural issue, not the workaround.
