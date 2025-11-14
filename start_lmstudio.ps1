# RAG Tech Doc Search - LM Studio Edition Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Tech Doc Search - LM Studio Edition" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-Not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Set UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

# Check LM Studio connection
Write-Host "[2/3] Checking LM Studio..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] LM Studio is running" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] LM Studio is not running or server not started" -ForegroundColor Yellow
    Write-Host "  Please:" -ForegroundColor Yellow
    Write-Host "  1. Open LM Studio" -ForegroundColor Yellow
    Write-Host "  2. Load a model" -ForegroundColor Yellow
    Write-Host "  3. Go to Server tab and click 'Start Server'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  App will start anyway (search-only mode)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/3] Starting application..." -ForegroundColor Green
Write-Host "  URL: http://localhost:7861" -ForegroundColor Cyan
Write-Host "  Login: admin / password123" -ForegroundColor Cyan
Write-Host ""

# Start application
python app_lmstudio.py

