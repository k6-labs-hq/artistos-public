# Intelligence, Dashboard, and Workflow Domain

## Intelligence Endpoints
- GET /artists/{artist_id}/intelligence/calibration
- POST /artists/{artist_id}/intelligence/ledger/ingest
- POST /artists/{artist_id}/intelligence/contracts/extract
- POST /artists/{artist_id}/intelligence/feedback
- GET /artists/{artist_id}/intelligence/feedback/events

## Dashboard Endpoints
- GET /dashboard/ui
- GET /artists/{artist_id}/dashboard
- GET /artists/{artist_id}/dashboard/flow
- GET /artists/{artist_id}/benchmarks
- GET /artists/{artist_id}/dashboard/export-guidance
- GET /artists/{artist_id}/agent-trace/{run_id}

## Workflow Endpoints
- POST /artists/{artist_id}/workflow/run-full-autonomous
- GET /artists/{artist_id}/workflow/runs/{run_id}

## Dashboard Agent Fields
- agent_orchestra_status
- onboarding_progress
- comfort_messages
- portal_guidance
- fast_track_claim
- expected_earnings
- public_profile
- readiness_score
- ugc_opportunities
- catalog_profile
- split_conflicts
- registration_actions
- follow_up_actions
