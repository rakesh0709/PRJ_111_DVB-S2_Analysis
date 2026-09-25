@echo off
setlocal EnableDelayedExpansion
title PRJ_111 Python Backend (Port 8080)
color 0B
cd /d "%~dp005_CODE"

echo ======================================================================
echo   PRJ_111: DVB-S2 Python Analysis Backend API Server
echo   Port: 8080  ^|  Host: 127.0.0.1
echo ======================================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo [OK] Using virtual environment (.venv)
) else (
    set "PYTHON_EXE=python"
    echo [NOTE] Using system Python
)

echo [OK] Starting Python HTTP REST API Server on http://127.0.0.1:8080 ...
echo [NOTE] Keep this window open. Press Ctrl+C to stop.
echo.

"%PYTHON_EXE%" run_frontend.py --host 127.0.0.1 --port 8080
pause
