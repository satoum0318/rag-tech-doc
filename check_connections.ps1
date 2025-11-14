# RAG App Connection Monitor
# Check how many users are currently connected

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG App - Connection Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if app is running
$connections = Get-NetTCPConnection -LocalPort 7861 -State Established -ErrorAction SilentlyContinue

if (-not $connections) {
    Write-Host "[INFO] No active connections" -ForegroundColor Yellow
    Write-Host "  The app may not be running or no users are connected" -ForegroundColor Gray
    Write-Host ""
    
    # Check if app is listening
    $listening = Get-NetTCPConnection -LocalPort 7861 -State Listen -ErrorAction SilentlyContinue
    if ($listening) {
        Write-Host "[OK] App is running and waiting for connections" -ForegroundColor Green
        Write-Host "  Access URL: http://192.168.2.101:7861" -ForegroundColor Cyan
    } else {
        Write-Host "[WARNING] App is not running on port 7861" -ForegroundColor Red
    }
} else {
    $count = ($connections | Measure-Object).Count
    Write-Host "[OK] Active Connections: $count" -ForegroundColor Green
    Write-Host ""
    Write-Host "Connected clients:" -ForegroundColor Cyan
    $connections | ForEach-Object {
        Write-Host "  - $($_.RemoteAddress):$($_.RemotePort)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Show system resources
Write-Host "System Resources:" -ForegroundColor Cyan
$cpu = Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average
$memory = Get-WmiObject Win32_OperatingSystem
$memUsedGB = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / 1MB, 2)
$memTotalGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)

Write-Host "  CPU Usage: $cpu%" -ForegroundColor White
Write-Host "  Memory: $memUsedGB GB / $memTotalGB GB" -ForegroundColor White

Write-Host ""
Write-Host "Press Ctrl+C to exit or close this window"
Write-Host "Refreshing every 5 seconds..."
Write-Host ""

# Keep running and refresh
while ($true) {
    Start-Sleep -Seconds 5
    
    $connections = Get-NetTCPConnection -LocalPort 7861 -State Established -ErrorAction SilentlyContinue
    $count = if ($connections) { ($connections | Measure-Object).Count } else { 0 }
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Active connections: $count" -ForegroundColor Gray
}

