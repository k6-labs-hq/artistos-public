# XR7 Documentation Index by Use Case

This index is organized by decision path so you can quickly find the right document for your goal.

## 1) Start Here: What are you trying to do?

- If you need the system architecture big picture:
  - [architecture_overview.md](architecture_overview.md)
  - [final_architecture_summary.md](final_architecture_summary.md)
  - [architecture_diagrams.md](architecture_diagrams.md)

- If you are building, changing, or running code:
  - [developer_onboarding.md](developer_onboarding.md)
  - [handbook.md](handbook.md)
  - [naming_convention_standard.md](naming_convention_standard.md)
  - [code_review_checklist.md](code_review_checklist.md)

- If you need API contracts and endpoint behavior:
  - [api/reference.md](api/reference.md)
  - [openapi_maintenance_guide.md](openapi_maintenance_guide.md)
  - [xr7_api_contract_diffs_and_scaffolds.md](xr7_api_contract_diffs_and_scaffolds.md)

- If you need deployment, infra, reliability, or CI/CD:
  - [production_deployment_guide.md](production_deployment_guide.md)
  - [cicd_pipeline_reference.md](cicd_pipeline_reference.md)
  - [container_registry_deployment_guide.md](container_registry_deployment_guide.md)
  - [disaster_recovery_backup_strategy.md](disaster_recovery_backup_strategy.md)

- If you need security, compliance, and incident handling:
  - [security_threat_model.md](security_threat_model.md)
  - [security_hardening_plan.md](security_hardening_plan.md)
  - [dependency_supply_chain_security.md](dependency_supply_chain_security.md)
  - [data_retention_privacy_compliance.md](data_retention_privacy_compliance.md)
  - [incident_response_runbook_index.md](incident_response_runbook_index.md)
  - [evidence_security_runbook.md](evidence_security_runbook.md)

- If you need product and roadmap context:
  - [product_expansion_backlog.md](product_expansion_backlog.md)
  - [recovery_intelligence_backlog.md](recovery_intelligence_backlog.md)
  - [roadmap_prioritization_rationale.md](roadmap_prioritization_rationale.md)
  - [market_readiness_audit_2026-03-16.md](market_readiness_audit_2026-03-16.md)

## 2) Decision Tree

## A. Are you making an architecture decision?

- Need current architecture state:
  - [architecture_overview.md](architecture_overview.md)
  - [architecture_diagrams.md](architecture_diagrams.md)
- Need acceptance criteria or review gate:
  - [architecture_acceptance_checklist.md](architecture_acceptance_checklist.md)
  - [code_review_checklist.md](code_review_checklist.md)
- Need target-state plan:
  - [microservices_migration_plan.md](microservices_migration_plan.md)
  - [enterprise_edition_architecture.md](enterprise_edition_architecture.md)
  - [multi_tenancy_isolation_model.md](multi_tenancy_isolation_model.md)

## B. Are you implementing API/backend behavior?

- Need API docs and domain contracts:
  - [api/reference.md](api/reference.md)
  - [api/domains/artists_ingestion.md](api/domains/artists_ingestion.md)
  - [api/domains/anomalies_claims_recovery.md](api/domains/anomalies_claims_recovery.md)
  - [api/domains/intelligence_dashboard_workflow.md](api/domains/intelligence_dashboard_workflow.md)
  - [api/domains/billing_trolley_widget_admin.md](api/domains/billing_trolley_widget_admin.md)
- Need async and workflow orchestration:
  - [celery_workflows.md](celery_workflows.md)
  - [langgraph_orchestrator.md](langgraph_orchestrator.md)
  - [langgraph_agent_devops.md](langgraph_agent_devops.md)

## C. Are you working on data, schema, or migrations?

- Need current schema and migration process:
  - [database_schema_and_migrations.md](database_schema_and_migrations.md)
  - [xr7_database_migration_rollout_plan.md](xr7_database_migration_rollout_plan.md)
  - [data_model_evolution_plan.md](data_model_evolution_plan.md)
- Need ingestion and lineage guidance:
  - [ingestion_format_catalog.md](ingestion_format_catalog.md)
  - [data_lineage_provenance_tracking.md](data_lineage_provenance_tracking.md)
  - [partner_distributor_integration_guide.md](partner_distributor_integration_guide.md)
  - [partner_integration_architecture.md](partner_integration_architecture.md)

