#!/usr/bin/env bash
set -e

# One-click launcher for Vibe Scanner
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Find Python executable
PYTHON_CMD=""
if command -v python >/dev/null 2>&1; then
  PYTHON_CMD=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
else
  echo "Error: Python is not installed or not on PATH."
  exit 1
fi

# Create virtualenv if needed
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON_CMD" -m venv .venv
fi

# Activate virtualenv
# shellcheck source=/dev/null
source .venv/bin/activate

# Install dependencies if needed
if [ -f "vibe_scanner/requirements.txt" ]; then
  echo "Installing dependencies..."
  pip install -r vibe_scanner/requirements.txt
fi

# Ensure environment config exists
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    echo "No .env file found. Copying .env.example to .env..."
    cp .env.example .env
    echo "Please edit .env to set a secure SECRET_KEY before using this in production."
  else
    echo "Error: .env file not found and .env.example missing."
    exit 1
  fi
fi

echo "Starting Vibe Scanner on http://127.0.0.1:8000"
exec uvicorn vibe_scanner.main:app --reload --host 127.0.0.1 --port 8000
