PYTHON ?= /usr/bin/python3
UVICORN ?= uvicorn

.PHONY: install run test lint migrate-up migrate-down openapi api-reference docs-check sdk-python sdk-typescript sdks seed up down worker beat

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(UVICORN) XR7.api.app:app --reload

test:
	$(PYTHON) -m pytest tests -v

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

worker:
	celery -A XR7.celery_app:celery_app worker --loglevel=INFO

beat:
	celery -A XR7.celery_app:celery_app beat --loglevel=INFO
