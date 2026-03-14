#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT_DIR/scripts/export_openapi.py"
"$ROOT_DIR/scripts/generate_sdk_python.sh"
"$ROOT_DIR/scripts/generate_sdk_typescript.sh"

echo "All SDKs generated under $ROOT_DIR/sdk"
