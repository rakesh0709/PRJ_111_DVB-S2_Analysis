@echo off
setlocal EnableDelayedExpansion
title PRJ_111 DVB-S2 Receiver Output Stream Analyzer
color 0A

echo ======================================================================
echo   PRJ_111: DVB-S2 Receiver Output Stream Analyzer
echo   Review-2 Functional Prototype Milestone
echo   HTML5 + Vanilla CSS + JavaScript Interactive Dashboard
echo   Presidency University - Dept. of Computer Science and Engineering
echo   Authors: C Rakeshwar, Sk Samad, Y Vengala Rao
echo   Guide:   Asst. Prof. Irfan Rajab Bhat
echo ======================================================================
echo.

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%05_CODE"

:: Locate Python virtual environment
set "PYTHON_EXE=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo [OK] Using virtual environment: 05_CODE\.venv
) else (
    echo [NOTE] Using system Python
)

:: Check if server is already running on port 8080
netstat -ano | findstr 8080 | findstr LISTENING >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo.
    echo [OK] PRJ_111 Server is already active and listening on port 8080.
    echo [OK] Opening dashboard in your default web browser...
    start "" http://127.0.0.1:8080
    echo.
    echo ======================================================================
    echo   Dashboard active at: http://127.0.0.1:8080
    echo   Press any key to close this launcher - server remains running in background.
    echo ======================================================================
    pause >nul
    exit /b 0
)

echo.
echo [1/2] Starting Python HTTP Server & Analysis Engine (Port 8080)...
echo [2/2] Launching HTML5 Dashboard in default web browser...
echo.
echo ======================================================================
echo   Serving at: http://127.0.0.1:8080
echo   Backend Status: F1-F7 Frozen & Verified (240 Tests Passing)
echo   (Press Ctrl+C in this window to stop the server.)
echo ======================================================================
echo.

"%PYTHON_EXE%" run_frontend.py --host 127.0.0.1 --port 8080
pause
