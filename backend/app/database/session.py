from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# If using SQLite, check_same_thread needs to be False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all models to ensure tables are registered with Base.metadata
    from app.models import (
        User, DataSource, Dataset, DatasetProfile,
        QueryModel, AnalysisSchemaModel, AnalysisPlanModel, AnalysisResultModel,
        DashboardModel, DashboardComponentModel,
        ConversationModel, ConversationMessageModel
    )
    Base.metadata.create_all(bind=engine)
