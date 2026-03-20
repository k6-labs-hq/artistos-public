# Infrastructure Acceleration Pack

This is executable platform code for provisioning and deploying XR7 across dev, staging, and prod.

## 1) Environment Ladder
- Environment roots:
  - infrastructure/terraform/environments/dev
  - infrastructure/terraform/environments/staging
  - infrastructure/terraform/environments/prod

## 2) Kubernetes Runtime
- Base manifests:
  - infrastructure/kubernetes/base
- Environment overlays:
  - infrastructure/kubernetes/overlays/dev
  - infrastructure/kubernetes/overlays/staging
  - infrastructure/kubernetes/overlays/prod

## 3) Infrastructure as Code
- Cloud foundation module (AWS VPC + EKS + RDS + Redis + S3 + KMS):
  - infrastructure/terraform/modules/aws_foundation
- Platform module (namespace + observability helm + runtime config):
  - infrastructure/terraform/modules/platform

## 4) Observability
- OpenTelemetry collector config, Prometheus SLO alert rules, Grafana dashboard:
  - infrastructure/observability

## 5) Data Reliability + DR
- Nightly backup cron + restore drill tooling:
  - infrastructure/kubernetes/base/backup-cronjob.yaml
  - scripts/ops/restore_drill.sh
  - infrastructure/runbooks/disaster_recovery.md

## 6) Security Controls
- Kubernetes policies + CI security scan:
  - infrastructure/kubernetes/base/security.yaml
  - .github/workflows/security-posture.yml

## 7) Release + Reliability Governance
- Progressive deployment and SLO gates:
  - .github/workflows/progressive-deploy.yml
  - scripts/ops/deploy_env.sh
  - scripts/ops/slo_gate.sh

## 8) Operations and Incident Response
- Runbooks:
  - infrastructure/runbooks/incident_response.md
  - infrastructure/runbooks/worker_backlog.md
  - infrastructure/runbooks/deployment_execution.md

## Quick Start (Code Path)
1. Copy and fill Terraform inputs:
   - cp infrastructure/terraform/environments/dev/terraform.tfvars.example infrastructure/terraform/environments/dev/terraform.tfvars
   - cp infrastructure/terraform/environments/staging/terraform.tfvars.example infrastructure/terraform/environments/staging/terraform.tfvars
   - cp infrastructure/terraform/environments/prod/terraform.tfvars.example infrastructure/terraform/environments/prod/terraform.tfvars
2. Copy and fill runtime secrets:
   - cp infrastructure/secrets/runtime.env.example infrastructure/secrets/runtime.env
3. Bootstrap cloud + cluster base:
   - make bootstrap-dev
   - make bootstrap-staging
   - make bootstrap-prod
4. Apply runtime secrets:
   - make apply-runtime-secret
5. Deploy workloads:
   - make deploy-dev
   - make deploy-staging
   - make deploy-prod
