# Deployment Execution Runbook (Full Code Path)

This runbook executes full environment provisioning and deployment with the code in this repository.

## 0) Prerequisites
- Terraform >= 1.6
- kubectl configured for target cluster
- Access to cloud state bucket configured in env main.tf
- Runtime secrets file generated from infrastructure/secrets/runtime.env.example

## 1) Configure Environment Variables
1. Copy example files:
   - cp infrastructure/terraform/environments/dev/terraform.tfvars.example infrastructure/terraform/environments/dev/terraform.tfvars
   - cp infrastructure/terraform/environments/staging/terraform.tfvars.example infrastructure/terraform/environments/staging/terraform.tfvars
   - cp infrastructure/terraform/environments/prod/terraform.tfvars.example infrastructure/terraform/environments/prod/terraform.tfvars
2. Fill real cluster endpoint, cert, token, and image tags.
3. Copy runtime env file:
   - cp infrastructure/secrets/runtime.env.example infrastructure/secrets/runtime.env
4. Fill real production values and keys.

## 2) Bootstrap Infrastructure
- Dev:
  - make bootstrap-dev
- Staging:
  - make bootstrap-staging
- Prod:
  - make bootstrap-prod

## 3) Apply Runtime Secrets
- make apply-runtime-secret

## 4) Deploy Workloads
- Dev:
  - make deploy-dev
- Staging:
  - make deploy-staging
- Prod:
  - make deploy-prod

## 5) Validate Platform
1. API health endpoint:
   - kubectl -n xr7 port-forward svc/xr7-api 8080:80
   - curl http://127.0.0.1:8080/health
2. Readiness endpoint:
   - curl http://127.0.0.1:8080/health/readiness
3. SLO gate script:
   - make slo-gate

## 6) Disaster Recovery Verification
1. Ensure backup cron exists:
   - kubectl -n xr7 get cronjob xr7-pg-backup
2. Execute restore drill:
   - DB_URL=<restore-target> make restore-drill

## 7) CI/CD Paths
- PRs with infra changes trigger:
  - .github/workflows/infrastructure-plan.yml
- Manual deployment trigger:
  - .github/workflows/progressive-deploy.yml
- Security scanning on PR/push:
  - .github/workflows/security-posture.yml
