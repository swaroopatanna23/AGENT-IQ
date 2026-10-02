from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User
from app.models.dashboards import DashboardModel, DashboardComponentModel
from app.models.datasets import Dataset
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/dashboards", tags=["Dashboards"])

class ComponentCreate(BaseModel):
    title: str
    component_type: str
    config: Dict[str, Any] = {}
    position: Dict[str, Any] = {}
    data_cache: List[Dict[str, Any]] = []
    query_id: Optional[int] = None

class DashboardCreate(BaseModel):
    dataset_id: int
    title: str
    description: Optional[str] = ""
    theme: Optional[str] = "light"
    layout_type: Optional[str] = "grid"
    components: Optional[List[ComponentCreate]] = []

class DashboardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    layout_type: Optional[str] = None
    components: Optional[List[Dict[str, Any]]] = None

@router.get("")
def list_dashboards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dashboards = db.query(DashboardModel).filter(DashboardModel.user_id == current_user.id).order_by(DashboardModel.updated_at.desc()).all()
    output = []
    for d in dashboards:
        output.append({
            "id": d.id,
            "dataset_id": d.dataset_id,
            "dataset_name": d.dataset.name if d.dataset else "Dataset",
            "title": d.title,
            "description": d.description,
            "theme": d.theme,
            "layout_type": d.layout_type,
            "component_count": len(d.components),
            "created_at": d.created_at,
            "updated_at": d.updated_at
        })
    return output

@router.post("", status_code=status.HTTP_201_CREATED)
def create_dashboard(
    data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == data.dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dashboard = DashboardModel(
        user_id=current_user.id,
        dataset_id=data.dataset_id,
        title=data.title,
        description=data.description,
        theme=data.theme or "light",
        layout_type=data.layout_type or "grid"
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)

    for c in data.components:
        comp = DashboardComponentModel(
            dashboard_id=dashboard.id,
            title=c.title,
            component_type=c.component_type,
            config=c.config,
            position=c.position,
            data_cache=c.data_cache,
            query_id=c.query_id
        )
        db.add(comp)
    db.commit()
    db.refresh(dashboard)

    return get_dashboard(dashboard.id, current_user, db)

@router.get("/{dashboard_id}")
def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(DashboardModel).filter(
        DashboardModel.id == dashboard_id,
        DashboardModel.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    components_data = []
    for c in dashboard.components:
        components_data.append({
            "id": c.id,
            "title": c.title,
            "component_type": c.component_type,
            "config": c.config,
            "position": c.position,
            "data_cache": c.data_cache,
            "query_id": c.query_id
        })

    return {
        "id": dashboard.id,
        "dataset_id": dashboard.dataset_id,
        "dataset_name": dashboard.dataset.name if dashboard.dataset else "Dataset",
        "title": dashboard.title,
        "description": dashboard.description,
        "theme": dashboard.theme,
        "layout_type": dashboard.layout_type,
        "components": components_data,
        "created_at": dashboard.created_at,
        "updated_at": dashboard.updated_at
    }

@router.put("/{dashboard_id}")
def update_dashboard(
    dashboard_id: int,
    data: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(DashboardModel).filter(
        DashboardModel.id == dashboard_id,
        DashboardModel.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    if data.title is not None: dashboard.title = data.title
    if data.description is not None: dashboard.description = data.description
    if data.theme is not None: dashboard.theme = data.theme
    if data.layout_type is not None: dashboard.layout_type = data.layout_type

    if data.components is not None:
        # Clear existing components and replace with updated set
        db.query(DashboardComponentModel).filter(DashboardComponentModel.dashboard_id == dashboard.id).delete()
        for c in data.components:
            comp = DashboardComponentModel(
                dashboard_id=dashboard.id,
                title=c.get("title", "Chart"),
                component_type=c.get("component_type", "bar"),
                config=c.get("config", {}),
                position=c.get("position", {}),
                data_cache=c.get("data_cache", []),
                query_id=c.get("query_id")
            )
            db.add(comp)

    db.commit()
    return get_dashboard(dashboard.id, current_user, db)

@router.delete("/{dashboard_id}")
def delete_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard = db.query(DashboardModel).filter(
        DashboardModel.id == dashboard_id,
        DashboardModel.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    db.delete(dashboard)
    db.commit()
    return {"message": "Dashboard deleted successfully"}
