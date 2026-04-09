from abc import ABC
from datetime import datetime


class BaseConnector(ABC):
    def __init__(self, config: dict):
        self.config = config


# Alias used by newer connectors that follow the IngestionConnector naming convention.
# Sub-classes may implement only the async methods relevant to their data source;
# the abstract methods of BaseConnector carry optional no-op defaults below.
class IngestionConnector(BaseConnector):
    """Relaxed base class for connectors that do not implement the full
    synchronous historical/recent/normalize protocol.  Subclasses only
    need to override the methods they support."""

    def connect(self) -> bool:
        return True

    def fetch_historical(
        self, artist_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        return []

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        return []

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        return raw_data
