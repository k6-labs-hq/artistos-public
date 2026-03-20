# WME Day-0 Historical Analysis Playbook

This playbook is the fastest path to walk into William Morris Endeavor and run a full historical analysis across music plus TV/film clients.

## 1) What You Need Before the Meeting

- Agency roster export with one row per client and a vertical label: `MUSIC` or `TV_FILM`.
- Historical statement/export files per client (CSV/TSV/XLSX).
- Basic legal authorization/attestation for data review and claim preparation.
- Operator machine with XR7 runtime access and credentials.
- Named decision owners for legal escalation and payout routing.

## 2) Input Schema (Roster-Level Analysis)

Use this template:

- `scripts/recovery/examples/wme_historical_analysis_template.csv`

Minimum useful columns:

- `client`
- `vertical`
- `sol_risk`
- Any amount columns that exist for the client:
  - `estimated_missing`
  - `estimated_underpayment`
  - `estimated_backend_missing`
  - `estimated_royalty_gap`
  - `estimated_unpaid_performance`
  - `estimated_unpaid_sync`
  - `estimated_unpaid_neighboring`
  - `estimated_mechanical_gap`
  - `estimated_residual_gap`
  - `estimated_ugc_gap`

## 3) Run Tomorrow (No Custom Coding)

### Option A: CLI (fastest)

```bash
python scripts/recovery/run_enterprise_historical_analysis.py \
  --input path/to/wme_roster.csv \
  --organization "William Morris Endeavor" \
  --entity-type "Talent Agency" \
  --out-json artifacts/wme_historical_analysis.json \
  --out-md artifacts/wme_historical_analysis.md
```

Or run the built-in template:

```bash
make enterprise-historical-analysis
```

### Option B: API (for portal workflows)

- `POST /enterprise/historical/analyze` (JSON payload)
- `POST /enterprise/historical/analyze-file` (multipart with CSV/TSV)

## 4) What the Output Gives You

- Total estimated recoverable value across all submitted clients.
- Breakdown by vertical (`MUSIC`, `TV_FILM`).
- SOL risk distribution (`high`, `medium`, `low`, `unknown`).
- Ranked top clients by estimated recoverable value.
- Immediate execution plan for next 24h and 7d.

## 5) Day-0 Meeting Flow

1. Import roster-level data and run historical rollup in front of stakeholders.
2. Sort by `high SOL risk` and `highest recoverable` to define sprint-1 cohort.
3. Confirm legal routing and evidence standards for that cohort.
4. Begin ingestion + anomaly + claim packet workflows for priority clients.

## 6) Hard Limits (What Still Requires External Inputs)

- Direct API connector pull-through for some partners still needs partner credentials/approvals.
- Any client without historical exports can be onboarded, but analysis depth depends on available records.
- Legal outcomes depend on contract rights and jurisdiction, not just anomaly detection.
