# Infrastructure Acceleration Pack

This directory implements an immediate platform expansion across eight tracks.

## 1) Environment Ladder
- Terraform environment roots:
  - infrastructure/terraform/environments/dev
  - infrastructure/terraform/environments/staging
  - infrastructure/terraform/environments/prod

## 2) Kubernetes Runtime
- Base manifests for API, worker, scheduler, ingress, HPA, and backup cron:
  - infrastructure/kubernetes/base

## 3) Infrastructure as Code
- Reusable Terraform platform module:
  - infrastructure/terraform/modules/platform

## 4) Observability
- OpenTelemetry collector config, Prometheus SLO rules, Grafana dashboard:
  - infrastructure/observability

## 5) Data Reliability + DR
- Daily backup cron and restore drill scripts:
  - infrastructure/kubernetes/base/backup-cronjob.yaml
  - scripts/ops/restore_drill.sh
  - infrastructure/runbooks/disaster_recovery.md

## 6) Security Controls
- Network policies + pod security labels + CI security workflow:
  - infrastructure/kubernetes/base/security.yaml
  - .github/workflows/security-posture.yml

## 7) Release + Reliability Governance
- Progressive deploy workflow with SLO gate:
  - .github/workflows/progressive-deploy.yml
  - scripts/ops/slo_gate.sh

## 8) Operations and Incident Response
- Incident + backlog runbooks:
  - infrastructure/runbooks/incident_response.md
  - infrastructure/runbooks/worker_backlog.md

## Quick Start
1. Copy terraform.tfvars.example in each environment and fill real values.
2. Apply Terraform per environment.
3. Create runtime secret `xr7-runtime-secrets` in target namespace.
4. Apply Kubernetes manifests.
5. Use workflow_dispatch for progressive deploy in GitHub Actions.
