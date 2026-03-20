#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-xr7}"
ENV_FILE="${2:-}"

if [[ -z "${ENV_FILE}" || ! -f "${ENV_FILE}" ]]; then
  echo "usage: $0 [namespace] <runtime.env>"
  exit 1
fi

echo "[secrets] applying xr7-runtime-secrets to namespace ${NAMESPACE}"
kubectl -n "${NAMESPACE}" create secret generic xr7-runtime-secrets \
  --from-env-file="${ENV_FILE}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "[secrets] applied"
