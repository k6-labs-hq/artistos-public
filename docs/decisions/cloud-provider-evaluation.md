# Cloud Provider Evaluation for ArtistOS

**Prepared for**: CEO / Founder
**Prepared by**: CTO
**Date**: 2026-04-21
**Status**: Decision pending

---

## TL;DR

We need to pick a cloud provider to host ArtistOS for the MVP pilot and first year of growth.

**Recommendation**: **Hetzner** for MVP and first ~100 artists. Migrate to AWS if/when we land an enterprise customer that requires it. This saves roughly **$2,400/year** at MVP scale with minimal downside given our workload profile (no HIPAA, no PCI, PII only).

**Decision required**: Approve vendor + AWS later reassessment milestone.

---

## What ArtistOS actually needs

| Requirement | Size at MVP | Projected at 100 artists |
|---|---|---|
| Compute | 1 web + 1 worker VM (2 vCPU / 4 GB) | 2 web + 2 worker (scale vertically first) |
| Database | PostgreSQL, ~10 GB | PostgreSQL, ~100 GB |
| Cache / queue | Redis, 1 GB | Redis, 2 GB |
| Object storage | ~50 GB (uploads + evidence PDFs) | ~1 TB |
| Bandwidth | ~100 GB/mo outbound | ~2 TB/mo outbound |
| Managed auth | Via Supabase (separate SaaS) | Same |
| Email / SMS | Via Supabase + Trolley | Same |

**Regulatory scope**: PII (artist names, emails, phones), financial statements, contractual data. **No HIPAA, no PCI (Trolley handles payments), no SOC 2 required until enterprise sales.**

---

## Options evaluated

| Provider | Tier | Managed DB | Notable |
|---|---|---|---|
| **Hetzner** | Bare-metal / VPS | ✅ (new, EU) | Cheapest; EU only |
| **AWS** | Hyperscaler | ✅ (RDS) | Most services; most expensive |
| **Google Cloud (GCP)** | Hyperscaler | ✅ (Cloud SQL) | Strong data tooling |
| **Azure** | Hyperscaler | ✅ | Enterprise/Microsoft-shop preference |
| **DigitalOcean** | Developer cloud | ✅ (Managed DB) | Simple; mid-tier pricing |
| **Fly.io** | Modern PaaS | ✅ | Edge-first; young product |
| **Render** | Modern PaaS | ✅ | Heroku-like; easy deploys |
| **Vultr / Linode** | Developer cloud | ✅ | Similar to DO, slightly cheaper |

---

## Monthly cost estimates

Prices assume **MVP configuration** (single region, single-AZ, no high-availability yet). Growth estimate assumes **~100 artists, ~1 TB object storage, ~2 TB egress**. All USD, rounded.

| Provider | MVP / month | Growth / month | 5-yr lock-in risk |
|---|---|---|---|
| **Hetzner** | **$35** | **$120** | Low (Docker → portable) |
| DigitalOcean | $70 | $280 | Low |
| Render | $80 | $320 | Medium (some proprietary config) |
| Fly.io | $60 | $250 | Medium |
| Vultr / Linode | $40 | $150 | Low |
| **GCP** | $140 | $550 | Medium-High |
| **AWS** | $180 | $700 | **High** |
| **Azure** | $170 | $650 | Medium-High |

> **Note**: These exclude Supabase (~$0 free tier), Trolley (per-transaction), LLM provider (per-token), and Sentry (free tier). Those costs are identical across providers.

---

## Pros and cons per provider

### Hetzner (German hosting, VPS + managed Postgres)

**Pros**
- 5–7x cheaper than AWS at comparable specs.
- EU-hosted by default — straightforward GDPR story.
- Flat, predictable pricing (no egress surprises).
- Good enough for serious workloads — many production SaaS companies run on it.
- Hetzner Cloud has matured significantly in 2024–2025: managed Postgres, object storage, load balancers, firewalls, snapshots.
- Docker / Compose / Kubernetes all work natively.

