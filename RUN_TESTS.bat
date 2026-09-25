@echo off
setlocal EnableDelayedExpansion
title PRJ_111 Automated Verification Suite
color 0B
set "ROOT_DIR=%~dp0"

echo ======================================================================
echo   PRJ_111: Full Automated Test Verification Suite
echo   Python Backend Suite (240 Tests) + Next.js Suite (9 Tests)
echo ======================================================================
echo.

cd /d "%ROOT_DIR%05_CODE"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [1/2] Running Python Regression Suite (240 tests: 207 unit + 33 API integration)...
"%PYTHON_EXE%" -m unittest discover -s tests -v
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Python tests failed with exit code %ERRORLEVEL%!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Next.js Frontend Verification Suite (9 tests)...
cd /d "%ROOT_DIR%05_CODE\web"
call npm test
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Next.js tests failed with exit code %ERRORLEVEL%!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo   ALL TESTS PASSED: 240/240 Python + 9/9 Next.js (100%% VERIFIED)
echo ======================================================================
pause
