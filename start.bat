@echo off
echo ===================================================
echo 🐉 Starting Dragon Intel Offline Startup Sequence
echo ===================================================
echo.

REM Start Ollama
echo [1/3] Starting Ollama AI Engine (llama3.2)...
start "Ollama Engine" cmd /k "ollama run llama3.2"
timeout /t 2 >nul

REM Start Backend
echo [2/3] Starting Backend (Flask) on http://localhost:5000...
cd backend
start "Flask Backend" cmd /k "..\.venv\Scripts\activate && python app.py"
cd ..
timeout /t 3 >nul

REM Start Frontend
echo [3/3] Starting Frontend (React) on http://localhost:3000...
cd frontend
start "React UI" cmd /k "npm start"
cd ..

echo.
echo ===================================================
echo All services launched in separate windows!
echo - Ollama API: http://localhost:11434
echo - Backend API: http://localhost:5000
echo - Frontend UI: http://localhost:3000
echo ===================================================
exit
