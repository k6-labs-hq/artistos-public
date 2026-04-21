# Hetzner Deployment

Production deployment path for ArtistOS. Vendor-neutral at the app layer (Docker Compose) with a thin Hetzner-specific infrastructure layer. Portable to AWS — see [`../PORTABILITY.md`](../PORTABILITY.md).

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

## First-time deployment

```bash
# 1. Provision infra via Terraform
cd infrastructure/hetzner/terraform
export HCLOUD_TOKEN=<your-token>
terraform init
terraform apply   # creates VM, firewall, Postgres, Object Storage

# 2. SSH to the VM (IP printed in Terraform output)
ssh root@<vm-ip>

# 3. Clone repo
git clone https://github.com/k6-labs-hq/ArtistOS.git /opt/artistos
cd /opt/artistos/infrastructure/hetzner

# 4. Populate production .env
cp .env.prod.example .env.prod
vi .env.prod   # paste real secrets

# 5. First deploy
bash deploy.sh

# 6. Verify
curl https://api.your-domain.com/health
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
