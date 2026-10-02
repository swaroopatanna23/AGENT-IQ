@echo off
title AgentIQ - Multi-Agent AI Analytics Framework
echo =====================================================================
echo  Starting AgentIQ (Batch-08 Final Year Major Project)
echo =====================================================================
echo.

:: Set environment paths
set VENV_PYTHON=C:\Users\TIRUPATI\.agentiq_venv\Scripts\python.exe
set WORKSPACE_DIR=%~dp0

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "AgentIQ Backend Server" cmd /k "cd /d "%WORKSPACE_DIR%" && "%VENV_PYTHON%" backend/run.py"

echo [2/2] Starting Vite React Frontend on http://localhost:5173 ...
start "AgentIQ Frontend WebApp" cmd /k "cd /d "%WORKSPACE_DIR%frontend" && npm run dev"

echo.
echo =====================================================================
echo  Both servers are starting in separate windows!
echo  AgentIQ Web App: http://localhost:5173
echo  FastAPI Backend: http://localhost:8000
echo  Swagger Docs:    http://localhost:8000/docs
echo =====================================================================
timeout /t 3 >nul
start http://localhost:5173
