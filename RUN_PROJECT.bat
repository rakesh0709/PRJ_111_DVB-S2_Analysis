@echo off
setlocal EnableDelayedExpansion
title PRJ_111 DVB-S2 Stream Analyzer Workstation
color 0A

:: Robust directory resolution: handle running from root or inside 05_CODE
if exist "%~dp005_CODE\run_frontend.py" (
    cd /d "%~dp005_CODE"
) else if exist "%~dp0run_frontend.py" (
    cd /d "%~dp0"
) else (
    echo [ERROR] Could not locate run_frontend.py!
    echo Looked in: "%~dp0" and "%~dp005_CODE"
    pause
    exit /b 1
)

echo ======================================================================
echo   PRJ_111: DVB-S2 Receiver Output Stream Analyzer Workstation
echo   Presidency University - Dept. of Computer Science and Engineering
echo   Authors: Sk Samad, Y Vengala Rao, C Rakeshwar
echo   Guide:   Asst. Prof. Irfan Rajab Bhat
echo ======================================================================
echo.
echo Current Working Directory: %CD%
echo.

:: Locate Python executable
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo [OK] Using dedicated project virtual environment (.venv)
) else (
    set "PYTHON_EXE=python"
    echo [NOTE] Dedicated .venv not found. Using system Python.
)

echo [OK] Python Target: %PYTHON_EXE%
echo.
echo ======================================================================
echo   Starting PRJ_111 HTTP Server and Analysis Engines...
echo   Dashboard URL: http://127.0.0.1:8080
echo   (Leave this console window open while testing. Press Ctrl+C to stop.)
echo ======================================================================
echo.

"%PYTHON_EXE%" run_frontend.py --host 127.0.0.1 --port 8080

echo.
echo ======================================================================
echo   Server has stopped.
echo ======================================================================
pause
