# Hetzner Deployment

Deployment path for ArtistOS QA and production. Vendor-neutral at the app layer (Docker Compose) with a thin Hetzner-specific infrastructure layer. Portable to AWS — see [`../PORTABILITY.md`](../PORTABILITY.md). Access control per [`docs/decisions/access-policy.md`](../../docs/decisions/access-policy.md).

## Deploy model: CI pushes (not VM pulls)

CI builds the Docker image and pushes to GHCR. CI then rsyncs only the small set of config files (this directory's `docker-compose.prod.yml`, `Caddyfile`, `deploy.sh`) to the VM and SSHes to run `docker compose pull && up`. **The VM never clones the repo** and has no GitHub credentials — just an SSH key and `.env.<env>`.

## Environments

| Environment | Where | Domain | Deploy trigger |
|-------------|-------|--------|----------------|
| **local** | your laptop (podman + docker-compose) | `localhost` | manual |
| **qa** | Hetzner VM `xr7-qa-app` | `api.qa.xr7.k6-labs.com` | auto on push to `main` |
| **prod** | Hetzner VM `xr7-prod-app` | `api.xr7.k6-labs.com` | `workflow_dispatch` + admin approval on the `prod` GitHub Environment |

Both Hetzner VMs live in the same Hetzner project (`artistos`), separate from the `trivia` project.

## Architecture

```
Internet ──▶ Hetzner Load Balancer ──▶ Caddy (TLS) ──┬──▶ xr7-api (2+ replicas)
                                                      ├──▶ xr7-worker (Celery)
                                                      └──▶ xr7-scheduler (Celery beat)

                                                  Hetzner Managed Postgres
                                                  Hetzner Object Storage (S3-compatible)
                                                  Redis (on-VM or separate)
```

Supabase (auth), Trolley (payouts), Sentry (errors), and the LLM provider are separate SaaS — identical across clouds.

## What's in this directory

| File | Purpose |
|---|---|
| `docker-compose.prod.yml` | Production Compose stack (app + worker + scheduler + redis + caddy) |
| `Caddyfile` | Reverse proxy + automatic Let's Encrypt TLS |
| `.env.prod.example` | All required env vars, placeholders only |
| `deploy.sh` | One-command deploy script (pulls image, runs migrations, restarts) |
| `terraform/` | IaC for the VM, firewall, private network, managed Postgres, object storage |

## Prerequisites

1. **Hetzner Cloud account** with project created.
2. **API token** with read/write access (Project → Security → API Tokens).
3. **Domain** with DNS pointing to the Hetzner Load Balancer IP (Cloudflare works great).
4. **GitHub Container Registry access** for pulling the xr7-api image.
5. **Secrets populated**: Supabase JWT secret, Trolley API key, JWT signing secret, DB credentials.

## First-time provisioning (per environment)

```bash
# 1. Provision infra via Terraform (run once for QA, once for prod)
cd infrastructure/hetzner/terraform
export HCLOUD_TOKEN=<your-token>
terraform init

# QA environment
terraform workspace new qa
terraform apply -var environment=qa -var 'ssh_key_names=["jason-admin","matt-admin","dev-ops"]'

# Prod environment — admin SSH keys ONLY
terraform workspace new prod
terraform apply -var environment=prod -var 'ssh_key_names=["jason-admin","matt-admin"]'

# 2. Point DNS at the load balancer IPs from terraform output
#    api.qa.xr7.k6-labs.com  → <qa-lb-ipv4>
#    api.xr7.k6-labs.com     → <prod-lb-ipv4>

# 3. SSH to each VM, bootstrap
ssh root@<vm-ip>
git clone https://github.com/k6-labs-hq/ArtistOS.git /opt/artistos
cd /opt/artistos/infrastructure/hetzner

# 4. Populate environment file
cp .env.qa.example .env.qa       # (or .env.prod.example .env.prod)
vi .env.qa                       # paste real secrets

# 5. First deploy
bash deploy.sh

# 6. Verify
curl https://api.qa.xr7.k6-labs.com/health
```

## Day-two operations

| Task | Command |
|---|---|
| Deploy a new image | `bash deploy.sh` on the VM (pulls `:latest` from GHCR) |
| Run migrations only | `docker compose -f docker-compose.prod.yml run --rm api alembic upgrade head` |
| View logs | `docker compose -f docker-compose.prod.yml logs -f api worker` |
| Restart a service | `docker compose -f docker-compose.prod.yml restart api` |
| Database shell | `docker compose -f docker-compose.prod.yml exec db psql -U xr7` |
| Back up Postgres | handled by Hetzner Managed Postgres automatic backups; plus `pg_dump` cron off-site |

## Production readiness before cutover

Walk [docs/architecture/09-production-readiness.md](../../docs/architecture/09-production-readiness.md) top to bottom. Every `☐` must become `✅` or `🟡 <reason>` before the first artist is onboarded.