## D. Are you working on claims, anomalies, and recovery logic?

- Need anomaly and claim behavior:
  - [anomaly_rule_catalog.md](anomaly_rule_catalog.md)
  - [claims_state_machine.md](claims_state_machine.md)
  - [sol_jurisdiction_reference.md](sol_jurisdiction_reference.md)
- Need finance/recovery policy:
  - [billing_contingency_fee_model.md](billing_contingency_fee_model.md)
  - [analyst_gated_recovery_advance_system.md](analyst_gated_recovery_advance_system.md)

## E. Are you working on dashboard and artist UX?

- Need UX and dashboard contracts:
  - [artist_facing_ux_flow.md](artist_facing_ux_flow.md)
  - [dashboard_schema_reference.md](dashboard_schema_reference.md)
  - [support_slas_escalation_paths.md](support_slas_escalation_paths.md)
- Need white-label and enterprise presentation:
  - [white_label_deployment_guide.md](white_label_deployment_guide.md)
  - [enterprise_edition_architecture.md](enterprise_edition_architecture.md)

## F. Are you working on ML/AI behavior and governance?

- Need model behavior and calibration:
  - [ml_calibration_methodology.md](ml_calibration_methodology.md)
  - [ml_model_cards.md](ml_model_cards.md)
- Need AI governance and agent framework:
  - [ai_agent_governance_framework.md](ai_agent_governance_framework.md)
  - [ai_augmentation_roadmap.md](ai_augmentation_roadmap.md)
  - [soundcloud_agents_modules_catalog.md](soundcloud_agents_modules_catalog.md)

## G. Are you preparing operations, incidents, or launch readiness?

- Need observability and performance:
  - [observability_monitoring_handbook.md](observability_monitoring_handbook.md)
  - [observability_monitoring_stack.md](observability_monitoring_stack.md)
  - [performance_scalability_benchmarks.md](performance_scalability_benchmarks.md)
- Need runbooks and failure handling:
  - [incident_response_runbook_index.md](incident_response_runbook_index.md)
  - [trolley_failure_playbook.md](trolley_failure_playbook.md)
- Need launch/go-to-market readiness:
  - [production_deployment_guide.md](production_deployment_guide.md)
  - [demo_environment_sales_guide.md](demo_environment_sales_guide.md)
  - [gtm_technical_plan.md](gtm_technical_plan.md)

## H. Are you looking for planning and program execution artifacts?

- Master plans and execution boards:
  - [xr7_master_specification_2026_2027.md](xr7_master_specification_2026_2027.md)
  - [xr7_execution_epics_and_tickets.md](xr7_execution_epics_and_tickets.md)
  - [xr7_implementation_board.md](xr7_implementation_board.md)
  - [HANDOFF.md](HANDOFF.md)

## 3) Fast Paths by Persona

- New engineer:
  1. [developer_onboarding.md](developer_onboarding.md)
  2. [architecture_overview.md](architecture_overview.md)
  3. [api/reference.md](api/reference.md)
  4. [database_schema_and_migrations.md](database_schema_and_migrations.md)

- Platform/SRE engineer:
  1. [production_deployment_guide.md](production_deployment_guide.md)
  2. [cicd_pipeline_reference.md](cicd_pipeline_reference.md)
  3. [observability_monitoring_handbook.md](observability_monitoring_handbook.md)
  4. [incident_response_runbook_index.md](incident_response_runbook_index.md)

- Product/technical lead:
  1. [final_architecture_summary.md](final_architecture_summary.md)
  2. [product_expansion_backlog.md](product_expansion_backlog.md)
  3. [roadmap_prioritization_rationale.md](roadmap_prioritization_rationale.md)
  4. [market_readiness_audit_2026-03-16.md](market_readiness_audit_2026-03-16.md)

## 4) Maintenance Rule for This Index

Whenever a new top-level document is added under docs/, update this file by:

- Adding it to the most relevant use-case section.
- Adding a new branch in the decision tree if needed.
- Keeping links relative so they work in GitHub and local editors.