**Cons**
- Smaller service catalog than AWS. No managed equivalents for SQS, Cognito, SES, Lambda, CloudFront.
- Support is email-only with slower response times.
- No first-party identity / email / SMS — we use Supabase / SendGrid / Twilio alongside.
- Only EU / US-east locations; no APAC presence.
- Less "enterprise buyer recognized" brand than AWS.

**When to use**: Cost-sensitive MVP, early-stage SaaS, EU-first GDPR workload. **This is our situation.**

---

### AWS

**Pros**
- Deepest service catalog. If we ever need it, AWS has it.
- Strongest compliance posture (SOC 2, HIPAA-eligible, FedRAMP). Enterprise customers often require it.
- Best auto-scaling, load balancing, multi-region story.
- Managed RDS Postgres is the gold standard for managed databases.
- IAM + Organizations is genuinely superior for multi-team orgs.
- Most third-party tooling integrates first-class.

**Cons**
- **Most expensive** — ~5x Hetzner at comparable specs before egress.
- **Egress is a tax** — moving 1 TB/mo out of AWS costs ~$90/mo on top of compute.
- Complex billing. Surprise costs are common.
- Steep learning curve; strong operational discipline required.
- Vendor lock-in is real — SQS, Cognito, Lambda, DynamoDB, IAM policies all have no direct portable equivalent.

**When to use**: Enterprise sales require it, scale justifies the complexity, or we need a service only AWS offers.

---

### Google Cloud Platform (GCP)

**Pros**
- Cheaper than AWS for compute (~20–30%).
- Best-in-class data analytics (BigQuery) if we ever need it for royalty analytics at scale.
- Strong Kubernetes story (GKE was first-class managed K8s).
- Cleaner, less labyrinthine console than AWS.

**Cons**
- Smaller ecosystem of third-party tools and enterprise customers.
- Google has a track record of deprecating services.
- Support tiers are confusing and support quality varies.
- Enterprise buyers are less familiar with it than AWS.

**When to use**: Data-heavy workload, team loves Kubernetes, prefer GCP's simpler IAM.

---

### Azure

**Pros**
- Strong Microsoft / enterprise integration (Active Directory, Office).
- Close to AWS in service breadth.
- Good for regulated industries (lots of compliance certifications).

**Cons**
- Console is widely considered the worst of the hyperscalers.
- Pricing is complex.
- Slowest to adopt open-source-native patterns.
- Only advantage over AWS for us would be existing Microsoft relationships — we have none.

**When to use**: Enterprise customers on Microsoft stack. Not relevant to our target market today.

---

### DigitalOcean

**Pros**
- 2–3x cheaper than AWS, simple pricing.
- Managed Postgres, Redis, Spaces (S3-compatible), and App Platform.
- Dev-friendly UX; good docs.
- Community tutorials are excellent.

**Cons**
- Smaller scale and SLAs than hyperscalers.
- Service catalog is mid-tier — enough for most apps, thin for advanced needs.
- Fewer regions than AWS/GCP.
- Moderate egress costs (~$0.01/GB after 5 TB free).

**When to use**: Middle ground between Hetzner and AWS. Good "grown-up developer cloud."

---

### Render

**Pros**
- Easiest deployment experience of any option. Git push → deployed.
- Managed Postgres, Redis, static sites, cron jobs all built-in.
- No infrastructure to run — pure PaaS.
- Strong free tier for testing.

**Cons**
- Paying for convenience — ~2.5x Hetzner.
- Some proprietary configuration (`render.yaml`) creates modest lock-in.
- Smaller than the majors; platform risk.
- Limited control; hard to do anything unusual.

**When to use**: Team wants to minimize ops burden. Good for early startups without a dedicated SRE.

---

### Fly.io

**Pros**
- Modern architecture — deploys containers globally at the edge.
- Fast cold starts, good latency story.
- Postgres clusters with automatic failover.
- Popular with developers; Docker-first.

