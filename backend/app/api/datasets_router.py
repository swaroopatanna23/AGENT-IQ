import os
import shutil
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.users import User
from app.models.datasets import Dataset
from app.models.dataset_profiles import DatasetProfile
from app.auth.dependencies import get_current_user
from app.data_sources.service import DataInputService
from app.agents.data_agent.agent import DataAgent

router = APIRouter(prefix="/api/v1/datasets", tags=["Datasets"])

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_format = DataInputService.detect_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to disk
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    saved_filename = f"{os.path.splitext(file.filename)[0]}_{int(pd.Timestamp.utcnow().timestamp())}.{file_format}"
    file_path = os.path.join(user_upload_dir, saved_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Load and profile
    try:
        df = DataInputService.load_data(file_format, file_path)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded dataset: {str(e)}")

    row_count = len(df)
    column_count = len(df.columns)

    # Save Dataset record
    dataset = Dataset(
        user_id=current_user.id,
        name=file.filename,
        file_path=file_path,
        file_format=file_format,
        file_size_bytes=file_size,
        row_count=row_count,
        column_count=column_count
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Profile using DataAgent (Slide 10)
    data_agent = DataAgent()
    profile_data = data_agent.profile(df)

    profile = DatasetProfile(
        dataset_id=dataset.id,
        columns=profile_data["columns"],
        numerical_columns=profile_data["numerical_columns"],
        categorical_columns=profile_data["categorical_columns"],
        datetime_columns=profile_data["datetime_columns"],
        text_columns=profile_data["text_columns"],
        missing_values=profile_data["missing_values"],
        duplicate_rows=profile_data["duplicate_rows"],
        quality_score=profile_data["quality_score"],
        sensitive_columns=profile_data["sensitive_columns"],
        summary_statistics=profile_data["summary_statistics"]
    )
    db.add(profile)
    db.commit()

    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_format": dataset.file_format,
        "file_size_bytes": dataset.file_size_bytes,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "quality_score": profile_data["quality_score"],
        "profile": profile_data
    }

@router.get("")
def list_datasets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    datasets = db.query(Dataset).filter(Dataset.user_id == current_user.id).order_by(Dataset.created_at.desc()).all()
    output = []
    for d in datasets:
        q_score = d.profile.quality_score if d.profile else 100.0
        output.append({
            "id": d.id,
            "name": d.name,
            "file_format": d.file_format,
            "file_size_bytes": d.file_size_bytes,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "quality_score": q_score,
            "created_at": d.created_at
        })
    return output

@router.get("/{dataset_id}")
def get_dataset(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load sample preview
    preview = []
    if os.path.exists(dataset.file_path):
        try:
            df = DataInputService.load_data(dataset.file_format, dataset.file_path)
            preview = df.head(10).to_dict(orient="records")
        except Exception:
            pass

    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_format": dataset.file_format,
        "file_size_bytes": dataset.file_size_bytes,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "created_at": dataset.created_at,
        "preview": preview
    }

@router.get("/{dataset_id}/profile")
def get_dataset_profile(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.profile:
        p = dataset.profile
        # Preview
        preview = []
        if os.path.exists(dataset.file_path):
            try:
                df = DataInputService.load_data(dataset.file_format, dataset.file_path)
                preview = df.head(10).to_dict(orient="records")
            except Exception:
                pass
        return {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": p.columns,
            "numerical_columns": p.numerical_columns,
            "categorical_columns": p.categorical_columns,
            "datetime_columns": p.datetime_columns,
            "text_columns": p.text_columns,
            "missing_values": p.missing_values,
            "duplicate_rows": p.duplicate_rows,
            "quality_score": p.quality_score,
            "sensitive_columns": p.sensitive_columns,
            "summary_statistics": p.summary_statistics,
            "sample_preview": preview
        }

    # If profile does not exist yet, generate it on the fly
    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset file missing on server")

    df = DataInputService.load_data(dataset.file_format, dataset.file_path)
    profile_data = DataAgent().profile(df)
    return profile_data

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.user_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except Exception:
            pass
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}

@router.post("/load-sample/{sample_name}")
def load_sample_dataset(
    sample_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    samples = {
        "students": ("Students.csv", "sample_data/Students.csv"),
        "retail": ("online_retail_sales.csv", "sample_data/online_retail_sales.csv"),
        "employee": ("employee_workforce.csv", "sample_data/employee_workforce.csv"),
        "healthcare": ("healthcare_patients.csv", "sample_data/healthcare_patients.csv")
    }
    if sample_name not in samples:
        raise HTTPException(status_code=400, detail="Invalid sample name. Choose 'students', 'retail', 'employee', or 'healthcare'.")

    display_name, src_path = samples[sample_name]
    if not os.path.exists(src_path):
        raise HTTPException(status_code=404, detail="Sample dataset not found on server")

    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_upload_dir, exist_ok=True)
    dst_path = os.path.join(user_upload_dir, f"{sample_name}_{int(pd.Timestamp.utcnow().timestamp())}.csv")
    shutil.copyfile(src_path, dst_path)

    df = pd.read_csv(dst_path)
    dataset = Dataset(
        user_id=current_user.id,
        name=display_name,
        file_path=dst_path,
        file_format="csv",
        file_size_bytes=os.path.getsize(dst_path),
        row_count=len(df),
        column_count=len(df.columns)
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    profile_data = DataAgent().profile(df)
    profile = DatasetProfile(
        dataset_id=dataset.id,
        columns=profile_data["columns"],
        numerical_columns=profile_data["numerical_columns"],
        categorical_columns=profile_data["categorical_columns"],
        datetime_columns=profile_data["datetime_columns"],
        text_columns=profile_data["text_columns"],
        missing_values=profile_data["missing_values"],
        duplicate_rows=profile_data["duplicate_rows"],
        quality_score=profile_data["quality_score"],
        sensitive_columns=profile_data["sensitive_columns"],
        summary_statistics=profile_data["summary_statistics"]
    )
    db.add(profile)
    db.commit()

    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_format": dataset.file_format,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "quality_score": profile_data["quality_score"],
        "profile": profile_data
    }
