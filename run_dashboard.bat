@echo off
echo =========================================
echo Starting Public Health Analytics Platform
echo =========================================

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k ".\venv\Scripts\activate && cd api && uvicorn main:app --reload"

echo Starting React Frontend...
timeout /t 3 /nobreak > nul
start "React Frontend" cmd /k "cd frontend && npm run dev"

echo Both services have been launched in separate terminal windows.
echo Navigate to http://localhost:5173 to view your Dashboard!
