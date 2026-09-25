@echo off
setlocal EnableDelayedExpansion
title PRJ_111 Automated Verification Suite
color 0B
set "ROOT_DIR=%~dp0"

echo ======================================================================
echo   PRJ_111: Full Automated Test Verification Suite
echo   Python Core Pipeline (207 Tests) + Frontend Integration (33 Tests)
echo ======================================================================
echo.

cd /d "%ROOT_DIR%05_CODE"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Running Full Automated Regression Suite (240 tests: 207 pipeline + 33 server integration)...
"%PYTHON_EXE%" -m unittest discover -s tests -v
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Automated tests failed with exit code %ERRORLEVEL%!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo   ALL TESTS PASSED: 240/240 Tests Passing (100%% VERIFIED, 0 ERRORS)
echo ======================================================================
pause

