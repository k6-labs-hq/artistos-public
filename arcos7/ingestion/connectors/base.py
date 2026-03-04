from abc import ABC, abstractmethod
from datetime import datetime


class BaseConnector(ABC):
    def __init__(self, config: dict):
        self.config = config

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
