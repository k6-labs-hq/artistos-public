#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/verify_evidence.sh --claim-id <id> [options]

Required:
  --claim-id <id>                 Claim ID to verify

Options:
  --base-url <url>                API base URL (default: http://localhost:8000)
  --expected-prior-hash <hash>    Require prior chain link match
  --output-dir <path>             Directory for verification artifact JSON (default: ./artifacts/evidence)
  --timeout <seconds>             Curl timeout in seconds (default: 20)
  --help                          Show this help

Exit codes:
  0 = verification passed
  1 = verification failed or invalid response
USAGE
}

CLAIM_ID=""
BASE_URL="http://localhost:8000"
EXPECTED_PRIOR_HASH=""
OUTPUT_DIR="./artifacts/evidence"
TIMEOUT_SECONDS="20"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claim-id)
      CLAIM_ID="${2:-}"
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

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="${OUTPUT_DIR%/}/verify_${CLAIM_ID}_${TS}.json"

URL="${BASE_URL%/}/claims/${CLAIM_ID}/evidence/verify"
if [[ -n "$EXPECTED_PRIOR_HASH" ]]; then
  URL="${URL}?expected_prior_packet_hash=${EXPECTED_PRIOR_HASH}"
fi

HTTP_BODY_FILE="$(mktemp)"
HTTP_CODE="$(curl -sS --max-time "$TIMEOUT_SECONDS" -w "%{http_code}" -o "$HTTP_BODY_FILE" "$URL")"
BODY_CONTENT="$(cat "$HTTP_BODY_FILE")"
rm -f "$HTTP_BODY_FILE"

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "$BODY_CONTENT" > "$OUT_FILE"
  echo "Verification API call failed with HTTP $HTTP_CODE. Response archived at $OUT_FILE" >&2
  exit 1
fi

if ! printf '%s' "$BODY_CONTENT" | python3 - <<'PY'
import json
import sys

raw = sys.stdin.read()
try:
    data = json.loads(raw)
except Exception:
    print("invalid_json")
    sys.exit(1)

checks = data.get("checks", {})
required = ["packet_hash_matches", "chain_hash_matches", "line_hashes_match", "signature_valid"]
missing = [k for k in required if k not in checks]
if missing:
    print(f"missing_checks:{','.join(missing)}")
    sys.exit(1)

if data.get("valid") is not True:
    print("valid_false")
    sys.exit(1)

for key in required:
    if checks.get(key) is not True:
        print(f"check_failed:{key}")
        sys.exit(1)

if "prior_link_matches" in checks and checks.get("prior_link_matches") is not True:
    print("check_failed:prior_link_matches")
    sys.exit(1)

print("ok")
PY
then
  echo "$BODY_CONTENT" > "$OUT_FILE"
  echo "Evidence verification FAILED for claim $CLAIM_ID. Details archived at $OUT_FILE" >&2
  exit 1
fi

printf '%s\n' "$BODY_CONTENT" > "$OUT_FILE"

echo "Evidence verification PASSED for claim $CLAIM_ID"
echo "Artifact: $OUT_FILE"
