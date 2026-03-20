#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-xr7}"
ENV_FILE="${2:-}"

if [[ -z "${ENV_FILE}" || ! -f "${ENV_FILE}" ]]; then
  echo "usage: $0 [namespace] <runtime.env> [ghcr_username] [ghcr_token]"
  exit 1
fi

GHCR_USERNAME="${3:-}"
GHCR_TOKEN="${4:-}"

echo "[secrets] applying xr7-runtime-secrets to namespace ${NAMESPACE}"
kubectl -n "${NAMESPACE}" create secret generic xr7-runtime-secrets \
  --from-env-file="${ENV_FILE}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create GHCR image pull secret if credentials provided
if [[ -n "${GHCR_USERNAME}" && -n "${GHCR_TOKEN}" ]]; then
  echo "[secrets] creating GHCR image pull secret"
  kubectl -n "${NAMESPACE}" create secret docker-registry ghcr-io-credentials \
    --docker-server=ghcr.io \
    --docker-username="${GHCR_USERNAME}" \
    --docker-password="${GHCR_TOKEN}" \
    --docker-email=noreply@github.com \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "[secrets] GHCR pull secret created"
fi

echo "[secrets] applied"
