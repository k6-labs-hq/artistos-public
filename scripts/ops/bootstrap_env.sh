#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-}"
VARS_FILE="${2:-}"

if [[ -z "${ENVIRONMENT}" || -z "${VARS_FILE}" ]]; then
  echo "usage: $0 <dev|staging|prod> <terraform.tfvars>"
  exit 1
fi

TF_DIR="infrastructure/terraform/environments/${ENVIRONMENT}"
if [[ ! -d "${TF_DIR}" ]]; then
  echo "missing terraform environment directory: ${TF_DIR}"
  exit 1
fi

if [[ ! -f "${VARS_FILE}" ]]; then
  echo "missing vars file: ${VARS_FILE}"
  exit 1
fi

echo "[bootstrap] terraform init/apply for ${ENVIRONMENT}"
terraform -chdir="${TF_DIR}" init
terraform -chdir="${TF_DIR}" apply -var-file="${VARS_FILE}" -auto-approve

echo "[bootstrap] ensure namespace + baseline resources"
kubectl apply -f infrastructure/kubernetes/base/namespace.yaml

echo "[bootstrap] completed for ${ENVIRONMENT}"
