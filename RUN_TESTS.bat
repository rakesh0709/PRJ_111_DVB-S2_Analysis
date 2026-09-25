@echo off
title PRJ_111 Automated Verification Suite (240 Tests)
color 0B
cd /d "%~dp005_CODE"

echo ======================================================================
echo   PRJ_111: Automated Test Verification Suite
echo   Executing 240 Unit & Integration Tests (100%% Target)
echo ======================================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m unittest discover -s tests -v

echo.
echo ======================================================================
echo   Verification Completed. Press any key to close this window.
echo ======================================================================
pause
