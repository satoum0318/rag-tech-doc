# Firewall Rule for RAG App - Port 7861
# Run this script as Administrator

Write-Host "Adding firewall rule for RAG App (Port 7861)..." -ForegroundColor Cyan
Write-Host ""

try {
    # Check if rule already exists
    $existingRule = Get-NetFirewallRule -DisplayName "RAG App Port 7861" -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "[INFO] Firewall rule already exists. Removing old rule..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName "RAG App Port 7861"
    }
    
    # Add new firewall rule
    New-NetFirewallRule `
        -DisplayName "RAG App Port 7861" `
        -Description "Allow inbound connections for RAG Technical Document Search System" `
        -Direction Inbound `
        -LocalPort 7861 `
        -Protocol TCP `
        -Action Allow `
        -Profile Any `
        -Enabled True
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[OK] Firewall rule added successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Port 7861 is now open for external access" -ForegroundColor White
    Write-Host "You can now access from other devices:" -ForegroundColor Cyan
    Write-Host "  http://192.168.2.101:7861" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "[ERROR] Failed to add firewall rule" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please make sure you are running PowerShell as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

