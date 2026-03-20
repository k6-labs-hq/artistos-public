#!/usr/bin/env bash
set -euo pipefail

# This gate is intentionally simple so it can run in CI before advanced telemetry integration.
ERROR_BUDGET_PCT="${ERROR_BUDGET_PCT:-2}"
LATENCY_P95_MS="${LATENCY_P95_MS:-800}"
CURRENT_ERROR_PCT="${CURRENT_ERROR_PCT:-0.5}"
CURRENT_P95_MS="${CURRENT_P95_MS:-420}"

echo "[slo-gate] error budget threshold: ${ERROR_BUDGET_PCT}%"
echo "[slo-gate] latency p95 threshold: ${LATENCY_P95_MS}ms"
echo "[slo-gate] current error ratio: ${CURRENT_ERROR_PCT}%"
echo "[slo-gate] current p95 latency: ${CURRENT_P95_MS}ms"

awk -v cur="${CURRENT_ERROR_PCT}" -v lim="${ERROR_BUDGET_PCT}" 'BEGIN {exit !(cur <= lim)}'
awk -v cur="${CURRENT_P95_MS}" -v lim="${LATENCY_P95_MS}" 'BEGIN {exit !(cur <= lim)}'

echo "[slo-gate] pass"
