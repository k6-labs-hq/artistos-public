PYTHON ?= /usr/bin/python3
UVICORN ?= uvicorn

.PHONY: install run dev frontend-dev frontend-build test lint migrate-up migrate-down openapi api-reference docs-check sdk-python sdk-typescript sdks seed up down docker-build worker beat check-runtime-stubs check-openapi-breaking update-completion install-git-hooks infra-plan-dev infra-plan-staging infra-plan-prod k8s-apply-base slo-gate restore-drill bootstrap-dev bootstrap-staging bootstrap-prod deploy-dev deploy-staging deploy-prod apply-runtime-secret enterprise-historical-analysis

BASE_REF ?= origin/main

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(UVICORN) XR7.api.app:app --reload

dev:
	docker compose up --build api worker postgres redis

frontend-dev:
	cd frontend && npm install && npm run dev

frontend-build:
	cd frontend && npm install && npm run build

test:
	$(PYTHON) -m pytest tests -v

check-runtime-stubs:
	$(PYTHON) scripts/ci/check_runtime_stubs.py

check-openapi-breaking:
	git show $(BASE_REF):openapi/openapi.json > /tmp/base_openapi.json
	$(PYTHON) scripts/ci/check_openapi_breaking.py /tmp/base_openapi.json openapi/openapi.json

lint:
	$(PYTHON) -m py_compile XR7/api/app.py

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

openapi:
	$(PYTHON) scripts/export_openapi.py

api-reference:
	$(PYTHON) scripts/generate_api_reference.py

docs-check: openapi api-reference
	git diff --exit-code -- openapi/openapi.json docs/api/reference.md

update-completion:
	$(PYTHON) scripts/update_completion.py

install-git-hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit

sdk-python:
	./scripts/generate_sdk_python.sh

sdk-typescript:
	./scripts/generate_sdk_typescript.sh

sdks:
	./scripts/generate_sdks.sh

seed:
	$(PYTHON) scripts/seed_data.py

up:
	docker compose up --build -d

down:
	docker compose down

docker-build:
	docker buildx build --load -t xr7:latest .
	docker image ls xr7:latest

worker:
	celery -A XR7.celery_app:celery_app worker --loglevel=INFO

beat:
	celery -A XR7.celery_app:celery_app beat --loglevel=INFO

infra-plan-dev:
	terraform -chdir=infrastructure/terraform/environments/dev init -backend=false
	terraform -chdir=infrastructure/terraform/environments/dev validate

infra-plan-staging:
	terraform -chdir=infrastructure/terraform/environments/staging init -backend=false
	terraform -chdir=infrastructure/terraform/environments/staging validate

infra-plan-prod:
	terraform -chdir=infrastructure/terraform/environments/prod init -backend=false
	terraform -chdir=infrastructure/terraform/environments/prod validate

k8s-apply-base:
	kubectl apply -k infrastructure/kubernetes/base

slo-gate:
	bash scripts/ops/slo_gate.sh

restore-drill:
	bash scripts/ops/restore_drill.sh

bootstrap-dev:
	bash scripts/ops/bootstrap_env.sh dev infrastructure/terraform/environments/dev/terraform.tfvars

bootstrap-staging:
	bash scripts/ops/bootstrap_env.sh staging infrastructure/terraform/environments/staging/terraform.tfvars

bootstrap-prod:
	bash scripts/ops/bootstrap_env.sh prod infrastructure/terraform/environments/prod/terraform.tfvars

deploy-dev:
	bash scripts/ops/deploy_env.sh dev dev xr7

deploy-staging:
	bash scripts/ops/deploy_env.sh staging staging xr7

deploy-prod:
	bash scripts/ops/deploy_env.sh prod latest xr7

apply-runtime-secret:
	bash scripts/ops/apply_runtime_secret.sh xr7 infrastructure/secrets/runtime.env

enterprise-historical-analysis:
	$(PYTHON) scripts/recovery/run_enterprise_historical_analysis.py --input scripts/recovery/examples/wme_historical_analysis_template.csv --organization "WME" --entity-type "Talent Agency"
