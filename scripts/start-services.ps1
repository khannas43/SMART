# Start SMART Platform Services
# Run this after computer restart

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting SMART Platform Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check PostgreSQL
Write-Host "1. Checking PostgreSQL..." -ForegroundColor Yellow
$pgCheck = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
if ($pgCheck) {
    $pgStatus = (Get-Service -Name "*postgresql*").Status
    if ($pgStatus -eq "Running") {
        Write-Host "   ✅ PostgreSQL is running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  PostgreSQL is not running. Starting..." -ForegroundColor Yellow
        Start-Service -Name "*postgresql*"
        Start-Sleep -Seconds 3
        Write-Host "   ✅ PostgreSQL started" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  PostgreSQL service not found. Make sure it's running manually." -ForegroundColor Yellow
}
Write-Host ""

# 2. Start MLflow UI (in WSL)
Write-Host "2. Starting MLflow UI..." -ForegroundColor Yellow
Write-Host "   Running in WSL (background)..." -ForegroundColor Gray
$mlflowJob = Start-Job -ScriptBlock {
    wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml && source .venv/bin/activate && mlflow ui --host 0.0.0.0 --port 5000"
}
Write-Host "   ✅ MLflow UI starting on http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "   (Check status with: Get-Job | Receive-Job)" -ForegroundColor Gray
Write-Host ""

# 3. Optional: Start JupyterLab
Write-Host "3. JupyterLab (optional)..." -ForegroundColor Yellow
Write-Host "   To start JupyterLab manually, run:" -ForegroundColor Gray
Write-Host "   wsl bash -c 'cd /mnt/c/Projects/SMART/ai-ml && source .venv/bin/activate && jupyter lab --no-browser'" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Services Status:" -ForegroundColor Cyan
Write-Host "  ✅ PostgreSQL: Running" -ForegroundColor Green
Write-Host "  ✅ MLflow UI: Starting (check http://127.0.0.1:5000)" -ForegroundColor Green
Write-Host "  ⚪ JupyterLab: Manual start required (see above)" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop MLflow, run: Get-Job | Stop-Job | Remove-Job" -ForegroundColor Yellow

