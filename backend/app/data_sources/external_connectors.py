import re
from typing import Dict, Any
import pandas as pd
from app.data_sources.base import DataSourceConnector

class GoogleSheetsConnector(DataSourceConnector):
    def connect(self) -> bool:
        url = self.config.get("url", "")
        self.is_connected = bool(url and ("docs.google.com/spreadsheets" in url))
        return self.is_connected

    def validate_connection(self) -> Dict[str, Any]:
        url = self.config.get("url", "")
        if not url:
            return {"valid": False, "message": "Google Sheets URL is required."}
        if "docs.google.com/spreadsheets" not in url:
            return {"valid": False, "message": "Invalid Google Sheets URL format."}
        try:
            # Extract sheet ID
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
            if not match:
                return {"valid": False, "message": "Could not parse Google Sheet ID from URL."}
            sheet_id = match.group(1)
            csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            # Try reading a few rows
            pd.read_csv(csv_export_url, nrows=5)
            return {"valid": True, "message": "Google Sheet connected and accessible!"}
        except Exception as e:
            return {"valid": False, "message": f"Unable to fetch Google Sheet. Ensure sheet is set to 'Anyone with link can view'. Detail: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        url = self.config.get("url", "")
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            sheet_id = match.group(1)
            csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            return pd.read_csv(csv_export_url)
        raise ValueError("Invalid Google Sheets URL")

    def get_schema(self) -> Dict[str, str]:
        df = self.load_data()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

class PostgreSQLConnector(DataSourceConnector):
    def connect(self) -> bool:
        uri = self.config.get("connection_uri", "")
        return bool(uri and ("postgresql" in uri))

    def validate_connection(self) -> Dict[str, Any]:
        uri = self.config.get("connection_uri", "")
        if not uri:
            return {"valid": False, "message": "PostgreSQL connection URI is required (e.g. postgresql://user:pass@host:5432/dbname)."}
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(uri, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"valid": True, "message": "Connected to PostgreSQL database successfully!"}
        except Exception as e:
            return {"valid": False, "message": f"PostgreSQL connection failed: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        uri = self.config.get("connection_uri", "")
        query = self.config.get("query", "")
        table = self.config.get("table", "")
        from sqlalchemy import create_engine
        engine = create_engine(uri)
        if query:
            return pd.read_sql_query(query, engine)
        elif table:
            return pd.read_sql_table(table, engine)
        raise ValueError("Specify either 'table' or 'query' to load data from PostgreSQL.")

    def get_schema(self) -> Dict[str, str]:
        df = self.load_data()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

class MySQLConnector(DataSourceConnector):
    def connect(self) -> bool:
        uri = self.config.get("connection_uri", "")
        return bool(uri and ("mysql" in uri))

    def validate_connection(self) -> Dict[str, Any]:
        uri = self.config.get("connection_uri", "")
        if not uri:
            return {"valid": False, "message": "MySQL connection URI is required (e.g. mysql+pymysql://user:pass@host:3306/dbname)."}
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(uri, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"valid": True, "message": "Connected to MySQL database successfully!"}
        except Exception as e:
            return {"valid": False, "message": f"MySQL connection failed: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        uri = self.config.get("connection_uri", "")
        query = self.config.get("query", "")
        table = self.config.get("table", "")
        from sqlalchemy import create_engine
        engine = create_engine(uri)
        if query:
            return pd.read_sql_query(query, engine)
        elif table:
            return pd.read_sql_table(table, engine)
        raise ValueError("Specify either 'table' or 'query' to load data from MySQL.")

    def get_schema(self) -> Dict[str, str]:
        df = self.load_data()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

class MongoDBConnector(DataSourceConnector):
    def connect(self) -> bool:
        uri = self.config.get("uri", "")
        return bool(uri and ("mongodb" in uri))

    def validate_connection(self) -> Dict[str, Any]:
        uri = self.config.get("uri", "")
        if not uri:
            return {"valid": False, "message": "MongoDB connection URI is required (e.g. mongodb://localhost:27017)."}
        try:
            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            return {"valid": True, "message": "Connected to MongoDB successfully!"}
        except Exception as e:
            return {"valid": False, "message": f"MongoDB connection failed: {str(e)}"}

    def load_data(self) -> pd.DataFrame:
        uri = self.config.get("uri", "")
        db_name = self.config.get("database", "")
        coll_name = self.config.get("collection", "")
        from pymongo import MongoClient
        client = MongoClient(uri)
        db = client[db_name]
        coll = db[coll_name]
        docs = list(coll.find().limit(5000))
        if not docs:
            return pd.DataFrame()
        df = pd.DataFrame(docs)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)
        return df

    def get_schema(self) -> Dict[str, str]:
        df = self.load_data()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}
