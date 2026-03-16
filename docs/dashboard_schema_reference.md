# Dashboard Schema Reference

The dashboard payload merges computed earnings/recovery metrics with agent orchestration state.

## Core Sections
- leakage_discovered
- in_pursuit
- recovered_and_deposited
- balance_still_pursuing
- deadlines
- priority_actions
- catalog_health
- earnings_trend
- activity_feed

## Agent Orchestra Sections
- agent_orchestra_status: current_step, confidence, trace_url
- onboarding_progress: step counters and missing checklist
- comfort_messages: artist-facing progress reassurance
- portal_guidance: provider-specific statement retrieval instructions
- fast_track_claim: first quick-win claim details
- expected_earnings: baseline expected performance
- public_profile: social/distribution profile enrichment
- readiness_score: onboarding readiness metric
- ugc_opportunities: monetizable social use opportunities
- catalog_profile, split_conflicts, registration_actions, follow_up_actions

## Trace Endpoint
GET /artists/{artist_id}/agent-trace/{run_id} returns event-level graph trace data.
