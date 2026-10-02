from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(20), nullable=False)  # csv, xlsx, json, sheets, etc.
    file_size_bytes = Column(BigInteger, default=0)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="datasets")
    data_source = relationship("DataSource", back_populates="datasets")
    profile = relationship("DatasetProfile", back_populates="dataset", uselist=False, cascade="all, delete-orphan")
    queries = relationship("QueryModel", back_populates="dataset", cascade="all, delete-orphan")
    dashboards = relationship("DashboardModel", back_populates="dataset", cascade="all, delete-orphan")
    conversations = relationship("ConversationModel", back_populates="dataset", cascade="all, delete-orphan")
