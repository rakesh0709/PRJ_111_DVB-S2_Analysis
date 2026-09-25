@echo off
setlocal EnableDelayedExpansion
title PRJ_111 DVB-S2 Analyzer - Dual-Stack Launch System
color 0A

echo ======================================================================
echo   PRJ_111: DVB-S2 Receiver Output Stream Analyzer
echo   Full Dual-Stack Engineering Workstation Launcher
echo   Presidency University - Dept. of Computer Science and Engineering
echo   Authors: C Rakeshwar, Sk Samad, Y Vengala Rao
echo   Guide:   Asst. Prof. Irfan Rajab Bhat
echo ======================================================================
echo.

set "ROOT_DIR=%~dp0"

:: 1. Launch Python REST Backend in dedicated window
echo [1/3] Starting Python Analysis Backend API (Port 8080)...
start "PRJ_111 Python Backend (Port 8080)" "%ROOT_DIR%START_BACKEND.bat"

:: 2. Wait for backend initialization
echo [2/3] Waiting for API gateway to initialize...
timeout /t 3 /nobreak >nul

:: 3. Launch Default Web Browser
echo [3/3] Opening Workstation in Default Web Browser...
start http://localhost:3000

:: 4. Launch Next.js Web Workstation in current window
echo.
echo ======================================================================
echo   Launching Next.js 15 Web Workstation...
echo   - Web Terminal:    http://localhost:3000
echo   - Backend REST:    http://127.0.0.1:8080
echo   (Press Ctrl+C in this window to stop the Next.js server.)
echo ======================================================================
echo.

call "%ROOT_DIR%START_WEB_WORKSTATION.bat"
