@echo off
title PRJ_111 Next.js 15 Web Workstation
color 0E
cd /d "%~dp005_CODE\web"

echo ======================================================================
echo   PRJ_111: DVB-S2 Next.js 15 + Tailwind CSS v4 Web Workstation
echo   Presidency University - Dept. of Computer Science and Engineering
echo ======================================================================
echo.
echo Starting Next.js development server on http://localhost:3000 ...
echo (Connects to Python backend at http://127.0.0.1:8080 for live analysis;
echo  gracefully falls back to precompiled empirical showcase if offline.)
echo.

npm run dev
pause
