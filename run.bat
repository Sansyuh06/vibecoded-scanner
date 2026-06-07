@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Ensure Python is available
where python >nul 2>&1 || (
  echo Error: Python is not installed or not on PATH.
  exit /b 1
)

:: Ensure npm and node are available for frontend
set "FRONTEND_AVAILABLE=1"
where npm >nul 2>&1 || set "FRONTEND_AVAILABLE="
where node >nul 2>&1 || set "FRONTEND_AVAILABLE="
if not defined FRONTEND_AVAILABLE (
  echo Warning: Node.js and npm are not installed or not on PATH. Frontend will not start automatically.
  set "SKIP_FRONTEND=1"
)

:: Create virtual environment if needed
if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)

:: Activate virtual environment
call ".venv\Scripts\activate.bat"

:: Install backend dependencies
if exist "vibe_scanner\requirements.txt" (
  echo Installing backend dependencies...
  pip install -r vibe_scanner\requirements.txt
)

:: Ensure environment config exists
if not exist ".env" (
  if exist ".env.example" (
    echo No .env file found. Copying .env.example to .env...
    copy /Y .env.example .env >nul
    echo Please edit .env to set a secure SECRET_KEY before using this in production.
  ) else (
    echo Error: .env file not found and .env.example missing.
    exit /b 1
  )
)

echo Starting backend server...
start "Vibe Scanner API" /D "%~dp0" cmd /k "call .venv\Scripts\activate.bat && uvicorn vibe_scanner.main:app --reload --host 127.0.0.1 --port 8000"

if defined SKIP_FRONTEND (
  echo Skipping frontend start because npm/node is unavailable.
  goto end
)

set "FRONTEND_DIR=%~dp0\vibe_scanner\frontend"
echo Installing frontend dependencies in %FRONTEND_DIR%...
pushd "%FRONTEND_DIR%"
npm install
if errorlevel 1 (
  echo Error: npm install failed in frontend directory.
  popd
  set "SKIP_FRONTEND=1"
) else (
  popd
)

if defined SKIP_FRONTEND (
  goto end
)

:: Start the frontend in a new window
start "Vibe Scanner UI" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev -- --host 0.0.0.0 --port 5173"

:: Wait a few seconds for the frontend to bind before opening the browser
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5173"

:end

echo Backend available at http://127.0.0.1:8000
if not defined SKIP_FRONTEND echo Frontend available at http://127.0.0.1:5173
pause