**Cons**
- Platform is younger than the alternatives; had a major outage in 2024.
- Pricing is per-machine-hour, can be hard to predict.
- Some unique concepts (fly volumes, fly proxy) have a learning curve.

**When to use**: Latency-sensitive workload, or team that wants modern infra without AWS complexity.

---

### Vultr / Linode

**Pros**
- Similar to DigitalOcean, slightly cheaper.
- Linode (now Akamai) has strong bandwidth included.
- Global footprint.

**Cons**
- Slightly less polished UX than DO.
- Managed services catalog thinner than DO.
- Similar tradeoffs to DigitalOcean overall.

**When to use**: Price-sensitive, want more regions than Hetzner.

---

## Decision matrix

Weights: **cost (30%)**, **dev productivity (25%)**, **compliance/enterprise readiness (20%)**, **portability (15%)**, **support (10%)**.

Scores 1–5 where 5 is best.

| Provider | Cost | Dev prod | Compliance | Portability | Support | Weighted |
|---|---|---|---|---|---|---|
| **Hetzner** | 5 | 3 | 3 | 5 | 2 | **3.85** |
| DigitalOcean | 4 | 4 | 3 | 4 | 4 | 3.85 |
| Render | 3 | 5 | 3 | 3 | 4 | 3.60 |
| Fly.io | 4 | 4 | 3 | 4 | 3 | 3.75 |
| AWS | 1 | 3 | 5 | 2 | 5 | 2.85 |
| GCP | 2 | 3 | 5 | 3 | 4 | 3.10 |
| Azure | 2 | 2 | 5 | 3 | 4 | 2.85 |
| Vultr / Linode | 5 | 3 | 3 | 4 | 3 | 3.70 |

Top three: **Hetzner, DigitalOcean, Fly.io** all cluster around 3.75–3.85 for our needs.

---

## Recommendation

**Choose Hetzner for MVP and first year.**

**Reasoning**:
1. Our workload is modest (single-region, 1–100 artists, no HIPAA).
2. The cost savings (~$2,400/year at MVP scale, growing with us) fund another month of runway.
3. EU hosting is a positive for GDPR and for any European artists.
4. Docker Compose on a VM is portable — **if we ever need AWS, migration is a weekend's work**, not a rewrite.
5. Supabase + Trolley + Sentry already cover the high-value managed services we need, and they're vendor-neutral.

**Reassess AWS at these triggers**:
- First enterprise deal requiring AWS (common in music-industry B2B).
- Growth past ~500 artists where multi-region / autoscaling complexity exceeds the savings.
- SOC 2 Type II audit kicks off (AWS's compliance posture accelerates this).

**Keep these decisions vendor-neutral regardless**:
- Auth (Supabase — separate SaaS).
- Error tracking (Sentry — separate SaaS).
- Payments (Trolley — separate SaaS).
- Code (Docker Compose — runs anywhere).

---

## If the CEO prefers AWS anyway

It's defensible. Extra cost is ~$150/month at MVP. The main wins are:

1. One bill for everything (AWS bundle includes Cognito, SES, SNS, S3 under one account).
2. Stronger enterprise-buyer story from day one.
3. Easier compliance story if we pursue SOC 2 early.
4. Can use App Runner instead of ECS to keep ops simple.

**Either decision is reasonable. This is a cost/complexity tradeoff, not a technical blocker.**

---

## Next steps

Upon decision:
1. Update [docs/architecture/03-deployment.md](../architecture/03-deployment.md) to reflect chosen provider.
2. Update [docs/architecture/09-production-readiness.md](../architecture/09-production-readiness.md) — section 6 specifics.
3. Close out part of [#102](https://github.com/k6-labs-hq/ArtistOS/issues/102) (prod env epic) with the chosen path.
4. Provision account, set up Terraform (AWS) or Pulumi/Ansible (Hetzner) for IaC.
5. Deploy staging first, validate the production readiness checklist against it.

**Target to first deployed URL**: 5–7 days after decision, assuming the MVP happy path is working locally (currently not — see section 1 of the production readiness checklist).
