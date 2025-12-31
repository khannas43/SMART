# PowerShell Setup Script for Eligibility Scoring & 360° Profiles
# Execute steps 1-4 of the setup process (Windows)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Eligibility Scoring & 360° Profiles Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$baseDir = Split-Path -Parent $PSScriptRoot
$env:PGPASSWORD = 'anjali143'

# Step 1: Create Database Schema
Write-Host ""
Write-Host "Step 1: Creating database schema..." -ForegroundColor Yellow
$dbDir = Join-Path $baseDir "database"
Push-Location $dbDir
wsl bash -c "export PGPASSWORD='anjali143' && psql -h 172.17.16.1 -p 5432 -U sameer -d smart_warehouse -f smart_warehouse.sql"
Pop-Location
Write-Host "✅ Database schema created" -ForegroundColor Green

# Step 2: Generate Synthetic Data (45K records)
Write-Host ""
Write-Host "Step 2: Generating synthetic data (45K records)..." -ForegroundColor Yellow
$dataDir = Join-Path $baseDir "data"
Push-Location $dataDir
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile/data && source ../../../.venv/bin/activate && python generate_synthetic.py"
Pop-Location
Write-Host "✅ Synthetic data generated" -ForegroundColor Green

# Step 3: Train Income Band Model
Write-Host ""
Write-Host "Step 3: Training income band model..." -ForegroundColor Yellow
$srcDir = Join-Path $baseDir "src"
Push-Location $srcDir
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile/src && source ../../../.venv/bin/activate && python income_band_train.py"
Pop-Location
Write-Host "✅ Income band model trained" -ForegroundColor Green

# Step 4: Run Graph Clustering
Write-Host ""
Write-Host "Step 4: Running graph clustering..." -ForegroundColor Yellow
wsl bash -c "cd /mnt/c/Projects/SMART/ai-ml/use-cases/02_eligibility_scoring_360_profile/src && source ../../../.venv/bin/activate && python graph_clustering.py"
Pop-Location
Write-Host "✅ Graph clustering completed" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Steps 1-4 Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - Run anomaly detection: cd src && python anomaly_detection.py"
Write-Host "  - Train eligibility scoring: python eligibility_scoring_train.py"
Write-Host "  - Run notebooks: cd ../notebooks && jupyter lab"

