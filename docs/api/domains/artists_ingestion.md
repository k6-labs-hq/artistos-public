# Artists + Ingestion Domain

## Artist Endpoints
- POST /artists/
- GET /artists/{artist_id}
- GET /artists/{artist_id}/summary
- POST /artists/{artist_id}/connect

## Onboarding Endpoints
- GET /artists/{artist_id}/onboarding/status
- POST /artists/{artist_id}/ingestion/upload-any
- POST /artists/{artist_id}/fetchers/{integration}
- Sync job lifecycle endpoints under /artists/{artist_id}/sync/jobs

## Ingestion Endpoints
- GET /ingestion/supported-formats
- POST /artists/{artist_id}/statements/upload
- POST /artists/{artist_id}/statements/upload-batch
- GET /artists/{artist_id}/statements
- GET /artists/{artist_id}/statements/{statement_id}

## Example cURL
```bash
curl -X POST http://localhost:8000/artists/{id}/statements/upload \
  -F "file=@statement.csv"
```
