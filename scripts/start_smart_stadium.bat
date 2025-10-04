@echo off
REM Smart Stadium - Windows Startup Script
REM Launches both API backend and React frontend

echo ==========================================
echo 🏟️ Smart Stadium System Launcher
echo ==========================================

echo.
echo 🔧 Setting up Python environment...
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo 🚀 Starting Smart Stadium API Server...
start "Smart Stadium API" cmd /k "cd api && python start_server.py"

echo Waiting for API to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Starting React Frontend Dashboard...
cd frontend\smart-stadium-dashboard
start "Smart Stadium Dashboard" cmd /k "npm install && npm run dev"

echo.
echo ==========================================
echo ✅ Smart Stadium is launching!
echo.
echo 📱 API Server: http://localhost:8000
echo 🎮 Dashboard: http://localhost:3000
echo 📋 API Docs: http://localhost:8000/api/docs
echo.
echo Press any key to exit launcher...
echo ==========================================
pause > nul