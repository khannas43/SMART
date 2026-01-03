# PowerShell script to migrate data from smart_warehouse to smart_citizen
# This script executes the Flyway migration V11 which contains the data migration SQL

param(
    [string]$DatabaseHost = "localhost",
    [int]$DatabasePort = 5432,
    [string]$DatabaseName = "smart",
    [string]$DatabaseUser = "sameer",
    [string]$DatabasePassword = "anjali143"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Data Migration: smart_warehouse -> smart_citizen" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for password
$env:PGPASSWORD = $DatabasePassword

# Check if both schemas exist
Write-Host "Checking database schemas..." -ForegroundColor Yellow
$schemaCheck = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d $DatabaseName -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('smart_warehouse', 'smart_citizen');"

if ($schemaCheck -lt 2) {
    Write-Host "ERROR: Both schemas (smart_warehouse and smart_citizen) must exist!" -ForegroundColor Red
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "  1. smart_warehouse schema has data populated" -ForegroundColor Yellow
    Write-Host "  2. smart_citizen schema has all tables created (via Flyway migrations)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Both schemas exist" -ForegroundColor Green
Write-Host ""

# Check if warehouse has data
Write-Host "Checking warehouse data..." -ForegroundColor Yellow
$warehouseCitizens = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_warehouse -t -c "SELECT COUNT(*) FROM citizens;" | ForEach-Object { $_.Trim() }
$warehouseSchemes = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_warehouse -t -c "SELECT COUNT(*) FROM schemes;" | ForEach-Object { $_.Trim() }
$warehouseApplications = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_warehouse -t -c "SELECT COUNT(*) FROM applications;" | ForEach-Object { $_.Trim() }

Write-Host "  Warehouse Citizens: $warehouseCitizens" -ForegroundColor Cyan
Write-Host "  Warehouse Schemes: $warehouseSchemes" -ForegroundColor Cyan
Write-Host "  Warehouse Applications: $warehouseApplications" -ForegroundColor Cyan
Write-Host ""

if ([int]$warehouseCitizens -eq 0) {
    Write-Host "WARNING: No citizens found in warehouse. Migration will have no effect." -ForegroundColor Yellow
}

# Check current citizen data
Write-Host "Checking current smart_citizen data..." -ForegroundColor Yellow
$currentCitizens = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM citizens;" | ForEach-Object { $_.Trim() }
$currentSchemes = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM schemes;" | ForEach-Object { $_.Trim() }
$currentApplications = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM service_applications;" | ForEach-Object { $_.Trim() }

Write-Host "  Current Citizens: $currentCitizens" -ForegroundColor Cyan
Write-Host "  Current Schemes: $currentSchemes" -ForegroundColor Cyan
Write-Host "  Current Applications: $currentApplications" -ForegroundColor Cyan
Write-Host ""

# Confirm migration
$confirm = Read-Host "Do you want to proceed with migration? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Migration cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting migration..." -ForegroundColor Green
Write-Host ""

# Execute migration via Flyway
# Note: This will run the V11 migration script
$migrationPath = "src\main\resources\db\migration\V11__migrate_data_from_warehouse.sql"

if (Test-Path $migrationPath) {
    Write-Host "Executing migration script..." -ForegroundColor Yellow
    
    # Execute SQL file directly (connect to smart_citizen database)
    $sqlContent = Get-Content $migrationPath -Raw
    $sqlContent | psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Migration completed successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Show final counts
        Write-Host "Final data counts:" -ForegroundColor Cyan
        $finalCitizens = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM citizens;" | ForEach-Object { $_.Trim() }
        $finalSchemes = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM schemes;" | ForEach-Object { $_.Trim() }
        $finalApplications = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM service_applications;" | ForEach-Object { $_.Trim() }
        $finalHistory = psql -h $DatabaseHost -p $DatabasePort -U $DatabaseUser -d smart_citizen -t -c "SELECT COUNT(*) FROM application_status_history;" | ForEach-Object { $_.Trim() }
        
        Write-Host "  Citizens: $finalCitizens" -ForegroundColor Green
        Write-Host "  Schemes: $finalSchemes" -ForegroundColor Green
        Write-Host "  Applications: $finalApplications" -ForegroundColor Green
        Write-Host "  Status History: $finalHistory" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Migration failed. Check error messages above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ERROR: Migration script not found at: $migrationPath" -ForegroundColor Red
    Write-Host "Please run this script from the citizen-service directory." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

