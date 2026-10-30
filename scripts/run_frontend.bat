@echo off
echo ========================================================
echo   Starting NEXORA CAMPUS Frontend (React + Vite)
echo   Listening on: http://localhost:5173
echo ========================================================
echo.

cd /d "%~dp0\..\frontend"
npm run dev
pause
