@echo off
echo ========================================================
echo   NEXORA CAMPUS - Automated Environment Setup
echo ========================================================
echo.

cd /d "%~dp0\.."

echo [1/4] Setting up Python virtual environment...
if not exist backend\venv (
    py -3.11 -m venv backend\venv
    if errorlevel 1 (
        echo Python 3.11 not found via 'py -3.11'. Falling back to 'python -m venv'...
        python -m venv backend\venv
    )
)

echo [2/4] Installing backend dependencies...
backend\venv\Scripts\python.exe -m pip install --upgrade pip
backend\venv\Scripts\pip.exe install -r backend\requirements.txt
backend\venv\Scripts\pip.exe install langgraph

echo [3/4] Initializing and seeding SQLite campus database...
backend\venv\Scripts\python.exe -m backend.app.data.seed_data

echo [4/4] Installing frontend npm packages...
cd frontend
call npm install
cd ..

echo.
echo ========================================================
echo   NEXORA CAMPUS Setup Complete!
echo   Run 'scripts\run_backend.bat' and 'scripts\run_frontend.bat'
echo ========================================================
pause
