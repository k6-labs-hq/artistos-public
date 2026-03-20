# Container Registry & Deployment Workflow

## Overview

This document describes the end-to-end flow from code push → Docker image build → GHCR push → K8s deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Developer: git push to main                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ GitHub Actions: container-publish.yml runs                  │
│ - Docker buildx build (with GHA cache)                      │
│ - Push to ghcr.io/mkallberg21/artistos:{tags}              │
│   Tags: latest, main-<sha>, version tags                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ Image lives in GHCR (GitHub Container Registry)            │
│ ghcr.io/mkallberg21/artistos:latest                        │
│ ghcr.io/mkallberg21/artistos:main-abc1234                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ Deploy to environment:                                       │
│ ./scripts/ops/deploy_env.sh <env> <tag>                    │
│                                                             │
│ - Deploys K8s overlays (infrastructure/kubernetes/*)       │
│ - kubectl set image to specified tag                       │
│ - Waits for rollout completion                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ K8s pulls image from GHCR using credentials                │
│ - ServiceAccount references ghcr-io-credentials secret     │
│ - Workloads: xr7-api, xr7-worker, xr7-scheduler           │
└──────────────────────────────────────────────────────────────┘
```

## Step-by-Step Workflow

### 1. Local Development & Testing

Test Docker build locally before push:

```bash
# Build and load image to Docker daemon
make docker-build

# Verify image was created
docker image ls xr7:latest
docker run -p 8000:8000 xr7:latest
```

### 2. Commit & Push

```bash
git add .
git commit -m "feature: ..."
git push origin main
```

GitHub Actions automatically triggers `container-publish.yml`:
- Builds Docker image using `docker/buildx`
- Pushes to `ghcr.io/mkallberg21/artistos` with tags like:
  - `latest` (if on main branch)
  - `main-<commit-sha>` (branch + SHA)
  - `0.1.0` (if git tag matches semver)

### 3. Deploy to Environment

#### Option A: Deploy with default `latest` tag

```bash
# Deploy dev environment
./scripts/ops/deploy_env.sh dev latest

# Deploy staging
./scripts/ops/deploy_env.sh staging latest

# Deploy prod
./scripts/ops/deploy_env.sh prod latest
```

#### Option B: Deploy specific build SHA

```bash
# Get latest commit SHA
export SHA=$(git rev-parse --short HEAD)

# Deploy that exact build
./scripts/ops/deploy_env.sh prod main-${SHA}
```

### 4. First-Time GHCR Authentication (Per Environment)

The K8s cluster needs credentials to pull from GHCR. Create a GitHub Personal Access Token first:

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Create token with `read:packages` scope
3. Save as environment variable: `export GHCR_TOKEN=ghp_xxx...`

Then apply credentials to cluster:

```bash
# Create runtime.env with your app secrets
cat > /tmp/runtime.env <<EOF
DATABASE_URL=postgresql://...
CELERY_BROKER_URL=redis://...
...
EOF

# Apply both runtime secrets + GHCR credentials
./scripts/ops/apply_runtime_secret.sh xr7 /tmp/runtime.env "${GITHUB_USER}" "${GHCR_TOKEN}"
```

This creates:
- `xr7-runtime-secrets` (app configuration)
- `ghcr-io-credentials` (K8s imagePullSecret)

## Workflow Files

### GitHub Actions: `.github/workflows/container-publish.yml`

- Trigger: Push to main, PRs
- Action: Builds Docker image
- Output: Pushes to GHCR with auto-tagger
- Cache: Uses GitHub Actions cache layer (fast rebuilds)

### Local Make Target: `make docker-build`

```bash
docker buildx build --load -t xr7:latest .
```

Loads image into local Docker daemon for testing.

### Kubernetes Configuration

**Base Manifests** (`infrastructure/kubernetes/base/`):
- `workloads.yaml` — API, worker, scheduler deployments
- `namespace.yaml` — Namespace + ServiceAccount (with imagePullSecrets)
- `autoscaling.yaml` — Horizontal Pod Autoscalers
- `security.yaml` — Network policies, pod security policies
- `ingress.yaml` — Ingress controller config
- `backup-cronjob.yaml` — Database backup scheduler

**Environment Overlays** (`infrastructure/kubernetes/overlays/{dev,staging,prod}/`):
- `kustomization.yaml` — Environment-specific patches
- `replica-counts.yaml` — Env-specific replica overrides

### Deploy Script: `scripts/ops/deploy_env.sh`

```bash
# Usage
./scripts/ops/deploy_env.sh <dev|staging|prod> <image_tag> [namespace]

# Examples
./scripts/ops/deploy_env.sh dev latest
./scripts/ops/deploy_env.sh staging main-a1b2c3d
./scripts/ops/deploy_env.sh prod 0.5.0
```

Steps:
1. Validates environment overlay exists
2. Applies K8s manifests via `kubectl apply -k`
3. Updates image tag: `kubectl set image deployment/...`
4. Waits for rollout with 300s timeout
5. Reports success

### Secrets Script: `scripts/ops/apply_runtime_secret.sh`

```bash
# Usage
./scripts/ops/apply_runtime_secret.sh [namespace] <env_file> [ghcr_username] [ghcr_token]

# Example
./scripts/ops/apply_runtime_secret.sh xr7 ~/secrets/prod.env mkallberg21 ghp_xxx...
```

Creates two K8s secrets:
- `xr7-runtime-secrets` (generic) — App config from env file
- `ghcr-io-credentials` (docker-registry) — GHCR authentication

## Image Tags

### Available Tags After Push to Main

```
ghcr.io/mkallberg21/artistos:latest      # Always latest main commit
ghcr.io/mkallberg21/artistos:main-abc1234   # Specific commit
ghcr.io/mkallberg21/artistos:0.5.0       # (if tagged as release)
```

### Using Tags in Deployments

```bash
# Deploy latest (recommended for dev/staging)
./scripts/ops/deploy_env.sh staging latest

# Deploy specific commit (for rollback/bisect)
./scripts/ops/deploy_env.sh staging main-abc1234

# Deploy release tag (for prod with version control)
./scripts/ops/deploy_env.sh prod 0.5.0
```

## Troubleshooting

### Image Pull Failed: `Failed to pull image`

**Solution:** Apply GHCR credentials:
```bash
./scripts/ops/apply_runtime_secret.sh xr7 ~/.env "${GITHUB_USER}" "${GHCR_TOKEN}"
```

### Rollout Timeout: `deployment did not progress`

**Check logs:**
```bash
kubectl -n xr7 logs deployment/xr7-api --tail=100
kubectl -n xr7 describe pod xr7-api-xxxxx

# Check image pull events
kubectl -n xr7 get events | grep -i pull
```

### Wrong Image Version Deployed

**Verify current image:**
```bash
kubectl -n xr7 get deployment xr7-api -o jsonpath='{.spec.template.spec.containers[0].image}'
# Should output: ghcr.io/mkallberg21/artistos:<your-tag>
```

**Redeploy correct tag:**
```bash
./scripts/ops/deploy_env.sh prod latest
```

## Security Notes

- **GHCR tokens** should be stored in a secure vault, never in git
- **imagePullSecret** is applied to ServiceAccount; all pods inherit it
- **imagePullPolicy: Always** ensures fresh images on every deploy (set in K8s manifests)
- **GitHub GITHUB_TOKEN** used in CI has automatic `packages: read` permission; no additional setup needed for public images
