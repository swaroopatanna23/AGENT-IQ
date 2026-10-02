from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class QueryModel(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    user_question = Column(Text, nullable=False)
    detected_language = Column(String(20), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="queries")
    dataset = relationship("Dataset", back_populates="queries")
    conversation = relationship("ConversationModel", back_populates="queries")
    
    schema = relationship("AnalysisSchemaModel", back_populates="query", uselist=False, cascade="all, delete-orphan")
    plan = relationship("AnalysisPlanModel", back_populates="query", uselist=False, cascade="all, delete-orphan")
    result = relationship("AnalysisResultModel", back_populates="query", uselist=False, cascade="all, delete-orphan")

class AnalysisSchemaModel(Base):
    __tablename__ = "analysis_schemas"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), unique=True, nullable=False)
    
    intent = Column(String(100), nullable=False)
    target_columns = Column(JSON, default=list)
    group_by = Column(JSON, default=list)
    filters = Column(JSON, default=list)
    aggregation = Column(String(50), nullable=True)
    sorting = Column(JSON, default=dict)
    limit = Column(Integer, nullable=True)
    time_granularity = Column(String(50), nullable=True)
    comparison = Column(JSON, default=dict)
    statistical_operation = Column(String(100), nullable=True)
    requested_visualization = Column(String(50), nullable=True)
    privacy_constraints = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("QueryModel", back_populates="schema")

class AnalysisPlanModel(Base):
    __tablename__ = "analysis_plans"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), unique=True, nullable=False)
    
    steps = Column(JSON, default=list)  # list of strings / steps
    compute_engine = Column(String(50), default="pandas")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("QueryModel", back_populates="plan")

class AnalysisResultModel(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), unique=True, nullable=False)
    
    execution_status = Column(String(50), default="success")  # success, error
    result_data = Column(JSON, default=list)  # records
    summary_kpis = Column(JSON, default=dict)
    row_count = Column(Integer, default=0)
    execution_time_ms = Column(Float, default=0.0)
    validation_status = Column(JSON, default=dict)  # integrity checks & privacy masking log
    
    # Visualization Specification
    visualization_spec = Column(JSON, default=dict)  # chart type, x, y, labels
    
    # Grounded Explanations
    explanation = Column(JSON, default=dict)  # short_answer, key_insights, observations, limitations
    
    # Observability Trace
    agent_trace = Column(JSON, default=list)  # trace metadata for all 7 agents
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("QueryModel", back_populates="result")
