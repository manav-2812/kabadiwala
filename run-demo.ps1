# Windows PowerShell Launch Script for Kabadiwala Connect
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Kabadiwala Connect - SIH 2026 (PS SIH26229)" -ForegroundColor Green
Write-Host "  Ministry of Mines / JNARDDC - Clean & Green Technology" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# 1. Check Python and Node
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Cyan
python --version
npm --version

# 2. Reset and seed DB
Write-Host "[2/4] Resetting and seeding database with demo scenario..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\backend"
python -m app.db.seed
if ($LASTEXITCODE -ne 0) {
    Write-Host "Database seed failed!" -ForegroundColor Red
    exit 1
}

# 3. Start Backend in background job or new window
Write-Host "[3/4] Starting FastAPI backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --port 8000"

# 4. Start Frontend
Write-Host "[4/4] Starting React Vite frontend on http://localhost:5173..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\web"
npm run dev
