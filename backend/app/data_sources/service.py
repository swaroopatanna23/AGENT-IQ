import os
import io
import pandas as pd
from typing import BinaryIO, Union
from app.data_sources.file_connectors import CSVConnector, ExcelConnector, JSONConnector
from app.data_sources.external_connectors import (
    GoogleSheetsConnector, PostgreSQLConnector, MySQLConnector, MongoDBConnector
)

class DataInputService:
    @staticmethod
    def detect_file_type(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower().strip(".")
        if ext in ["csv"]:
            return "csv"
        elif ext in ["xlsx", "xls"]:
            return "excel"
        elif ext in ["json"]:
            return "json"
        else:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats: CSV, Excel, JSON.")

    @staticmethod
    def load_data(file_type: str, file_obj: Union[BinaryIO, str, bytes]) -> pd.DataFrame:
        """
        Loads data from file object or file path deterministically into a Pandas DataFrame.
        Directly implements Slide 10 DataInputService.load_data.
        """
        if isinstance(file_obj, str) and os.path.exists(file_obj):
            if file_type == "csv":
                return pd.read_csv(file_obj)
            elif file_type in ["excel", "xlsx", "xls"]:
                return pd.read_excel(file_obj)
            elif file_type == "json":
                return pd.read_json(file_obj)
        else:
            # File is an uploaded stream / bytes
            if hasattr(file_obj, "read"):
                content = file_obj.read()
                file_buffer = io.BytesIO(content)
            elif isinstance(file_obj, bytes):
                file_buffer = io.BytesIO(file_obj)
            else:
                raise ValueError("Invalid file object provided for loading.")

            if file_type == "csv":
                return pd.read_csv(file_buffer)
            elif file_type in ["excel", "xlsx", "xls"]:
                return pd.read_excel(file_buffer)
            elif file_type == "json":
                return pd.read_json(file_buffer)

        raise ValueError(f"Unable to load data for format '{file_type}'.")

    @staticmethod
    def get_connector(source_type: str, config: dict):
        mapping = {
            "csv": CSVConnector,
            "excel": ExcelConnector,
            "json": JSONConnector,
            "google_sheets": GoogleSheetsConnector,
            "postgresql": PostgreSQLConnector,
            "mysql": MySQLConnector,
            "mongodb": MongoDBConnector
        }
        connector_cls = mapping.get(source_type.lower())
        if not connector_cls:
            raise ValueError(f"Unknown data source type: '{source_type}'.")
        return connector_cls(config)
