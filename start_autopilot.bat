@echo off
title AI Instagram Reels Autopilot Launcher
cd /d "%~dp0"
echo =========================================================
echo Starting AI Instagram Reels Autopilot 24/7 Engine
echo =========================================================
docker compose up -d
echo Services running in background!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo =========================================================
pause
