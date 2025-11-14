# RAG Tech Doc Search - Quick Launcher
# Encoding: UTF-8

param(
    [Parameter(Position=0)]
    [ValidateSet("lmstudio", "gpu")]
    [string]$Mode = "lmstudio"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TechScout - Quick Launcher" -ForegroundColor Cyan
Write-Host "東洋電機製造株式会社" -ForegroundColor White
Write-Host "開発センター基盤技術部" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-Not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Then run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "Then run: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Set encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

# Select app
$appFile = ""
if ($Mode -eq "lmstudio") {
    Write-Host "[2/3] Mode: LM Studio Edition" -ForegroundColor Green
    $appFile = "app_lmstudio.py"
    
    # Check LM Studio
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "[OK] LM Studio is running" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] LM Studio not detected" -ForegroundColor Yellow
        Write-Host "  App will run in search-only mode" -ForegroundColor Yellow
    }
} else {
    Write-Host "[2/3] Mode: GPU Edition (requires CUDA)" -ForegroundColor Green
    $appFile = "app.py"
    
    # Check CUDA
    try {
        $cudaCheck = & python -c "import torch; print(torch.cuda.is_available())" 2>$null
        if ($cudaCheck -eq "True") {
            Write-Host "[OK] CUDA is available" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] CUDA not available (CPU mode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARNING] Could not check CUDA status" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[3/3] Starting application..." -ForegroundColor Green
Write-Host ""
Write-Host "  URL:   " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:7861" -ForegroundColor White
Write-Host "  Login: " -NoNewline -ForegroundColor Cyan
Write-Host "admin / password123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run application
python $appFile

