# Legacy Agent Archive

The previous multi-agent competitive orchestration layer has been retired.

These modules remain in the repository as implementation libraries for node logic and backward compatibility, but they are no longer orchestrated as independent top-level competing agents:

- onboarding_agents.py
- specialized_agents.py
- tvfilm_agents.py
- advance_recovery_agents.py

Runtime orchestration now routes through exactly two top-level agents:

- onboarding_preparation_graph.py
- recovery_execution_graph.py

The only top-level router is two_agent_orchestrator_graph.py, exposed via orchestrator.py compatibility wrappers.
