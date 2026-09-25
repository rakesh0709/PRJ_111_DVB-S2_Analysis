@echo off
setlocal EnableDelayedExpansion
title PRJ_111 Next.js 15 Web Workstation (Port 3000)
color 0E
cd /d "%~dp005_CODE\web"

echo ======================================================================
echo   PRJ_111: Next.js 15 + Tailwind CSS v4 Engineering Workstation
echo   Port: 3000  ^|  URL: http://localhost:3000
echo ======================================================================
echo.

if not exist "node_modules" (
    echo [NOTE] node_modules not found. Installing web dependencies...
    call npm install
)

echo Starting Next.js development server on http://localhost:3000 ...
echo (Connects to Python backend at http://127.0.0.1:8080 for live analysis;
echo  gracefully falls back to precompiled empirical showcase if offline.)
echo.

call npm run dev
pause
