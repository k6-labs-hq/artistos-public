# White label deployment guide

## Purpose
This runbook defines the production baseline for **White label deployment guide** and replaces the previous scaffold with implementation-focused guidance.

## Code Anchors
- XR7/services/branding.py,XR7/api/routers/branding.py,tests/test_branding.py

## Operating Model
- Scope: production services, background tasks, data pipelines, and CI/CD automation that touch this domain.
- Owners: engineering lead, platform/on-call lead, and product owner for sign-off.
- Change control: all changes require tests, changelog updates, and CI green status before merge.

## Minimum Controls
- Define owners for this area\n- Add SLOs and alert thresholds\n- Add rollback and recovery procedures\n- Add quarterly audit cadence

## Validation Checklist
- Verify expected API behavior with targeted pytest suites in tests/.
- Verify schema and contract drift using:
  - python scripts/export_openapi.py
  - python scripts/generate_api_reference.py
  - python scripts/ci/check_openapi_breaking.py <base> openapi/openapi.json
- Verify runtime stub policy using: python scripts/ci/check_runtime_stubs.py

## Incident Procedure
- Detect: use test failures, workflow alerts, and service logs to identify impact scope.
- Contain: disable affected path via config or rollback to last known-good deployment.
- Recover: apply tested fix, run targeted + regression tests, redeploy, and verify SLIs.
- Review: capture root cause, customer impact, and prevention actions in docs/ and backlog.

## Release Gate
A release is considered market-ready for this domain only when:
- Functional tests pass.
- Security and compliance checks pass.
- Generated artifacts (OpenAPI and API reference) are in sync.
- Operational runbook steps are current and executable.
