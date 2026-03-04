# ARCOS7 Engine 2 — Artist Earnings Accuracy Platform

ARCOS7 Engine 2 is a comprehensive platform designed to detect, recover, and prevent earning discrepancies for artists across all revenue streams — streaming royalties, touring settlements, merchandise royalties, sync licensing, brand partnerships, and platform payments.

## Features

- **Multi-Source Ingestion**: Connects to PROs (ASCAP, BMI, SESAC, GEMA, PRS), DSPs (Spotify, Apple Music, Tidal), ticketing platforms (Ticketmaster, AXS), and content platforms (YouTube, TikTok)
- **Rights Graph**: NetworkX-powered directed graph mapping artists, works, and contracts
- **Earnings Engine**: Reconstructs historical earnings and computes real-time expected payments against contract terms
- **Anomaly Detection**: Rule-based detection for royalty underpayments, touring settlement gaps, merch royalty omissions, sync licensing violations, and low platform rates
- **Claims Orchestration**: Full lifecycle management from identification through payment recovery
- **Billing Engine**: 10% contingency fee model with invoice generation and billing summaries
- **REST API**: FastAPI-powered endpoints for all platform operations

## Architecture

```
arcos7/
├── models/         # SQLAlchemy ORM models + Pydantic schemas
├── ingestion/      # Data pipeline + connector stubs (PRO, DSP, Ticketing, Platform)
├── graph/          # Rights graph (NetworkX DiGraph)
├── earnings/       # Earnings calculation and historical reconstruction
├── anomaly/        # Anomaly detection engine + rule modules
├── recovery/       # Claims lifecycle orchestration
├── billing/        # Contingency billing and invoice management
└── api/            # FastAPI application and routers
```

## Setup

### Requirements

- Python 3.11+

### Installation

```bash
pip install -r requirements.txt
```

### Running the API

```bash
uvicorn arcos7.api.app:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/artists/` | Create artist |
| GET | `/artists/{id}` | Get artist |
| GET | `/artists/{id}/summary` | Earnings + anomaly summary |
| POST | `/artists/{id}/connect` | Trigger historical ingestion |
| GET | `/artists/{id}/earnings` | Earnings summary |
| GET | `/artists/{id}/earnings/history` | Earnings history |
| POST | `/artists/{id}/earnings/reconstruct` | Reconstruct earnings for date range |
| GET | `/artists/{id}/anomalies` | List anomalies |
| POST | `/artists/{id}/anomalies/detect` | Run anomaly detection |
| GET | `/anomalies/{id}` | Get anomaly detail |
| GET | `/artists/{id}/claims` | List claims |
| GET | `/claims/{id}` | Get claim detail |
| POST | `/claims/{id}/advance` | Advance claim status |
| POST | `/claims/{id}/evidence` | Generate evidence packet |
| POST | `/claims/{id}/reconcile` | Reconcile recovered amount |
| GET | `/artists/{id}/billing` | Billing summary |
| GET | `/artists/{id}/invoices` | List invoices |

## License

Proprietary — ARCOS7 Engine 2
