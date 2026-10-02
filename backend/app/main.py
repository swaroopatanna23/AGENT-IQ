from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import init_db
from app.data_sources.service import DataInputService
from app.agents.data_agent.agent import DataAgent

# Routers
from app.auth.router import router as auth_router
from app.api.datasets_router import router as datasets_router
from app.api.analysis_router import router as analysis_router
from app.api.dashboards_router import router as dashboards_router
from app.api.data_sources_router import router as data_sources_router
from app.api.export_router import router as export_router

# Initialize database tables on startup
init_db()

app = FastAPI(
    title="AgentIQ API",
    version=settings.APP_VERSION,
    description="An AI Framework for Universal File Analysis and Interactive Dashboard Generation over Data (Major Project Batch-08)"
)

# CORS Configuration
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(datasets_router)
app.include_router(analysis_router)
app.include_router(dashboards_router)
app.include_router(data_sources_router)
app.include_router(export_router)

# Direct root endpoint matching Slide 10
@app.get("/")
def root():
    return {
        "message": "AgentIQ backend is running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "agents": [
            "Data Agent",
            "Query Understanding Agent",
            "Planning Agent",
            "Analysis Agent",
            "Validation & Privacy Agent",
            "Visualization Agent",
            "Explanation Agent"
        ]
    }

# Direct profile endpoint directly matching Slide 10
@app.post("/api/v1/profile")
async def profile_file(file: UploadFile = File(...)):
    try:
        t = DataInputService.detect_file_type(file.filename)
        df = DataInputService.load_data(t, file.file)
        return DataAgent().profile(df)
    except Exception as e:
        raise HTTPException(400, str(e))
