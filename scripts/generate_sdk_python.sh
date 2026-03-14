#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_PATH="$ROOT_DIR/openapi/openapi.json"
OUT_DIR="$ROOT_DIR/sdk/python"

if [[ ! -f "$SPEC_PATH" ]]; then
  echo "OpenAPI spec not found at $SPEC_PATH. Run: python scripts/export_openapi.py" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

if command -v openapi-generator-cli >/dev/null 2>&1; then
  openapi-generator-cli generate \
    -i "$SPEC_PATH" \
    -g python \
    -o "$OUT_DIR" \
    --additional-properties=packageName=xr7_sdk,projectName=xr7-python-sdk
else
  docker run --rm \
    -v "$ROOT_DIR:/local" \
    openapitools/openapi-generator-cli generate \
    -i /local/openapi/openapi.json \
    -g python \
    -o /local/sdk/python \
    --additional-properties=packageName=xr7_sdk,projectName=xr7-python-sdk
fi

echo "Generated Python SDK at $OUT_DIR"
