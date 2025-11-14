# RAG Tech Doc Search System - GPU Version Startup Script
# Encoding: UTF-8 with BOM

Write-Host "================================" -ForegroundColor Cyan
Write-Host "RAG Tech Doc Search - GPU Mode" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-Not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Set UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

# Check CUDA
Write-Host "[2/4] Checking CUDA/GPU status..." -ForegroundColor Green
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

Write-Host ""
Write-Host "[3/4] First-time startup notice:" -ForegroundColor Yellow
Write-Host "  - Mistral-7B model download (~14GB) may take time" -ForegroundColor Yellow
Write-Host "  - GPU memory usage: ~8GB" -ForegroundColor Yellow
Write-Host ""

# Start application
Write-Host "[4/4] Starting application..." -ForegroundColor Green
Write-Host "  URL: http://localhost:7861" -ForegroundColor Cyan
Write-Host ""
python app.py
