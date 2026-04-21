#!/usr/bin/env bash
# One-command deploy for ArtistOS on Hetzner.
# Run this on the VM after the first-time Terraform provisioning.

set -euo pipefail

COMPOSE_FILE="$(dirname "$0")/docker-compose.prod.yml"
ENV_FILE="$(dirname "$0")/.env.prod"

if [[ ! -f "$ENV_FILE" ]]; then
	echo "ERROR: $ENV_FILE not found. Copy .env.prod.example and populate it." >&2
	exit 1
fi

echo "==> Pulling latest image..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull api worker scheduler

echo "==> Running migrations..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm api alembic upgrade head

echo "==> Rolling restart..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans

echo "==> Health check..."
sleep 5
if curl -fsS --max-time 10 "https://${DOMAIN:-localhost}/health" >/dev/null 2>&1; then
	echo "Deploy OK — API healthy at https://${DOMAIN:-localhost}/health"
else
	echo "WARNING: health check failed; check 'docker compose logs api'" >&2
	exit 1
fi
