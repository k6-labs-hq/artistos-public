# Portability: Hetzner today, AWS (or anywhere) tomorrow

ArtistOS is deployed on Hetzner for MVP, but the deployment is structured so
that switching to AWS — or any other cloud — doesn't require touching the
application code. This document is the map.

## What stays identical across clouds

Nothing in the app changes. These are the layers that are cloud-agnostic:

| Layer | Where it lives | Portability |
|---|---|---|
| Application code | `XR7/`, `frontend/` | 100% portable |
| Container image | `Dockerfile` + GHCR | Runs on any Docker host |
| Compose stack | [`hetzner/docker-compose.prod.yml`](hetzner/docker-compose.prod.yml) | Translates 1:1 to ECS Task Definitions, Cloud Run, or Nomad |
| Env vars | `.env.prod` | Same keys everywhere; only values change |
| Migrations | Alembic | Standard Postgres |
| Object storage API | `boto3` + `S3_ENDPOINT_URL` | Works with Hetzner Object Storage, AWS S3, MinIO, any S3-compatible |
| Auth | Supabase (separate SaaS) | Cloud-independent |
| Payouts | Trolley (separate SaaS) | Cloud-independent |
| Error tracking | Sentry (separate SaaS) | Cloud-independent |

## What changes per cloud

Only the infrastructure provisioning layer. See the mapping below.

### Mapping Hetzner resources → AWS equivalents

| Role | Hetzner (today) | AWS (migration target) |
|---|---|---|
| VM / compute | `hcloud_server` (Ubuntu + Docker) | ECS Fargate service, or EC2 + Docker Compose |
| Load balancer | `hcloud_load_balancer` | Application Load Balancer (ALB) |
| Private network | `hcloud_network` | VPC + private subnets |
| Firewall | `hcloud_firewall` | Security Groups |
| Managed Postgres | Hetzner Managed Postgres (console) | RDS Postgres |
| Redis | Docker container or Hetzner Redis Cloud | ElastiCache Redis |
| Object storage | Hetzner Object Storage (S3-compatible) | S3 bucket |
| TLS certs | Caddy + Let's Encrypt (automatic) | ACM + ALB listener |
| DNS | Cloudflare / Hetzner DNS | Route53 |
| Secrets | `.env.prod` file + file perms 0600 | Secrets Manager / SSM Parameter Store |
| Backups | Managed Postgres daily snapshots + `pg_dump` off-site | RDS automated backups |
| CDN (optional) | Cloudflare | CloudFront |

### What the migration looks like, concretely

1. **Swap Terraform modules**: replace `infrastructure/hetzner/terraform/main.tf` with an AWS equivalent module that provisions VPC + ECS cluster + RDS + ALB + S3.
2. **Update env vars**: the same keys, but the values point at AWS endpoints. `S3_ENDPOINT_URL` becomes `https://s3.us-east-1.amazonaws.com`, `DATABASE_URL` points at RDS.
3. **Swap TLS**: remove Caddy, use ALB with ACM.
4. **CI**: update `production-deploy.yml` to do `aws ecs update-service` instead of `ssh + deploy.sh`.
5. **Migrate data**: `pg_dump` from Hetzner Managed Postgres → `pg_restore` into RDS. Object storage via `rclone sync`.

Realistic timeline for a migration: **2–5 days** for someone familiar with AWS, mostly spent on IaC and a staging cutover. The app never needs to change.

## Design rules to preserve portability

Follow these when adding features. Violations make a migration harder:

1. **All config via env vars.** Never read from a cloud-specific metadata service unless wrapped behind a Settings class.
2. **Use S3-compatible APIs only** — never call `boto3.client('s3', region_name=...)` directly with cloud-specific parameters. Always honor `S3_ENDPOINT_URL`.
3. **No AWS-SDK-specific calls in app code.** No SQS, no Cognito in-app, no AWS Secrets Manager SDK calls. Use standard HTTP + env vars.
4. **Avoid cloud-only databases** (DynamoDB, BigQuery) in the MVP. If we ever need them, wrap behind an interface so we can swap back.
5. **Logs go to stdout.** Let the platform (Hetzner VM journal / CloudWatch agent / ECS logs) pick them up.
6. **Secrets injected at runtime, never baked into the image.** Image must be identical across environments.
7. **No hardcoded URLs.** Use env vars for all external service endpoints.

## Observability portability

| Concern | Hetzner (today) | AWS equivalent |
|---|---|---|
| Metrics | Prometheus on VM + Grafana (self-hosted) | CloudWatch + managed Grafana, or same self-hosted |
| Logs | Docker logs + journald + Loki (optional) | CloudWatch Logs, or same Loki |
| Traces | OTel collector → Jaeger or Honeycomb | OTel collector → X-Ray or Honeycomb |
| Errors | Sentry | Sentry (same) |

All four can stay identical if we use self-hosted Grafana + Loki. Only CloudWatch is AWS-specific — we only use it if we migrate.

## When to actually migrate

Don't migrate prematurely. Specific triggers:

1. An enterprise customer requires AWS (often a procurement checkbox).
2. Compliance audit (SOC 2 Type II) where AWS's pre-built audit controls save real time.
3. Scale that genuinely exceeds what a single Hetzner setup handles gracefully.
4. Multi-region requirements.

Until one of those hits, Hetzner is the right place to be.
