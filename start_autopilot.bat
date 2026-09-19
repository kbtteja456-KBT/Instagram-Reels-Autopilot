@echo off
title AI Instagram Reels Autopilot Launcher
cd /d "%~dp0"
echo =========================================================
echo Starting AI Instagram Reels Autopilot 24/7 Engine
echo =========================================================

where docker >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [Launcher] Docker detected. Launching containers...
    docker compose up -d
) else (
    echo [Launcher] Docker not found. Starting local Python 24/7 backend and frontend...
    start "Instagram Autopilot Backend (Port 8001)" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001 --reload"
    if exist "frontend\node_modules" (
        start "Instagram Autopilot Frontend (Port 3001)" cmd /k "cd frontend && npm run dev"
    )
)

echo.
echo =========================================================
echo Autopilot Services Started!
echo Backend API & 24/7 Scheduler: http://localhost:8001
echo Frontend Dashboard:          http://localhost:3001
echo =========================================================
pause
