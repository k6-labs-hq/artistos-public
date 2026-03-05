from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector


class IngestionPipeline:
    def __init__(self, db_session, connectors: list[BaseConnector]):
        self.db_session = db_session
        self.connectors = connectors

    def run_historical_ingestion(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        all_records = []
        for connector in self.connectors:
            raw = connector.fetch_historical(artist_id, start_date, end_date)
            processed = self.process_batch(connector, raw)
            all_records.extend(processed)
        return all_records

    def run_ongoing_ingestion(self, artist_id: str, since: datetime) -> list[dict]:
        all_records = []
        for connector in self.connectors:
            raw = connector.fetch_recent(artist_id, since)
            processed = self.process_batch(connector, raw)
            all_records.extend(processed)
        return all_records

    def process_batch(self, connector: BaseConnector, raw_records: list[dict]) -> list[dict]:
        return connector.normalize(raw_records)
