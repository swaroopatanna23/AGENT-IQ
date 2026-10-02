from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class DashboardModel(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    theme = Column(String(50), default="light")
    layout_type = Column(String(50), default="grid")  # grid, executive, detailed, trends
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboards")
    dataset = relationship("Dataset", back_populates="dashboards")
    components = relationship("DashboardComponentModel", back_populates="dashboard", cascade="all, delete-orphan")

class DashboardComponentModel(Base):
    __tablename__ = "dashboard_components"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    component_type = Column(String(50), nullable=False)  # kpi_card, bar_chart, line_chart, pie_chart, scatter_plot, etc.
    config = Column(JSON, default=dict)  # x_axis, y_axis, colors, aggregations
    position = Column(JSON, default=dict)  # x, y, w, h
    data_cache = Column(JSON, default=dict)  # cached chart data
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dashboard = relationship("DashboardModel", back_populates="components")
