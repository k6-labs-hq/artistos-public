#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="${1:-}"
DB_URL="${DB_URL:-}"

if [[ -z "${BACKUP_FILE}" || -z "${DB_URL}" ]]; then
  echo "usage: DB_URL=<postgres-url> $0 <backup-file.sql.gz>"
  exit 1
fi

echo "[restore-drill] starting restore drill against ${DB_URL}"
gunzip -c "${BACKUP_FILE}" | psql "${DB_URL}"

echo "[restore-drill] restore completed"
