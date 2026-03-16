from abc import ABC, abstractmethod
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

    def connect(self) -> bool:  # type: ignore[override]
        return True

    def fetch_historical(self, artist_id: str, start_date, end_date) -> list[dict]:  # type: ignore[override]
        return []

    def fetch_recent(self, artist_id: str, since) -> list[dict]:  # type: ignore[override]
        return []

    def normalize(self, raw_data: list[dict]) -> list[dict]:  # type: ignore[override]
        return raw_data

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        pass

    @abstractmethod
    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        pass

    @abstractmethod
    def normalize(self, raw_data: list[dict]) -> list[dict]:
        pass
