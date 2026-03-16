# Ingestion Format Catalog

XR7 supports explicit and generic ingestion formats.

## Explicit Sources
- DistroKid
- TuneCore
- CD Baby
- Amuse
- United Masters
- ONErpm
- Stem
- LANDR
- Ditto Music
- ReverbNation
- Bandcamp
- ASCAP
- BMI
- Spotify for Artists

## Fallback
- Generic CSV with date/source/quantity/amount-compatible columns.

## Operational Endpoints
- GET /ingestion/supported-formats
- POST /artists/{artist_id}/statements/upload
- POST /artists/{artist_id}/statements/upload-batch

## Agent-Aware Ingestion
SmartUploadFixerAgent and FileClassifierAgent run pre-normalization and classification passes before downstream anomaly and claim processing.
