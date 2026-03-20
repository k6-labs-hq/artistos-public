#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-}"
IMAGE_TAG="${2:-}"
NAMESPACE="${3:-xr7}"

if [[ -z "${ENVIRONMENT}" || -z "${IMAGE_TAG}" ]]; then
  echo "usage: $0 <dev|staging|prod> <image_tag> [namespace]"
  exit 1
fi

OVERLAY="infrastructure/kubernetes/overlays/${ENVIRONMENT}"
if [[ ! -d "${OVERLAY}" ]]; then
  echo "missing overlay: ${OVERLAY}"
  exit 1
fi

echo "[deploy] applying ${OVERLAY}"
kubectl apply -k "${OVERLAY}"

echo "[deploy] updating image tag ${IMAGE_TAG}"
kubectl -n "${NAMESPACE}" set image deployment/xr7-api api="ghcr.io/mkallberg21/artistos-api:${IMAGE_TAG}"
kubectl -n "${NAMESPACE}" set image deployment/xr7-worker worker="ghcr.io/mkallberg21/artistos-api:${IMAGE_TAG}"
kubectl -n "${NAMESPACE}" set image deployment/xr7-scheduler scheduler="ghcr.io/mkallberg21/artistos-api:${IMAGE_TAG}"

echo "[deploy] waiting for rollouts"
kubectl -n "${NAMESPACE}" rollout status deployment/xr7-api --timeout=300s
kubectl -n "${NAMESPACE}" rollout status deployment/xr7-worker --timeout=300s
kubectl -n "${NAMESPACE}" rollout status deployment/xr7-scheduler --timeout=300s

echo "[deploy] success"
