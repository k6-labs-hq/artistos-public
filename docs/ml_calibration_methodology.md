# ML Calibration Methodology

XR7 calibration health combines event outcomes and model reliability signals.

## Inputs
- feedback events
- anomaly outcomes
- claim progression outcomes
- payout reconciliation state

## Outputs
- posterior_success_rate
- credible confidence bounds
- calibration health artifacts surfaced in dashboard/intelligence APIs

## Automation
- CalibrationAgent updates state-level calibration after workflow execution.
- Pipeline tasks aggregate feedback across artist scope.

## Endpoint Surface
- GET /artists/{artist_id}/intelligence/calibration
- POST /artists/{artist_id}/intelligence/feedback
- GET /artists/{artist_id}/intelligence/feedback/events
