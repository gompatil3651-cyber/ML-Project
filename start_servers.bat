@echo off
echo =================================================
echo   Starting Stock Insight Full-Stack System
echo =================================================

start "Python ML Microservice (Port 8000)" cmd /k "cd /d %~dp0 && python -m uvicorn microservices.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir microservices"
start "Node.js Express Backend (Port 5000)" cmd /k "cd /d %~dp0 && npm --prefix backend start"
start "Streamlit Frontend Dashboard (Port 8501)" cmd /k "cd /d %~dp0 && python -m streamlit run frontend/app.py"

echo All services launched in separate windows!
echo -> Streamlit Dashboard: http://localhost:8501
echo -> Python Swagger Docs: http://127.0.0.1:8000/docs
echo -> Node.js Backend API: http://127.0.0.1:5000/health
pause
