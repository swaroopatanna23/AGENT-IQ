from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User
from app.models.data_sources import DataSource
from app.auth.dependencies import get_current_user
from app.data_sources.service import DataInputService

router = APIRouter(prefix="/api/v1/data-sources", tags=["Data Sources"])

class ConnectorTestRequest(BaseModel):
    source_type: str
    config: Dict[str, Any]

@router.get("")
def list_connectors(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    configured_sources = db.query(DataSource).filter(DataSource.user_id == current_user.id).all()
    configured_map = {s.type: s for s in configured_sources}

    available_connectors = [
        {
            "id": "csv",
            "name": "CSV File",
            "category": "Files",
            "description": "Standard Comma Separated Values files (.csv)",
            "status": "available",
            "icon": "FileSpreadsheet"
        },
        {
            "id": "excel",
            "name": "Microsoft Excel",
            "category": "Files",
            "description": "Excel workbooks (.xlsx, .xls)",
            "status": "available",
            "icon": "FileSpreadsheet"
        },
        {
            "id": "json",
            "name": "JSON Dataset",
            "category": "Files",
            "description": "JavaScript Object Notation data files (.json)",
            "status": "available",
            "icon": "FileCode"
        },
        {
            "id": "google_sheets",
            "name": "Google Sheets",
            "category": "Cloud Spreadsheet",
            "description": "Live cloud spreadsheets via URL or Google Sheets API",
            "status": "configured" if "google_sheets" in configured_map else "available",
            "icon": "Table"
        },
        {
            "id": "postgresql",
            "name": "PostgreSQL",
            "category": "Relational Database",
            "description": "Enterprise SQL relational database connector",
            "status": "configured" if "postgresql" in configured_map else "available",
            "icon": "Database"
        },
        {
            "id": "mysql",
            "name": "MySQL",
            "category": "Relational Database",
            "description": "Open-source relational database connector",
            "status": "configured" if "mysql" in configured_map else "available",
            "icon": "Database"
        },
        {
            "id": "mongodb",
            "name": "MongoDB",
            "category": "NoSQL Database",
            "description": "Document-oriented NoSQL database connector",
            "status": "configured" if "mongodb" in configured_map else "available",
            "icon": "Boxes"
        }
    ]
    return available_connectors

@router.post("/test")
def test_connector(req: ConnectorTestRequest):
    try:
        connector = DataInputService.get_connector(req.source_type, req.config)
        res = connector.validate_connection()
        return res
    except Exception as e:
        return {"valid": False, "message": f"Connection test failed: {str(e)}"}
