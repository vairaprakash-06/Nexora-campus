@echo off
echo ========================================================
echo   Starting NEXORA CAMPUS Backend (FastAPI + Uvicorn)
echo   Listening on: http://127.0.0.1:8000
echo   API Docs:     http://127.0.0.1:8000/docs
echo ========================================================
echo.

cd /d "%~dp0\.."
backend\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
