from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class DatasetProfile(Base):
    __tablename__ = "dataset_profiles"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True, nullable=False)
    
    # Core Profiling Data
    columns = Column(JSON, default=list)  # list of {name, type, null_count, unique_count, sample_values}
    numerical_columns = Column(JSON, default=list)
    categorical_columns = Column(JSON, default=list)
    datetime_columns = Column(JSON, default=list)
    text_columns = Column(JSON, default=list)
    
    missing_values = Column(JSON, default=dict)  # {col_name: {count, percentage}}
    duplicate_rows = Column(Integer, default=0)
    quality_score = Column(Float, default=100.0)  # 0.0 - 100.0
    sensitive_columns = Column(JSON, default=list)  # [{column, reason, risk_level}]
    summary_statistics = Column(JSON, default=dict)  # {col: {min, max, mean, std, median, q25, q75}}
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="profile")
