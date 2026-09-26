@echo off
echo ===================================================
echo   Starting Analyzer.ai - AI Resume Analyzer
echo ===================================================

cd backend
if not exist .venv (
    echo Virtual environment not found. Please run setup first.
    pause
    exit /b
)

echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "" .venv\Scripts\python.exe run.py

timeout /t 2 >nul
echo Opening Frontend in your default browser...
start "" "..\frontend\index.html"

echo.
echo Application is running!
echo Backend:  http://127.0.0.1:8000
echo Swagger:  http://127.0.0.1:8000/docs
echo.
pause
