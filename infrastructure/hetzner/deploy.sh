#!/usr/bin/env bash
# One-command deploy for ArtistOS on Hetzner (CI-pushes model).
#
# Expects:
#   - docker-compose.prod.yml, Caddyfile in the same dir
#   - .env.<env> in the same dir (not committed; placed by CI or operator)
#
# Pulls the latest image from GHCR, runs migrations inside it, rolling restart.

set -euo pipefail

COMPOSE_FILE="$(cd "$(dirname "$0")" && pwd)/docker-compose.prod.yml"
ENV_NAME="${1:-qa}"
ENV_FILE="$(cd "$(dirname "$0")" && pwd)/.env.${ENV_NAME}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found." >&2
  exit 1
fi

# Load API_DOMAIN + APP_DOMAIN so Caddy picks them up.
# Legacy DOMAIN is still respected for backwards compat.
set -a; source "$ENV_FILE"; set +a
export API_DOMAIN APP_DOMAIN DOMAIN

echo "==> Pulling latest image for ${ENV_NAME}..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull api worker scheduler

echo "==> Running migrations..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm \
  -e PYTHONPATH=/app \
  api alembic upgrade head

echo "==> Rolling restart..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans

echo "==> Waiting for health..."
sleep 8
HEALTH_HOST="${API_DOMAIN:-${DOMAIN:-localhost}}"
if curl -fsS --max-time 10 "http://localhost:8000/health" >/dev/null 2>&1 || \
   curl -fsS --max-time 10 "https://${HEALTH_HOST}/health" >/dev/null 2>&1; then
  echo "Deploy OK for ${ENV_NAME}"
else
  echo "WARNING: health check failed; inspect 'docker compose logs api'" >&2
  exit 1
fi
