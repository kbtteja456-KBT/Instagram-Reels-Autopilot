@echo off
title AI Reels Autopilot - Cloud Failure Self-Healer
cd /d "%~dp0"
echo ========================================================
echo  AI Instagram Reels Autopilot - Missed Slot Recovery
echo ========================================================
echo Checking MongoDB Atlas to see if Cloud Servers posted today...
python scripts/catch_up_missed_slots.py
echo.
echo Check complete.
pause
