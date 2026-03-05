# Recovery Intelligence Backlog

This document defines four deliverables to move ArtistOS toward a best-in-class AI/ML leakage detector.

## 1) New Models and Schemas Added

Implemented in `XR7/models/recovery_intelligence.py`:

- `RoyaltyLedgerEntry`
: Statement-line canonical ledger with lineage fields (`source_file`, `source_row`, `contract_version`, `fx_rate_used`, `ingested_at`).

- `ContractTermSnapshot`
: Parsed contract terms with confidence and effective dates for versioned expected-payout logic.

- `RecoveryOutcomeFeedback`
: Human outcome loop storage (`DISMISSED`, `FILED`, `SETTLED`, `RECOVERED`) to train ranking and confidence calibration later.

Associated schemas:
- `RoyaltyLedgerEntryCreate`, `RoyaltyLedgerEntrySchema`
- `ContractTermSnapshotSchema`
- `RecoveryOutcomeFeedbackCreate`, `RecoveryOutcomeFeedbackSchema`

## 2) Exact API Endpoints Added

Implemented in `XR7/api/routers/intelligence.py` and registered in `XR7/api/app.py`.

- `POST /artists/{artist_id}/intelligence/ledger/ingest`
: Ingest canonical ledger rows with source lineage.

- `POST /artists/{artist_id}/intelligence/contracts/extract`
: Extract term snapshots from contract text and persist with confidence.

- `POST /artists/{artist_id}/intelligence/simulate-expected-payout`
: Simulate expected payout from usage/rates and compute variance vs received.

- `POST /artists/{artist_id}/intelligence/feedback`
: Record analyst/ops outcomes for anomaly/claim lifecycle learning.

- `POST /artists/{artist_id}/intelligence/rank-utility`
: Rank actions by expected utility (`recoverable * success_prob - effort_cost`).

## 3) First Three Model Classes Implemented

Implemented in `XR7/ml/`:

- `ContractTermExtractor` (`contract_term_extractor.py`)
: Rule-based extraction for royalty rate, territory, and recoupment clause signals.

- `ExpectedPayoutSimulator` (`expected_payout_simulator.py`)
: Computes expected totals from usage rows and rates, plus variance and variance %.

- `RecoveryUtilityRanker` (`recovery_utility_ranker.py`)
: Produces expected-utility ranking for triage and action queues.

## 4) Test Plan and Starter Coverage

### Test Plan

Functional tests:
- Happy-path and artist-not-found coverage for all 5 intelligence endpoints.
- Ledger ingestion persistence and schema validation.
- Contract extraction deterministic outputs for representative clause text.
- Payout simulation variance correctness with mixed rate inputs.
- Utility ranking order correctness and stable ties behavior.
- Feedback persistence and enum validation.

Model tests:
- `ContractTermExtractor` regex robustness and dedupe behavior.
- `ExpectedPayoutSimulator` edge cases (zero quantities, no received amount).
- `RecoveryUtilityRanker` ranking monotonicity and effort-cost sensitivity.

Data quality tests:
- Reject malformed ledger rows (missing source/record_type).
- Ensure confidence values remain bounded [0, 1] where expected.

### Suggested Acceptance Criteria (Phase 1)

- All intelligence endpoints return deterministic JSON contracts and `404` on unknown artist.
- Contract extraction stores snapshots with confidence and effective dates.
- Utility rank endpoint returns sorted items with `utility_rank` starting at 1.
- Ledger entries preserve source lineage for claim evidence traceability.

## Next Build Priorities (Phase 2)

1. Add true contract NLP parser for PDFs + OCR pipeline.
2. Attach simulator to real contract terms and territory-specific rates.
3. Train utility model from `RecoveryOutcomeFeedback` outcomes.
4. Add calibration metrics dashboard (precision@k, recovered USD per analyst hour).
