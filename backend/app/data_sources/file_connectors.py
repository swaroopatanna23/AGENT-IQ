import os
import json
import pandas as pd
from typing import Dict, Any
from app.data_sources.base import DataSourceConnector

class CSVConnector(DataSourceConnector):
    def connect(self) -> bool:
        path = self.config.get("file_path", "")
        self.is_connected = os.path.exists(path)
        return self.is_connected

    def validate_connection(self) -> Dict[str, Any]:
        path = self.config.get("file_path", "")
        if not path or not os.path.exists(path):
            return {"valid": False, "message": f"CSV file not found at path: {path}"}
        try:
            pd.read_csv(path, nrows=5)
            return {"valid": True, "message": "CSV file validated successfully"}
        except Exception as e:
            return {"valid": False, "message": f"Invalid CSV file: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        path = self.config.get("file_path", "")
        return pd.read_csv(path)

    def get_schema(self) -> Dict[str, str]:
        df = pd.read_csv(self.config.get("file_path", ""), nrows=10)
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

class ExcelConnector(DataSourceConnector):
    def connect(self) -> bool:
        path = self.config.get("file_path", "")
        self.is_connected = os.path.exists(path)
        return self.is_connected

    def validate_connection(self) -> Dict[str, Any]:
        path = self.config.get("file_path", "")
        if not path or not os.path.exists(path):
            return {"valid": False, "message": f"Excel file not found at path: {path}"}
        try:
            pd.read_excel(path, nrows=5)
            return {"valid": True, "message": "Excel file validated successfully"}
        except Exception as e:
            return {"valid": False, "message": f"Invalid Excel file: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        path = self.config.get("file_path", "")
        sheet = self.config.get("sheet_name", 0)
        return pd.read_excel(path, sheet_name=sheet)

    def get_schema(self) -> Dict[str, str]:
        df = pd.read_excel(self.config.get("file_path", ""), nrows=10)
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

class JSONConnector(DataSourceConnector):
    def connect(self) -> bool:
        path = self.config.get("file_path", "")
        self.is_connected = os.path.exists(path)
        return self.is_connected

    def validate_connection(self) -> Dict[str, Any]:
        path = self.config.get("file_path", "")
        if not path or not os.path.exists(path):
            return {"valid": False, "message": f"JSON file not found at path: {path}"}
        try:
            pd.read_json(path)
            return {"valid": True, "message": "JSON file validated successfully"}
        except Exception as e:
            return {"valid": False, "message": f"Invalid JSON file: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        path = self.config.get("file_path", "")
        return pd.read_json(path)

    def get_schema(self) -> Dict[str, str]:
        df = self.load_data()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}
