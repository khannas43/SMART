# PowerShell script to populate Hindi data for testing
# This script helps you quickly add Hindi content to test localization

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Hindi Data Population Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if psql is available
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Host "ERROR: psql is not in your PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run the SQL script manually in pgAdmin:" -ForegroundColor Yellow
    Write-Host "  File: scripts/QUICK_TEST_HINDI.sql" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or add PostgreSQL bin directory to your PATH." -ForegroundColor Yellow
    exit 1
}

# Database connection details
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "smart"
$dbUser = "sameer"
$dbPassword = "anjali143"

Write-Host "Connecting to database: $dbName on $dbHost..." -ForegroundColor Green

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $dbPassword

# Run the SQL script
$sqlFile = Join-Path $PSScriptRoot "QUICK_TEST_HINDI.sql"
if (Test-Path $sqlFile) {
    Write-Host "Running SQL script: $sqlFile" -ForegroundColor Green
    & psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -f $sqlFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Hindi data populated successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Refresh your frontend application" -ForegroundColor White
        Write-Host "2. Switch language to Hindi (हिंदी)" -ForegroundColor White
        Write-Host "3. Check the dashboard and schemes pages" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✗ Error running SQL script. Check the error messages above." -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: SQL file not found: $sqlFile" -ForegroundColor Red
}

# Clear password from environment
Remove-Item Env:\PGPASSWORD

