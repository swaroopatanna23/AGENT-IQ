from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd

class DataSourceConnector(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def validate_connection(self) -> Dict[str, Any]:
        """Returns { 'valid': bool, 'message': str }"""
        pass

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Returns DataFrame representing the source dataset"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, str]:
        """Returns mapping of column names to datatypes"""
        pass

    def preview(self, n: int = 5) -> list:
        df = self.load_data()
        return df.head(n).to_dict(orient="records")

    def close(self):
        self.is_connected = False
