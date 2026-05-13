@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion
title Task Planner

echo ============================================================
echo  Task Planner -- install and run
echo ============================================================
echo.

REM ----- Find Python -----
set "PY_CMD="
where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"
)
if not defined PY_CMD (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version >nul 2>&1
        if not errorlevel 1 set "PY_CMD=python"
    )
)
if not defined PY_CMD (
    echo [ERROR] Python not found in PATH.
    echo Install Python 3.12 from:
    echo    https://www.python.org/downloads/release/python-3127/
    echo Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
echo [1/4] Python: !PY_CMD!

REM ----- Create venv -----
if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Creating .venv ...
    !PY_CMD! -m venv .venv
    if errorlevel 1 (
        echo [ERROR] venv creation failed.
        pause
        exit /b 1
    )
) else (
    echo [2/4] .venv already exists
)

REM ----- Install dependencies -----
echo [3/4] Installing dependencies ^(may take a few minutes^)...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    echo Try installing Python 3.12 from:
    echo    https://www.python.org/downloads/release/python-3127/
    echo Then delete .venv folder and run this script again.
    pause
    exit /b 1
)

REM ----- Seed demo data -----
if not exist "tasks.db" (
    echo [4/4] Seeding demo data ...
    ".venv\Scripts\python.exe" seed_demo.py
    if errorlevel 1 (
        echo [ERROR] seed_demo.py failed.
        pause
        exit /b 1
    )
) else (
    echo [4/4] tasks.db already exists, skipping seed
)

echo.
echo ============================================================
echo  Open http://127.0.0.1:8000 in your browser
echo  Login:    matvey
echo  Password: matvey2026
echo  Ctrl+C to stop the server
echo ============================================================
echo.

start "" /min cmd /c "ping -n 4 127.0.0.1 >nul && start http://127.0.0.1:8000"

".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
endlocal