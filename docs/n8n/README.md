# XR7 n8n Workflow Blueprints

This directory contains **node-by-node n8n workflow blueprints** for every major orchestration flow in the XR7 engine. Each blueprint is self-contained and describes exactly which API endpoints to call, what inputs/outputs each node expects, and how to handle errors and retries.

## Blueprints in this directory

| File | Flow |
|---|---|
| `01_dsp_ingestion_pipeline.md` | DSP ingestion → normalization → matching → storage |
| `02_pro_reconciliation_pipeline.md` | PRO ingestion → reconciliation → discrepancy flagging |
| `03_mlc_metadata_alignment_pipeline.md` | MLC ingestion → metadata alignment → claim generation |
| `04_recovery_claim_export_pipeline.md` | Recovery pipeline → claim packaging → export |

## How to import into n8n

1. Open your n8n instance.
2. Go to **Workflows → Import from JSON**.
3. Paste the JSON payload from the `workflow_json` block in any blueprint.
4. Configure the `XR7_BASE_URL` credential to point at your running XR7 API.
5. Set `XR7_API_KEY` in n8n credentials store.

## Credential setup

Create a **Header Auth** credential in n8n named `XR7 API`:
- Header name: `X-API-Key`
- Header value: your `XR7_API_KEY` value

All HTTP Request nodes reference this credential by name.

## Environment variables expected by workflows

| n8n Variable | Maps to |
|---|---|
| `XR7_BASE_URL` | `https://your-xr7-api.internal` |
| `XR7_API_KEY` | Service account API key |
| `WEBHOOK_ERROR_CHANNEL` | Slack/webhook URL for error alerts |
