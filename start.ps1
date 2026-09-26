# Analyzer.ai - Startup Script for PowerShell
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting Analyzer.ai - AI Resume Analyzer" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$BackendDir = Join-Path $PSScriptRoot "backend"
$FrontendFile = Join-Path $PSScriptRoot "frontend\index.html"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Virtual environment not detected at $PythonExe." -ForegroundColor Red
    Write-Host "Creating environment with uv..." -ForegroundColor Yellow
    & "C:\Users\vamsh\.local\bin\uv.exe" venv --python 3.12 (Join-Path $BackendDir ".venv")
    & "C:\Users\vamsh\.local\bin\uv.exe" pip install -r (Join-Path $BackendDir "requirements.txt") --python $PythonExe
}

Write-Host "Launching FastAPI backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process -FilePath $PythonExe -ArgumentList "run.py" -WorkingDirectory $BackendDir

Start-Sleep -Seconds 2

Write-Host "Opening Frontend in default browser..." -ForegroundColor Green
Start-Process $FrontendFile

Write-Host "`nApplication is active!" -ForegroundColor Cyan
Write-Host "Backend API:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "API Docs:     http://127.0.0.1:8000/docs" -ForegroundColor White
