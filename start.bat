@echo off
echo Starting Dragon Intelligence Platform...
echo.

REM Start Backend
echo [1/2] Starting Backend (Flask) on http://localhost:5000
cd backend
start cmd /k "python app.py"
timeout /t 3

REM Start Frontend
echo [2/2] Starting Frontend (React) on http://localhost:3000
cd ../frontend
npm start

pause
