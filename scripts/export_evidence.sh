#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/export_evidence.sh --claim-id <id> [options]

Required:
  --claim-id <id>                 Claim ID to export

Options:
  --format <zip|pdf>              Export format (default: zip)
  --base-url <url>                API base URL (default: http://localhost:8000)
  --expected-prior-hash <hash>    Require chain-link match during verification
  --refresh                        Force evidence packet regeneration before export
  --output-dir <path>             Output directory for exports (default: ./artifacts/evidence)
  --timeout <seconds>             Curl timeout in seconds (default: 30)
  --help                          Show this help

Behavior:
  1) Runs scripts/verify_evidence.sh with strict pass/fail gating.
  2) Exports evidence only if verification passes.

Exit codes:
  0 = verification passed and export succeeded
  1 = verification failed, export failed, or invalid input
USAGE
}

CLAIM_ID=""
FORMAT="zip"
BASE_URL="http://localhost:8000"
EXPECTED_PRIOR_HASH=""
REFRESH="false"
OUTPUT_DIR="./artifacts/evidence"
TIMEOUT_SECONDS="30"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claim-id)
      CLAIM_ID="${2:-}"
      shift 2
      ;;
    --format)
      FORMAT="${2:-}"
      shift 2
      ;;
    --base-url)
      BASE_URL="${2:-}"
      shift 2
      ;;
    --expected-prior-hash)
      EXPECTED_PRIOR_HASH="${2:-}"
      shift 2
      ;;
    --refresh)
      REFRESH="true"
      shift 1
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --timeout)
      TIMEOUT_SECONDS="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$CLAIM_ID" ]]; then
  echo "Error: --claim-id is required" >&2
  usage
  exit 1
fi

if [[ "$FORMAT" != "zip" && "$FORMAT" != "pdf" ]]; then
  echo "Error: --format must be 'zip' or 'pdf'" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_SCRIPT="${SCRIPT_DIR}/verify_evidence.sh"
if [[ ! -x "$VERIFY_SCRIPT" ]]; then
  echo "Error: verify helper not found/executable: $VERIFY_SCRIPT" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EXT="$FORMAT"
OUT_FILE="${OUTPUT_DIR%/}/evidence_${CLAIM_ID}_${TS}.${EXT}"

VERIFY_ARGS=(--claim-id "$CLAIM_ID" --base-url "$BASE_URL" --output-dir "$OUTPUT_DIR" --timeout "$TIMEOUT_SECONDS")
if [[ -n "$EXPECTED_PRIOR_HASH" ]]; then
  VERIFY_ARGS+=(--expected-prior-hash "$EXPECTED_PRIOR_HASH")
fi

"$VERIFY_SCRIPT" "${VERIFY_ARGS[@]}"

URL="${BASE_URL%/}/claims/${CLAIM_ID}/evidence/export?format=${FORMAT}"
if [[ "$REFRESH" == "true" ]]; then
  URL="${URL}&refresh=true"
fi

HTTP_CODE="$(curl -sS -L --max-time "$TIMEOUT_SECONDS" -w "%{http_code}" -o "$OUT_FILE" "$URL")"
if [[ "$HTTP_CODE" != "200" ]]; then
  ERR_COPY="${OUT_FILE}.error.txt"
  cp "$OUT_FILE" "$ERR_COPY" || true
  rm -f "$OUT_FILE"
  echo "Export failed with HTTP $HTTP_CODE. Error body archived at $ERR_COPY" >&2
  exit 1
fi

echo "Evidence export PASSED for claim $CLAIM_ID"
echo "Export file: $OUT_FILE"
