param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Ensure-Command($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Required command '$name' is not installed or not on PATH."
    }
}

Ensure-Command python

$npmExists = $true
try {
    Ensure-Command npm
} catch {
    Write-Warning "npm is not installed or not on PATH. Frontend will not start automatically."
    $npmExists = $false
}

if (-not (Test-Path '.venv')) {
    Write-Host 'Creating virtual environment...'
    python -m venv .venv
}

$pythonExe = Join-Path $root '.venv\Scripts\python.exe'
$pipExe = Join-Path $root '.venv\Scripts\pip.exe'
if (-not (Test-Path $pythonExe)) {
    throw 'Failed to locate the Python executable inside .venv.'
}

Write-Host 'Installing backend dependencies...'
& $pipExe install -r vibe_scanner/requirements.txt

if (-not (Test-Path '.env')) {
    if (Test-Path '.env.example') {
        Write-Host 'Copying .env.example to .env...'
        Copy-Item -Path '.env.example' -Destination '.env' -Force
        Write-Host 'Please edit .env to set a secure SECRET_KEY before production use.'
    } else {
        throw '.env file not found and .env.example is missing.'
    }
}

Write-Host 'Starting backend server...'
$backendCommand = "& '$pythonExe' -m uvicorn vibe_scanner.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process -FilePath pwsh -ArgumentList '-NoExit', '-Command', "Set-Location '$root'; $backendCommand"

if ($npmExists) {
    $frontendDir = Join-Path $root 'vibe_scanner/frontend'
    Write-Host 'Installing frontend dependencies...'
    Push-Location $frontendDir
    npm install
    Pop-Location

    Write-Host 'Starting frontend server...'
    $frontendCommand = "Set-Location '$frontendDir'; npm run dev -- --host 0.0.0.0 --port 5173"
    Start-Process -FilePath pwsh -ArgumentList '-NoExit', '-Command', $frontendCommand

    Start-Sleep -Seconds 5
    Write-Host 'Opening frontend in browser...'
    Start-Process 'http://127.0.0.1:5173'
} else {
    Write-Warning 'Frontend skipped because npm is unavailable.'
}

Write-Host 'Backend available at http://127.0.0.1:8000'
if ($npmExists) {
    Write-Host 'Frontend available at http://127.0.0.1:5173'
}
