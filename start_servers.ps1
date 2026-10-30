# Stock Insight Multi-Service Launcher
$rootDir = $PSScriptRoot
if (-not $rootDir) { $rootDir = "d:\se" }

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Starting Stock Insight Full-Stack System      " -ForegroundColor Cyan
Write-Host "  Working Directory: $rootDir" -ForegroundColor DarkGray
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Start Python FastAPI Microservice
Write-Host "[1/3] Launching Python ML Microservice (Port 8000)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $rootDir -ArgumentList "-NoExit", "-Command", "Set-Location '$rootDir'; Write-Host 'Starting Python ML Microservice...'; python -m uvicorn microservices.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir microservices"

# 2. Start Node.js Express Backend
Write-Host "[2/3] Launching Node.js Backend API (Port 5000)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $rootDir -ArgumentList "-NoExit", "-Command", "Set-Location '$rootDir'; Write-Host 'Starting Node.js Backend...'; npm --prefix backend start"

# 3. Start Streamlit Frontend Dashboard
Write-Host "[3/3] Launching Streamlit Dashboard (Port 8501)..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $rootDir -ArgumentList "-NoExit", "-Command", "Set-Location '$rootDir'; Write-Host 'Starting Streamlit Dashboard...'; python -m streamlit run frontend/app.py"

Write-Host ""
Write-Host "All services launching:" -ForegroundColor Yellow
Write-Host "  -> Streamlit Dashboard:          http://localhost:8501" -ForegroundColor Yellow
Write-Host "  -> Node.js API Health & Auth:    http://localhost:5000/health" -ForegroundColor Yellow
Write-Host "  -> Python ML Microservice Docs:  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Cyan
